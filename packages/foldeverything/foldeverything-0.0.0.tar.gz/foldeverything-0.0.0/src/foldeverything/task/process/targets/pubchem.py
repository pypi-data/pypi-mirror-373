import pickle
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import replace

import pandas as pd
from tqdm import tqdm

from foldeverything.data import const
from foldeverything.data.data import (
    PDB,
    Atom,
    Bond,
    Chain,
    ChainInfo,
    PubChem,
    Record,
    Residue,
    Structure,
    StructureInfo,
    InterfaceInfo,
    Target,
    AffinityInfo,
)
from foldeverything.data.parse.affinity import parse_smiles_sequences
from foldeverything.task.process.process import Resource
from foldeverything.task.process.targets.target import TargetsSource
from foldeverything.data.filter.static.filter import StaticFilter


class PubChemTargets(TargetsSource):
    """The PubChem target data source."""

    def __init__(
        self,
        data_dir: str,
        components: str,
        resource: str,
        clusters: str,
        chain_map: str,
        filters: Optional[List[StaticFilter]] = None,
    ) -> None:
        """Initialize the data source.

        Parameters
        ----------
        data_dir : str
            Directory containing the dataframe.
        components : str
            Path to the processed rdkit Mol dictionary.

        """
        super().__init__(data_dir, components, filters)
        self._data_dir = Path(data_dir)
        self._components = components
        self._resource = resource

    def fetch(self) -> List[PDB]:
        """Get a list of raw data points.

        Returns
        -------
        List[Raw]
            A list of raw data points

        """
        data = []
        with Path(self._components).open("rb") as f:
            components = pickle.load(f)

        df = pd.read_csv(self._data_dir, index_col=0)
        failed_count = 0
        for i, row in tqdm(
            df.iterrows(), total=df.shape[0], desc="Fetching data to process"
        ):
            try:
                entry = PubChem(
                    id=str(i),
                    aid=int(row["aid"]),
                    sid=int(row["sid"]),
                    cid=int(row["cid"]),
                    outcome=1 if str(row["activity_outcome"]) == "Active" else 0,
                    activity_name=str(row["activity_name"]),
                    activity_qualifier=str(row["activity_qualifier"]),
                    affinity=(
                        10.0
                        if str(row["activity_value"]) == "Inactive"
                        else float(row["activity_value"])
                    ),
                    normalized_protein_accession=str(
                        row["normalized_protein_accession"]
                    ),
                    protein_cluster=row["protein_cluster_03"],
                    protein_cluster_03=row["protein_cluster_03"],
                    protein_cluster_06=row["protein_cluster_06"],
                    protein_cluster_09=row["protein_cluster_09"],
                    modify_date=str(row["deposit_date"]),
                    deposit_date=str(row["deposit_date"]),
                    pair_id=int(row["pair_id"]),
                    assay_prot_id=int(row["assay_prot_id"]),
                    num_duplicate_pair_ids_in_assay=row[
                        "num_duplicate_pair_ids_in_assay"
                    ],
                    num_unique_activity_value_in_assay=row[
                        "num_unique_activity_value_in_assay"
                    ],
                    num_binders_in_assay=row["num_binders_in_assay"],
                    protein_sequences=row["protein_sequence"].split(";"),
                    smiles=[row["isometric_smiles"]],
                    mols=[components[str(int(row["cid"]))]],
                )
                data.append(entry)
            except:
                failed_count += 1
        print(f"Failed to parse {failed_count} entries")
        return data

    def parse(self, data: PubChem, resource: Resource) -> Target:
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
        # Parse ID
        id = data.id

        # Parse structure
        parsed = parse_smiles_sequences(data.protein_sequences, data.mols, resource)

        structure = parsed.data
        structure_info = parsed.info

        # Add dates to structure info
        structure_info = replace(
            structure_info,
            deposited=data.deposit_date,
            released=data.deposit_date,
            revised=data.modify_date,
        )

        # Create chain metadata
        chain_info = []
        for i, chain in enumerate(structure.chains):
            chain_info.append(
                ChainInfo(
                    chain_id=int(chain["asym_id"]),
                    msa_id=(
                        -1
                        if int(chain["mol_type"]) == 3
                        else data.normalized_protein_accession.split(";")[i]
                    ),
                    template_id=-1,  # self._chain_map.get(key),
                    mol_type=int(chain["mol_type"]),
                    cluster_id=data.protein_cluster,
                    num_residues=int(chain["res_num"]),
                    cluster_id_03=data.protein_cluster_03,
                    cluster_id_06=data.protein_cluster_06,
                    cluster_id_09=data.protein_cluster_09,
                )
            )

        # # Get interface metadata
        # interface_info = []
        # for interface in structure.interfaces:
        #     chain_1 = interface["chain_1"]
        #     chain_2 = interface["chain_2"]
        #     interface_info.append(
        #         InterfaceInfo(
        #             chain_id_1=chain_1,
        #             chain_id_2=chain_2,
        #         )
        #     )

        # Create affinity info
        affinity_info = AffinityInfo(
            affinity=data.affinity,
            outcome=data.outcome,
            activity_name=data.activity_name,
            activity_qualifier=data.activity_qualifier,
            sid=data.sid,
            cid=data.cid,
            normalized_protein_accession=data.normalized_protein_accession,
            aid=data.aid,
            pair_id=data.pair_id,
            assay_prot_id=data.assay_prot_id,
            num_duplicate_pair_ids_in_assay=data.num_duplicate_pair_ids_in_assay,
            num_unique_activity_value_in_assay=data.num_unique_activity_value_in_assay,
            num_binders_in_assay=data.num_binders_in_assay,
        )

        # Create record
        record = Record(
            id=id,
            structure=structure_info,
            chains=chain_info,
            interfaces=[],
            affinity=affinity_info,
        )

        # Return target
        return Target(structure=structure, record=record)

    def resource(self) -> Dict:
        """Return a shared resource needed for processing.

        Returns
        -------
        Dict
            The shared resource.

        """
        with Path(self._resource).open("rb") as f:
            resource = pickle.load(f)  # noqa: S301
        return resource
