import hashlib
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
from foldeverything.data.parse.mmcif import parse_mmcif
from foldeverything.task.process.process import Resource
from foldeverything.task.process.targets.target import TargetsSource


def get_subfolder(seq: str) -> str:  # noqa: D103
    return hashlib.sha256(seq.encode()).hexdigest()[:2]


class AFDBTargets(TargetsSource):
    """The AFDB target data source."""

    def fetch(self) -> List[PDB]:
        """Get a list of raw data points.

        Returns
        -------
        List[Raw]
            A list of raw data points

        """
        data = []
        for path in Path(self._data_dir).glob("**/*.cif"):
            name = path.name.split("-")[1]
            subfolder = get_subfolder(name)
            full_name = subfolder + "/" + name
            data.append(PDB(id=full_name, path=str(path)))
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
        Targets
            The parsed target.

        """
        parsed = parse_mmcif(data.path, resource, use_assembly=False)
        structure = parsed.data

        structure_info = StructureInfo(
            resolution=0.0,
            deposited="0001-01-01",
            released="0001-01-01",
            revised="0001-01-01",
            num_chains=1,
            num_interfaces=0,
            method="AFDB",
        )
        chain_info = ChainInfo(
            chain_id=0,
            chain_name="A",
            msa_id=data.id,
            template_ids=None,
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
