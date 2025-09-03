import json
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd
from tqdm import tqdm

from foldeverything.data import const
from foldeverything.data.data import (
    ChainInfo,
    InterfaceInfo,
    MDInfo,
    Record,
    StructureInfo,
    Target,
    UniProtData,
)
from foldeverything.data.filter.static.filter import StaticFilter
from foldeverything.data.md_sampling.md_sampler import MDSampler
from foldeverything.data.parse.IDRome import IDRome_RawMD
from foldeverything.data.parse.md import parse_md
from foldeverything.task.process.process import Resource
from foldeverything.task.process.targets.target import TargetsSourceMD


class IDRomeTargets(TargetsSourceMD):
    """The IDRome target data source."""

    def __init__(
        self,
        data_dir: str,
        pdb_metadata: str,
        moldir: str,
        topology_dir: str,
        clusters: str,
        cg2all_working_dir: str,
        md_sampler: MDSampler,
        filters: Optional[List[StaticFilter]] = None,
        molecules: Optional[list[str]] = None,
        timeout: Optional[int] = 10,
        patience: Optional[int] = 4,
        max_length: Optional[int] = 100,
        pdb_fixer_threads: Optional[int] = 1,
    ) -> None:
        """Initialize the data source.

        Parameters
        ----------
        data_dir : str
            Directory containing the dataframe.
        moldir : str
            Path to the processed rdkit Mol files.

        """
        super().__init__(data_dir, moldir, filters, molecules)
        self.moldir = moldir
        self._data_dir = Path(data_dir)
        self.topology_dir = Path(topology_dir)
        pdb_metadata = Path(pdb_metadata)
        self.max_length = max_length

        self.raw_parser = IDRome_RawMD(
            md_sampler=md_sampler,
            cg2all_working_dir=cg2all_working_dir,
            timeout=timeout,
            patience=patience,
            pdb_fixer_threads=pdb_fixer_threads
        )

        # Load csv metadata
        self.metadata_df = pd.read_csv(self._data_dir / "IDRome_metadata.csv")

        # Get PDB dates
        self.pdb_metadata = pd.read_pickle(pdb_metadata)  # noqa: S301

        with Path(clusters).open("r") as f:
            _clusters: Dict[str, str] = json.load(f)
            self._clusters = {k.upper(): v.upper() for k, v in _clusters.items()}

        self.polymer_codes = [
            const.prot_token_to_letter[x] for x in const.canonical_tokens
        ]

    def fetch(self) -> List[UniProtData]:
        """Get a list of raw data points.

        Returns
        -------
        List[Raw]
            A list of raw data points

        """
        # Loop through the dataframe and extract the PDB and trajectory data
        data = []
        for _, row in tqdm(
            self.metadata_df.iterrows(),
            total=len(self.metadata_df),
            desc="Fetching data to process",
        ):
            IDRome_id = row["seq_name"]
            uniprot_id = row["uniprotID"]
            start = row["subseq_start"]
            end = row["subseq_end"]

            if end - start > self.max_length:
                continue

            refs = row["pdb_refs"]
            pdb_ids = [] if pd.isna(refs) else refs.split(",")
            subfolders = f"{uniprot_id[0:2]}/{uniprot_id[2:4]}/{uniprot_id[4:6]}/{uniprot_id[6:]}/{start}_{end}"
            path = self.topology_dir / subfolders

            full_seq = row["full_sequence"]
            msg = f"Non-polymer codes found in sequence for {IDRome_id}"
            assert all(x in self.polymer_codes for x in full_seq), msg

            entry = UniProtData(
                pdb_ids=pdb_ids,
                id=IDRome_id,
                uniprot_id=uniprot_id,
                path=path,
                ref_seq=full_seq,
            )
            data.append(entry)

        print(f"Number of structures to process: {len(data)}")

        return data

    def parse(self, data: UniProtData, resource: Resource) -> Target:
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
        # print("data.id", data.id)

        # Load the topology, coordinates and atoms mask
        coord_matrix, topology, atom_mask = self.raw_parser.parse(
            data.path, uid_name=data.id
        )

        # Create fake chain info, pass uniprot reference sequence for alignment
        chain_info = {
            const.chain_type_ids["PROTEIN"]: [
                {
                    "entity_id": 0,
                    "entity_name": "0",
                    "subchains": "A",
                    "seq": data.ref_seq,
                }
            ]
        }

        # Parse structure
        structure = parse_md(
            topology=topology,
            coord_matrix=coord_matrix,
            atom_mask=atom_mask,
            mols=resource,
            chain_info=chain_info,
            chain_type_map=None,
            moldir=self.moldir,
            chain_match_th=1.0,  # we know IDRome seqs in MD are fragments of the full sequence in uniprot
            local_alg=True,
        )

        # Get the date of the earliest PDB release
        released = None  # TODO could map to closest PDB entry ?
        if len(data.pdb_ids) > 0:
            for pdb_id in data.pdb_ids:
                if pdb_id.upper() in self.pdb_metadata:
                    released_ = pd.to_datetime(
                        self.pdb_metadata[pdb_id.upper()]["date"]
                    )
                    released = (
                        min(released, released_) if released is not None else released_
                    )

        structure_info = StructureInfo(
            deposited=None,
            revised=None,
            released=str(released) if released is not None else None,
            resolution=0.0,
            method="MD",
            num_chains=len(structure.chains),
            num_interfaces=len(structure.interfaces),
        )

        # Create chain metadata
        chain_info = []
        uniprot_id = data.uniprot_id

        for chain in structure.chains:
            key = f"{uniprot_id.upper()}"
            chain_info.append(
                ChainInfo(
                    chain_id=int(chain["asym_id"]),
                    chain_name=chain["name"],
                    msa_id=uniprot_id,
                    template_ids=None,
                    mol_type=int(chain["mol_type"]),
                    cluster_id=self._clusters[key],
                    num_residues=int(chain["res_num"]),
                )
            )

        # Create MD info. For IDRome they all have the same parameters
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
