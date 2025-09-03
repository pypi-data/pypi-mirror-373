import hashlib
import json
from dataclasses import replace
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np

from foldeverything.data import const
from foldeverything.data.data import (
    PDB,
    ChainInfo,
    ConfidenceInfo,
    InterfaceInfo,
    Record,
    Target,
)
from foldeverything.data.filter.static.filter import StaticFilter
from foldeverything.data.mol import load_all_molecules
from foldeverything.data.parse.mmcif import parse_mmcif
from foldeverything.task.process.process import Resource
from foldeverything.task.process.targets.target import TargetsSource


def hash_sequence(seq: str) -> str:
    """Hash the sequence."""
    return hashlib.sha256(seq.encode()).hexdigest()


class BoltzTargets(TargetsSource):
    """The Boltz target data source."""

    def __init__(
        self,
        data_dir: str,
        moldir: str,
        filters: List[StaticFilter],
        ligand_moldir: Optional[str] = None,
    ) -> None:
        """Initialize the data source.

        Parameters
        ----------
        data_dir : str
            Path to the directory containing the PDB archive.
        components : str
            Path to the processed CCD components dictionary.
        clusters: str
            Path to the cluster map.
        filters : List[StaticFilter]
            The filters to apply.

        """
        super().__init__(data_dir, moldir, filters)
        self.ligand_moldir = ligand_moldir

    def resource(self) -> Dict:
        """Return a shared resource needed for processing.

        Returns
        -------
        Dict
            The shared resource.

        """
        mols: dict = load_all_molecules(self._moldir)

        if self.ligand_moldir is not None:
            mols.update(load_all_molecules(self.ligand_moldir))

        return mols

    def fetch(self) -> List[PDB]:
        """Get a list of raw data points.

        Returns
        -------
        List[Raw]
            A list of raw data points

        """
        data: List[PDB] = []
        for folder in Path(self._data_dir).iterdir():
            target = PDB(id=str(folder.stem), path=folder)
            data.append(target)
        return data

    def parse(self, data: PDB, resource: Resource) -> Target:
        """Process a structure.

        Parameters
        ----------
        data : PDB
            The raw input data.
        resource: Resource
            The shared resource.

        Returns
        -------
        Target
            The processed data.

        """
        # Parse structure
        path = data.path / f"{data.id}_model_0.cif"
        parsed = parse_mmcif(path, resource)
        structure = parsed.data
        structure_info = parsed.info
        sequences = parsed.sequences

        # Open plddt file
        plddt_path = data.path / f"plddt_{data.id}_model_0.npz"
        plddt = np.load(plddt_path)["plddt"]

        # Compute atom_to_residue matrix
        index = 0
        atom_to_token = []

        for chain in structure.chains:
            res_st = chain["res_idx"]
            res_en = res_st + chain["res_num"]
            residues = structure.residues[res_st:res_en]
            if chain["mol_type"] == const.chain_type_ids["NONPOLYMER"]:
                for _ in residues:
                    indices = list(range(index, index + chain["atom_num"]))
                    atom_to_token.extend(indices)
                    index += chain["atom_num"]
            else:
                for res in residues:
                    indices = [index] * res["atom_num"]
                    atom_to_token.extend(indices)
                    index += 1

        atom_to_token = np.array(atom_to_token)
        plddt = plddt[atom_to_token]
        structure.atoms["plddt"] = plddt

        # Override bfactor
        structure.atoms["bfactor"] = 0.0

        # Create chain metadata
        chain_info = []
        for chain in structure.chains:
            chain_name = str(chain["name"])
            chain_seq = sequences.get(chain_name, None)

            msa_id = -1
            if (chain_seq is not None) and int(
                chain["mol_type"]
            ) == const.chain_type_ids["PROTEIN"]:
                msa_id = hash_sequence(chain_seq)

            chain_info.append(
                ChainInfo(
                    chain_id=int(chain["asym_id"]),
                    chain_name=chain_name,
                    msa_id=msa_id,
                    template_ids=None,
                    cluster_id=-1,
                    mol_type=int(chain["mol_type"]),
                    num_residues=int(chain["res_num"]),
                )
            )

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

        # Get confidence info
        conf_path = data.path / f"confidence_{data.id}_model_0.json"
        with Path.open(conf_path) as f:
            confidence_info = json.load(f)
            confidence_info = ConfidenceInfo(**confidence_info)

        # Add method
        structure_info = replace(structure_info, method="BOLTZ-1")

        # Create record
        record = Record(
            id=data.id,
            structure=structure_info,
            chains=chain_info,
            interfaces=interface_info,
            confidence=confidence_info,
        )

        return Target(structure=structure, record=record)
