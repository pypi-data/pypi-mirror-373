import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional

import h5py
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
from foldeverything.data.parse.misato import MISATO_RawMD
from foldeverything.task.process.process import Resource
from foldeverything.task.process.targets.target import TargetsSourceMD


class MISATOTargets(TargetsSourceMD):
    """The MISATO target data source."""

    def __init__(
        self,
        data_dir: str,
        fasta_dir: str,
        pdb_metadata: str,
        template_map: str,
        moldir: str,
        clusters: str,
        chain_map: str,
        temp_dir: str,
        map_dir: str,
        ligand_map_file: str,
        mol2_dir: str,
        md_sampler: MDSampler,
        rcsb_struct_path: str,
        filters: Optional[List[StaticFilter]] = None,
        molecules: Optional[list[str]] = None,
        chain_match_th: Optional[float] = 0.95,
        atom_match_th: Optional[float] = 0.2,
        recompute_rcsb: Optional[bool] = False,
        struct_dir: Optional[str] = None,
        rcsb_file_type: Optional[str] = "-assembly1",
        num_processes: Optional[int] = 1
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
        self.mol2_dir = Path(mol2_dir)
        map_dir = Path(map_dir)
        pdb_metadata = Path(pdb_metadata)
        self.struct_dir = Path(struct_dir)
        self.num_processes = num_processes
        self.recompute_rcsb = recompute_rcsb
        self.rcsb_file_type = rcsb_file_type
        self.temp_dir = temp_dir
        self.chain_info = None
        self.chain_match_th = chain_match_th
        self.atom_match_th = atom_match_th

        # Get ligand information contained for each PDB_id
        with open(ligand_map_file) as f:
            lines = f.readlines()[6:]  # skip header lines

        ligand_map = {}
        for line in lines:
            match = re.match(r"(\w{4}).*pdf\s\((.*)\)", line)
            if match is not None:
                pdb_id, ligands = match.groups()
                is_mer = False

                if "mer" in ligands:
                    ligand = None
                    is_mer = True
                elif "&" in ligands:
                    # If multiple ligands could be found, it is not clear which one to
                    # use, so we skip it
                    continue
                else:
                    ligands = ligands.split("-")
                    if len(ligands) > 1:
                        # Multi-residue ligands such as glycans are not considered
                        continue
                    ligand = ligands[0]
                ligand_map[pdb_id] = (ligand, is_mer)

        with Path(clusters).open("r") as f:
            _clusters: Dict[str, str] = json.load(f)
            self._clusters = {k.lower(): v.lower() for k, v in _clusters.items()}

        with Path(chain_map).open("r") as f:
            _chain_map: Dict[str, str] = json.load(f)
            self._chain_map = {k.lower(): v.lower() for k, v in _chain_map.items()}

        with Path(template_map).open("r") as f:
            _template_map: Dict[str, str] = json.load(f)
            self._template_map = {k.lower(): v for k, v in _template_map.items()}

        # Get PDB dates
        self.pdb_metadata = pd.read_pickle(pdb_metadata)  # noqa: S301

        # Path to RCSB structures
        self.rcsb_struct_path = Path(rcsb_struct_path)

        self.raw_parser = MISATO_RawMD(
            md_sampler=md_sampler,
            map_dir=map_dir,
            path_temp=temp_dir,
            path_md_hdf5=self._data_dir / "MD.hdf5",
            ligand_map=ligand_map,
            mol2_dir=self.mol2_dir,
        )

    def fetch(self) -> List[MDData]:
        """Get a list of raw data points.

        Returns
        -------
        List[Raw]
            A list of raw data points

        """
        # Open hdf5 file with MISATO dataset and get pdb_id keys
        hd5f_file = self._data_dir / "MD.hdf5"
        keys = []
        with h5py.File(hd5f_file, "r") as f:
            keys = list(f.keys())

        # Load chain data from RCSB
        ligand_data, protein_data, dna_data, rna_data = self.parse_fastas(
            self.fasta_dir,
            recompute=self.recompute_rcsb,
            keys=keys,
            file_type=self.rcsb_file_type,
            struct_dir=self.struct_dir,
            num_processes=self.num_processes,
        )

        # Loop through the dataframe and extract the PDB and trajectory data
        data = []
        chain_info = defaultdict(dict)
        for pdb_id in tqdm(keys, total=len(keys), desc="Fetching data to process"):
            # Skip entry if no ligand information is available
            if pdb_id.lower() not in self.raw_parser.ligand_map:
                continue

            # ids = ["3LVW", "5NW7", "3O9L", "1EIX", "3TD4", "1Z9H", "5WCM", "2AM4", "3L6H", "4AU7", "4ACI", "4YKK", "4IVK", "2I5F", "6P9E", "1XFF", "4BJ8", "2PMN", "3NOK", "1UJ5", "5VAR", "5MRA", "1NOX", "3PGL", "5A7Y", "3V1R", "5MEK", "5HBN", "4Y0A", "6HAI", "1WM1", "6GHV", "5KRE", "4NNR", "4QNU", "1U1W", "8A3H"]
            # ids = [i.lower() for i in ids]
            #if pdb_id.lower() not in ids:
            #     continue

            # TODO
            #if sum([ord(char) for char in pdb_id.lower()]) % 4 != 1:
            #    continue

            entry = MDData(
                pdb_id=pdb_id,
                id=pdb_id,
                path=None,
            )
            data.append(entry)

            pdb_id = pdb_id.lower()
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
        coord_matrix, topology, atom_mask = self.raw_parser.parse(data.pdb_id)

        # Parse structure
        chain_info = self.chain_info[data.pdb_id.lower()]

        structure = parse_md(
            topology=topology,
            coord_matrix=coord_matrix,
            atom_mask=atom_mask,
            mols=resource,
            chain_info=chain_info,
            chain_type_map=None,
            moldir=self.moldir,
            chain_match_th=self.chain_match_th,
            atom_match_th=self.atom_match_th,
            rcsb_struct_path=self.rcsb_struct_path / f"{data.pdb_id.lower()}.npz",
            local_alg=False,
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

        # Create MD info. For ATLAS they all have the same parameters
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
