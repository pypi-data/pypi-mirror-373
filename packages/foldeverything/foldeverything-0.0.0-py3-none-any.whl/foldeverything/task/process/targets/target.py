import json
import traceback
from abc import abstractmethod
from collections import defaultdict
from dataclasses import asdict, replace
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import rdkit
import requests
from Bio import SeqIO
from tqdm import tqdm

from foldeverything.data.data import PDB, Target
from foldeverything.data.filter.static.filter import StaticFilter
from foldeverything.data.mol import load_all_molecules, load_molecules
from foldeverything.task.process.process import Resource, Source
from foldeverything.task.process.sequences.sequences import main


class TargetsSource(Source[PDB]):
    """A target data source."""

    def __init__(
        self,
        data_dir: str,
        moldir: str,
        filters: Optional[List[StaticFilter]] = None,
        molecules: Optional[list[str]] = None,
    ) -> None:
        """Initialize the data source.

        Parameters
        ----------
        data_dir : str
            Directory containing the raw data.
        components : str
            Path to the processed CCD components dictionary.
        filters : List[StaticFilter]
            The filters to apply.

        """
        self._data_dir = Path(data_dir)
        self._moldir = moldir
        self._filters = filters
        self.molecules = molecules

    def resource(self) -> dict:
        """Return a shared resource needed for processing.

        Returns
        -------
        Dict
            The shared resource.

        """
        if self.molecules is None:
            return load_all_molecules(self._moldir)
        else:
            return load_molecules(self._moldir, self.molecules)


    def setup(self, outdir: Path) -> None:
        """Run pre-processing in main thread.

        Parameters
        ----------
        outdir : Paths
            The output directory.

        """
        # Set default pickle properties
        pickle_option = rdkit.Chem.PropertyPickleOptions.AllProps
        rdkit.Chem.SetDefaultPickleProperties(pickle_option)

        # Create output directories
        records_dir = outdir / "records"
        records_dir.mkdir(parents=True, exist_ok=True)

        structure_dir = outdir / "structures"
        structure_dir.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def parse(self, data: PDB, resource: Resource) -> Target:
        """Parse a target.

        Parameters
        ----------
        data : PDB
            The raw input data.
        resource: Resource
            The shared resource.

        Returns
        -------
        Target
            The parsed target.

        """
        raise NotImplementedError

    def subfolder(self, target: Target) -> str:
        """Return a subfolder name for a target.

        Parameters
        ----------
        target : Target
            The target.

        Returns
        -------
        str
            The subfolder name.

        """
        return ""

    def process(self, data: PDB, resource: Resource, outdir: Path) -> None:
        """Process a target.

        Parameters
        ----------
        data : PDB
            The raw input data.
        resource: Resource
            The shared resource.
        outdir : Path
            The output directory.

        """
        # Check if we need to process
        struct_path = outdir / "structures" / f"{data.id}.npz"
        record_path = outdir / "records" / f"{data.id}.json"

        struct_path.parent.mkdir(parents=True, exist_ok=True)
        record_path.parent.mkdir(parents=True, exist_ok=True)

        if struct_path.exists() and record_path.exists():
            return

        try:
            # Parse the target
            target: Target = self.parse(data, resource)
            structure = target.structure

            # Apply the filterss
            mask = structure.mask
            if self._filters is not None:
                for f in self._filters:
                    filter_mask = f.filter(structure)
                    mask = mask & filter_mask
        except Exception:  # noqa: BLE001
            traceback.print_exc()
            print(f"Failed to parse {data.id}")
            return

        # Replace chains and interfaces
        chains = []
        for i, chain in enumerate(target.record.chains):
            chains.append(replace(chain, valid=bool(mask[i])))

        interfaces = []
        for interface in target.record.interfaces:
            chain_1 = bool(mask[interface.chain_1])
            chain_2 = bool(mask[interface.chain_2])
            interfaces.append(replace(interface, valid=(chain_1 and chain_2)))

        # Replace structure and record
        structure = replace(structure, mask=mask)
        record = replace(target.record, chains=chains, interfaces=interfaces)
        target = replace(target, structure=structure, record=record)

        # Dump structure
        np.savez_compressed(struct_path, **asdict(structure))

        # Dump record
        with record_path.open("w") as f:
            json.dump(asdict(record), f)

    def finalize(self, outdir: Path) -> None:
        """Run post-processing in main thread.

        Parameters
        ----------
        outdir : Path
            The output directory.

        """
        # Group records into a manifest
        records_dir = outdir / "records"

        manifest = []
        for path in records_dir.glob("**/*.json"):
            with path.open("r") as f:
                try:
                    d = json.load(f)
                except json.JSONDecodeError:
                    print(f"Failed to decode JSON from {path}")
                    continue
                manifest.append(d)

        with (outdir / "manifest.json").open("w") as f:
            json.dump(manifest, f)


class TargetsSourceMD(TargetsSource):
    """A target data source for MD."""

    def __init__(
        self,
        data_dir: str,
        moldir: str,
        filters: Optional[List[StaticFilter]] = None,
        molecules: Optional[list[str]] = None,
    ) -> None:
        """Initialize the data source.

        Parameters
        ----------
        data_dir : str
            Directory containing the raw data.
        components : str
            Path to the processed CCD components dictionary.
        filters : List[StaticFilter]
            The filters to apply.
        molecules: List of molecules to load from moldir. Loads all if None.

        """
        super().__init__(data_dir, moldir, filters, molecules)

    def parse_fasta_chain_info(self, chain_id: str, seq):
        entity_id = int(chain_id.split("_")[1].split("=")[1])
        entity_name = chain_id.split("_")[2].split("=")[1]
        subchains = chain_id.split("_")[3].split("=")[1]
        value = {
            "entity_id": entity_id,
            "entity_name": entity_name,
            "subchains": subchains,
            "seq": str(seq),
        }
        key = chain_id.split("_")[0].split("=")[1][0:4]
        return key, value

    def parse_fastas(
            self,
            fasta_dir: Path,
            recompute: bool = False,
            keys: Optional[List[str]] = None,
            file_type: Optional[str] = None,
            struct_dir: Optional[Path] = None,
            num_processes: Optional[int] = 1
        ) -> tuple[Dict, Dict, Dict, Dict]:
        """Parse FASTA files and return sequences."""
        if recompute:
            print("Recomputing RCSB sequences...")
            self.get_rcsb_sequences(
                keys=keys,
                fasta_dir=fasta_dir,
                struct_dir=struct_dir,
                file_type=file_type,
                num_processes=num_processes
            )

        # Open fasta files with chain sequence info
        with Path(fasta_dir / "ligands.fasta").open("r") as handle:
            ligand_data_ = list(SeqIO.parse(handle, "fasta"))
            ligand_data = defaultdict(list)
            for x in ligand_data_:
                key, value = self.parse_fasta_chain_info(x.id, x.seq)
                ligand_data[key].append(value)

        with Path(fasta_dir / "proteins.fasta").open("r") as handle:
            protein_data_ = list(SeqIO.parse(handle, "fasta"))
            protein_data = defaultdict(list)
            for x in protein_data_:
                key, value = self.parse_fasta_chain_info(x.id, x.seq)
                protein_data[key].append(value)

        with Path(fasta_dir / "dnas.fasta").open("r") as handle:
            dna_data_ = list(SeqIO.parse(handle, "fasta"))
            dna_data = defaultdict(list)
            for x in dna_data_:
                key, value = self.parse_fasta_chain_info(x.id, x.seq)
                dna_data[key].append(value)

        with Path(fasta_dir / "rnas.fasta").open("r") as handle:
            rna_data_ = list(SeqIO.parse(handle, "fasta"))
            rna_data = defaultdict(list)
            for x in rna_data_:
                key, value = self.parse_fasta_chain_info(x.id, x.seq)
                rna_data[key].append(value)

        return ligand_data, protein_data, dna_data, rna_data

    def get_rcsb_sequences(
        self,
        keys: List[str],
        fasta_dir: Path,
        struct_dir: Path,
        file_type: str,
        num_processes: int = 1,
    ) -> None:
        """Download and extract sequences from RCSB PDB.

        Parameters
        ----------
        keys : List[str]
            List of PDB IDs to download.
        fasta_dir : Path
            Directory to save extracted FASTA files.
        struct_dir : Path
            Directory to save downloaded structure files.
        file_type : str
            File type to download (e.g., '-assembly1').
        num_processes : int, optional
            Number of processes to use for extraction, by default 1.

        """
        if file_type is None:
            raise ValueError("file_type must be specified")

        # Create directories
        struct_dir.mkdir(parents=True, exist_ok=True)
        # assert not fasta_dir.exists(), "FASTA directory already exists, prevent overwriting"

        print("Will save to ", fasta_dir)

        # Download the files
        print("Downloading files...")
        for key in tqdm(keys):
            url = f"https://files.rcsb.org/download/{key.upper()}{file_type}.cif.gz"
            pdb_file = struct_dir / f"{key.upper()}{file_type}.cif.gz"
            if not pdb_file.exists():
                try:
                    response = requests.get(url, timeout=10)
                    with pdb_file.open("wb") as f:
                        f.write(response.content)
                except requests.exceptions.ReadTimeout:
                    print(f"Failed to download {key}")
                    continue

        # Extract the sequences
        print("Running main")
        main(pdb_dir=struct_dir, outdir=fasta_dir, num_processes=num_processes, subfolders=False)
