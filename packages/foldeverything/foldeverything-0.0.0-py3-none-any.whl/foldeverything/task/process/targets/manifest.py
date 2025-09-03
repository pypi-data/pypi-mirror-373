import pickle
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import replace, asdict
import json
import traceback
import os

import numpy as np
import pandas as pd
from tqdm import tqdm
import rdkit

from foldeverything.data import const
from foldeverything.data.data import (
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
        filters: Optional[List[StaticFilter]] = None,
        ligand_dir: Optional[str] = None,
        protein_dir: Optional[str] = None,
        pocket_filter: bool = False,
        use_assay_prot_id: bool = False,
    ) -> None:
        """Initialize the data source.

        Parameters
        ----------
        data_dir : str
            Directory containing the dataframe.

        """
        super().__init__(data_dir, filters)
        self._data_dir = Path(data_dir)
        self.use_assay_prot_id = use_assay_prot_id
        if ligand_dir:
            self.filter_ligands = True
            self.ligand_dir = [
                ".".join(l.split(".")[:-1])
                for l in os.listdir("/".join([ligand_dir, "ligands"]))
            ]
        else:
            self.filter_ligands = False
        if protein_dir:
            self.filter_proteins = True
            if pocket_filter:
                self.protein_dir = [
                    ".".join(p.split(".")[:-1])
                    for p in os.listdir("/".join([protein_dir, "proteins_pockets"]))
                ]
            else:
                self.protein_dir = [
                    ".".join(p.split(".")[:-1])
                    for p in os.listdir("/".join([protein_dir, "proteins"]))
                ]
        else:
            self.filter_proteins = False
            self.protein_dir = None

    def setup(self, outdir: Path) -> None:
        """Run pre-processing in main thread.

        Parameters
        ----------
        outdir : Path
            The output directory.

        """
        # Create output directories
        records_dir = outdir / "records"
        records_dir.mkdir(parents=True, exist_ok=True)

    def fetch(self) -> List[PubChem]:
        """Get a list of raw data points.

        Returns
        -------
        List[Raw]
            A list of raw data points

        """
        data = []

        df = pd.read_csv(self._data_dir, index_col=0)
        failed_count = 0
        for i, row in tqdm(
            df.iterrows(), total=df.shape[0], desc="Fetching data to process"
        ):
            try:
                entry = PubChem(
                    id=str(i),
                    aid=(
                        int(row["aid"])
                        if not self.use_assay_prot_id
                        else int(row["assay_prot_id"])
                    ),
                    sid=int(row["cid"]),
                    cid=int(row["cid"]),
                    outcome=1 if str(row["activity_outcome"]) == "Active" else 0,
                    activity_name=str(row["activity_name"]),
                    activity_qualifier=(
                        row["activity_sign"] if "activity_sign" in row else "="
                    ),
                    affinity=(
                        10.0
                        if str(row["activity_value"]) == "Inactive"
                        else float(row["activity_value"])
                    ),
                    normalized_protein_accession=str(
                        row["normalized_protein_accession"]
                    ),
                    protein_cluster=str(row["protein_cluster"]),
                    protein_cluster_03=str(row["protein_cluster_03"]),
                    protein_cluster_06=str(row["protein_cluster_06"]),
                    protein_cluster_09=str(row["protein_cluster_09"]),
                    modify_date=str(row["deposit_date"]),
                    deposit_date=str(row["deposit_date"]),
                    pair_id=int(row["pair_id"]),
                    assay_prot_id=int(row["assay_prot_id"]),
                    protein_sequences=row["protein_sequence"].split(";"),
                    smiles=[row["isometric_smiles"]],
                )
                data.append(entry)
            except Exception as e:  # noqa: BLE001
                failed_count += 1
        print(f"Failed to parse {failed_count} entries")
        return data

    def parse(self, data: PubChem) -> Target:
        """Process a structure.

        Parameters
        ----------
        data : PubChem
            The raw input data.

        Returns
        -------
        Target
            The processed data.

        """
        if self.filter_ligands and str(data.cid) not in self.ligand_dir:
            print(f"Ligand {data.cid} not in ligand directory")
            raise ValueError(f"Ligand {data.cid} not in ligand directory")

        if (
            self.filter_proteins
            and str(data.normalized_protein_accession) not in self.protein_dir
        ):
            print(
                f"Protein {data.normalized_protein_accession} not in protein directory"
            )
            raise ValueError(
                f"Protein {data.normalized_protein_accession} not in protein directory"
            )

        # Parse ID
        id = data.id

        structure_info = StructureInfo(
            deposited=data.deposit_date,
            revised=data.modify_date,
            released=data.deposit_date,
            num_chains=len(data.smiles) + len(data.protein_sequences),
            num_interfaces=0,
        )

        # Create chain metadata
        chain_info = []
        i = 0
        for _ in data.protein_sequences:
            msa_id = data.normalized_protein_accession.split(";")[i]
            mol_type = 0
            res_num = len(data.protein_sequences[i])
            chain_info.append(
                ChainInfo(
                    chain_id=i,
                    msa_id=msa_id,
                    mol_type=mol_type,
                    cluster_id=data.protein_cluster.split(";")[i],
                    num_residues=res_num,
                    cluster_id_03=data.protein_cluster_03.split(";")[i],
                    cluster_id_06=data.protein_cluster_06.split(";")[i],
                    cluster_id_09=data.protein_cluster_09.split(";")[i],
                )
            )
            i += 1
        for _ in data.smiles:
            msa_id = -1
            mol_type = 3
            res_num = 1
            chain_info.append(
                ChainInfo(
                    chain_id=i,
                    msa_id=msa_id,
                    mol_type=mol_type,
                    cluster_id=data.protein_cluster,
                    num_residues=res_num,
                    cluster_id_03=data.protein_cluster_03,
                    cluster_id_06=data.protein_cluster_06,
                    cluster_id_09=data.protein_cluster_09,
                )
            )
            i += 1

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
        )

        # Create record
        record = Record(
            id=id,
            structure=structure_info,
            chains=chain_info,
            interfaces=[],
            affinity=affinity_info,
            protein_id=data.normalized_protein_accession,
            ligand_id=data.cid,
        )

        # Return target
        return record

    def resource(self) -> Dict:
        """Return a shared resource needed for processing.

        Returns
        -------
        Dict
            The shared resource.

        """
        return None

    def process(self, data: PubChem, resource: Resource, outdir: Path) -> None:
        """Process a target.

        Parameters
        ----------
        data : PubChem
            The raw input data.
        resource: Resource
            The shared resource.
        outdir : Path
            The output directory.

        """
        # Check if we need to process
        record_path = outdir / "records" / f"{data.id}.json"

        if record_path.exists():
            return

        try:
            # Parse the target
            record = self.parse(data)
        except Exception as e:  # noqa: BLE001
            # traceback.print_exc()
            print(f"Failed to parse {data.id}")
            return

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

        failed_count = 0
        records = []
        for record in records_dir.iterdir():
            path = records_dir / record
            try:
                with path.open("r") as f:
                    records.append(json.load(f))
            except Exception as e:
                failed_count += 1
                print(f"Failed to parse {record}")
        print(f"Failed to parse {failed_count} entries)")

        # Save manifest
        outpath = outdir / "manifest.json"
        with outpath.open("w") as f:
            json.dump(records, f)
