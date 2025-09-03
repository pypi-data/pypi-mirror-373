import os
from pathlib import Path
from typing import List

from foldeverything.data import const
from foldeverything.data.data import (
    PDB,
    ChainInfo,
    Record,
    StructureInfo,
    Target,
)
from foldeverything.data.parse.openfold import parse_openfold
from foldeverything.task.process.process import Resource
from foldeverything.task.process.targets.target import TargetsSource


class OpenFoldTargets(TargetsSource):
    """The OpenFold target data source."""

    def fetch(self) -> List[PDB]:
        """Get a list of raw data points.

        Returns
        -------
        List[Raw]
            A list of raw data points

        """
        data = []
        for name in os.listdir(self._data_dir):
            if not Path.is_dir(self._data_dir / name):
                continue

            path = self._data_dir / name
            pdb = path / "pdb" / f"{name}.pdb"
            msa = path / "a3m" / "uniclust30.a3m"
            if (
                pdb.exists()
                and msa.exists()
                and pdb.stat().st_size > 0
                and msa.stat().st_size > 0
            ):
                data.append(PDB(id=name, path=str(path)))

        return data

    def parse(self, data: PDB, resource: Resource) -> Target:
        """Process a target.

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
        structure = parse_openfold(data, resource)
        structure_info = StructureInfo(
            resolution=0.0,
            deposited="0001-01-01",
            released="0001-01-01",
            revised="0001-01-01",
            num_chains=1,
            num_interfaces=0,
        )
        chain_info = ChainInfo(
            chain_id=0,
            chain_name="A",
            msa_id=data.id,
            template_id=data.id,
            mol_type=const.chain_type_ids["PROTEIN"],
            cluster_id=0,
            num_residues=len(structure.residues),
        )
        record = Record(
            id=data.id,
            structure=structure_info,
            chains=[chain_info],
            interfaces=[],
        )

        return Target(structure=structure, record=record)
