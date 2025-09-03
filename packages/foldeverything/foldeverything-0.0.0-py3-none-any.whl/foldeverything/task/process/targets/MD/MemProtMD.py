import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd
from tqdm import tqdm

from foldeverything.data import const
from foldeverything.data.data import (
    ChainInfo,
    InterfaceInfo,
    MDData,
    MDInfo,
    Record,
    StructureInfo,
    Target,
)
from foldeverything.data.filter.static.filter import StaticFilter
from foldeverything.data.md_sampling.md_sampler import MDSampler
from foldeverything.data.parse.md import parse_md
from foldeverything.data.parse.MemProtMD import MemProtMD_RawMD
from foldeverything.task.process.process import Resource
from foldeverything.task.process.targets.target import TargetsSourceMD


class MemProtMDTargets(TargetsSourceMD):
    """The MemProtMD target data source."""

    def __init__(
        self,
        data_dir: str,
        fasta_dir: str,
        pdb_metadata: str,
        moldir: str,
        clusters: str,
        chain_map: str,
        template_map: str,
        md_sampler: MDSampler,
        filters: Optional[List[StaticFilter]] = None,
        max_conformers: Optional[int] = 256,
        chain_match_th: Optional[float] = 0.95,
        atom_match_th: Optional[float] = 0.2,
        max_file_size: Optional[int] = None,
        molecules: Optional[list[str]] = None,
        rcsb_struct_path: Optional[str] = None,
    ) -> None:
        """Initialize the data source.

        Parameters
        ----------
        data_dir : str
            Directory containing the dataframe.
        components : str
            Path to the processed rdkit Mol dictionary.

        """
        super().__init__(data_dir, moldir, filters, molecules)
        self.moldir = moldir
        self._data_dir = Path(data_dir)
        self.fasta_dir = Path(fasta_dir)
        pdb_metadata = Path(pdb_metadata)
        self._max_conformers = max_conformers
        self.chain_info = None
        self.chain_match_th = chain_match_th
        self.atom_match_th = atom_match_th
        self.max_file_size = max_file_size

        with Path(clusters).open("r") as f:
            _clusters: Dict[str, str] = json.load(f)
            self._clusters = {k.lower(): v.lower() for k, v in _clusters.items()}

        with Path(chain_map).open("r") as f:
            _chain_map: Dict[str, str] = json.load(f)
            self._chain_map = {k.lower(): v.lower() for k, v in _chain_map.items()}

        with Path(template_map).open("r") as f:
            _template_map: Dict[str, str] = json.load(f)
            self._template_map = {k.lower(): v for k, v in _template_map.items()}

        # Path to RCSB structures
        self.rcsb_struct_path = Path(rcsb_struct_path)

        # Get PDB dates
        self.pdb_metadata = pd.read_pickle(pdb_metadata)  # noqa: S301

        # Raw MD parser for MemProtMD
        self.raw_parser = MemProtMD_RawMD(md_sampler=md_sampler)

    def fetch(self) -> List[MDData]:
        """Get a list of raw data points.

        Returns
        -------
        List[Raw]
            A list of raw data points

        """
        # Load chain data
        ligand_data, protein_data, dna_data, rna_data = self.parse_fastas(
            self.fasta_dir
        )

        # Load json file
        with Path(self._data_dir / "all_data.json").open("r") as f:
            json_data = json.load(f)

        # Loop through domains
        data = []
        chain_info = defaultdict(dict)
        for row_d in tqdm(
            json_data, total=len(json_data), desc="Fetching data to process"
        ):
            entry_id = row_d["_id"]
            pdb_id = row_d["accession"].lower()
            assert row_d["db"] == "PDB", "Entry is not a PDB entry"

            path = self._data_dir
            entry = MDData(
                pdb_id=pdb_id,
                id=entry_id,
                path=path,
            )
            data.append(entry)

            chain_info[pdb_id][const.chain_type_ids["NONPOLYMER"]] = ligand_data.get(
                pdb_id, None
            )
            chain_info[pdb_id][const.chain_type_ids["PROTEIN"]] = protein_data.get(
                pdb_id, None
            )
            chain_info[pdb_id][const.chain_type_ids["DNA"]] = dna_data.get(pdb_id, None)
            chain_info[pdb_id][const.chain_type_ids["RNA"]] = rna_data.get(pdb_id, None)

        self.chain_info = chain_info

        return data

    def parse(self, data: MDData, resource: Resource) -> Target:
        """Process a structure.

        Parameters
        ----------
        data : PubChem
            The raw input data.
        resource: Resource
            The shared resource.

        Returns
        -------
        Target
            The processed data.

        """
        print("data.pdb_id", data.pdb_id)

        # Load the topology and coordinates
        coord_matrix, topology, atom_mask, chain_type_map = self.raw_parser.parse(data.path, data.id)

        # Parse structure
        chain_info = self.chain_info[data.pdb_id.lower()]

        # Parse structure
        structure = parse_md(
            topology=topology,
            coord_matrix=coord_matrix,
            atom_mask=atom_mask,
            mols=resource,
            chain_info=chain_info,
            chain_match_th=0.9,
            atom_match_th=self.atom_match_th,
            local_alg=False,
            rcsb_struct_path=self.rcsb_struct_path / f"{data.pdb_id.lower()}.npz",
            chain_type_map=chain_type_map,
            moldir=self.moldir,
        )

        # Get original PDB date
        if data.pdb_id.upper() in self.pdb_metadata:
            released = self.pdb_metadata[data.pdb_id.upper()]["date"]
        else:
            msg = f"Could not find PDB date for {data.pdb_id}"
            raise AssertionError(msg)

        structure_info = StructureInfo(
            deposited=None,
            revised=None,
            released=released,
            resolution=0.0,
            method="MD",
            num_chains=len(structure.chains),
            num_interfaces=len(structure.interfaces),
        )

        # Create chain metadata
        chain_info = []
        pdb_id = data.pdb_id.lower()

        for chain in structure.chains:
            key = f"{pdb_id}_{chain['entity_id']}"
            chain_info.append(
                ChainInfo(
                    chain_id=int(chain["asym_id"]),
                    chain_name=chain["name"],
                    msa_id=self._chain_map.get(key, -1),
                    template_ids=self._template_map.get(key, None),
                    mol_type=int(chain["mol_type"]),
                    cluster_id=self._clusters[key],
                    num_residues=int(chain["res_num"]),
                )
            )

        # Create MD info.
        md_params_file = self._data_dir / "md_params/manual_md_params_parsed.json"
        with Path(md_params_file).open() as f:
            d = json.load(f)

        md_info = MDInfo(**d)

        # Get interface metadata
        interface_info = []
        for interface in structure.interfaces:
            chain_1 = int(interface["chain_1"])
            chain_2 = int(interface["chain_2"])
            interface_info.append(
                InterfaceInfo(
                    chain_1=chain_1,
                    chain_2=chain_2,
                )
            )

        # Create record
        record = Record(
            id=data.id,
            structure=structure_info,
            chains=chain_info,
            interfaces=interface_info,
            md=md_info,
        )

        # Return target
        return Target(structure=structure, record=record)
