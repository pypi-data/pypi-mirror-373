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
from foldeverything.data.parse.atlas import ATLAS_RawMD
from foldeverything.data.parse.md import parse_md
from foldeverything.task.process.process import Resource
from foldeverything.task.process.targets.target import TargetsSourceMD


class ATLASTargets(TargetsSourceMD):
    """The ATLAS target data source."""

    def __init__(
        self,
        data_dir: str,
        moldir: str,
        md_sampler: MDSampler,
        clusters: str,
        chain_map: str,
        fasta_dir: str,
        pdb_metadata: str,
        template_map: str,
        rcsb_struct_path: str,
        filters: Optional[List[StaticFilter]] = None,
        molecules: Optional[list[str]] = None,
        chain_match_th: Optional[float] = 0.95,
        atom_match_th: Optional[float] = 0.2,
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
        self._data_dir = Path(data_dir)
        self.fasta_dir = Path(fasta_dir)
        pdb_metadata = Path(pdb_metadata)
        self.moldir = moldir

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
        self.pdb_metadata = pd.read_pickle(pdb_metadata)

        # Path to RCSB structures
        self.rcsb_struct_path = Path(rcsb_struct_path)

        self.raw_parser = ATLAS_RawMD(md_sampler=md_sampler)
        self.chain_info = None
        self.chain_match_th = chain_match_th
        self.atom_match_th = atom_match_th

    def fetch(self) -> List[MDData]:
        """Get a list of raw data points.

        Returns
        -------
        List[MDData]
            A list of raw MD data points

        """
        # Load chain data
        ligand_data, protein_data, dna_data, rna_data = self.parse_fastas(
            self.fasta_dir
        )

        # Open TSV file containing metadata about all the MD runs in the ATLAS dataset
        tsv_file = self._data_dir / "2022_06_13_ATLAS_info.tsv"
        df_metadata = pd.read_csv(tsv_file, sep="\t")

        # Loop through the dataframe and extract the PDB and trajectory data
        data = []
        chain_info = defaultdict(dict)
        for _, row in tqdm(
            df_metadata.iterrows(),
            total=df_metadata.shape[0],
            desc="Fetching data to process",
        ):
            name = row["PDB"]
            path = self._data_dir / f"trajectories/{name}/"

            #if name != "1vk1_A":
            #    continue

            pdb_id = name.split("_")[0]

            entry = MDData(
                pdb_id=pdb_id,
                id=name,
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
        # Load the topology and coordinates
        coord_matrix, topology, atom_mask = self.raw_parser.parse(data.path, data.id)

        # Parse structure
        chain_info = self.chain_info[data.pdb_id]
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
        assert len(structure.chains) == 1, "ATLAS dataset should only have one chain"
        chain = structure.chains[0]
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
