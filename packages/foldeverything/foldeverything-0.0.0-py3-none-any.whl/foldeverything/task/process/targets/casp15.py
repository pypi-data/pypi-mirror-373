import json
from pathlib import Path
from typing import Dict, List

from foldeverything.data.data import (
    PDB,
    ChainInfo,
    InterfaceInfo,
    Record,
    Target,
)
from foldeverything.data.filter.static.filter import StaticFilter
from foldeverything.data.parse.mmcif import parse_mmcif
from foldeverything.task.process.process import Resource
from foldeverything.task.process.targets.target import TargetsSource

PDB_IDS = {
    "7zj4",
    "8c6z",
    "7roa",
    "7uzt",
    "7uyx",
    "8h2n",
    "7yr7",
    "8fza",
    "7ptk",
    "7r1l",
    "7til",
    "8dys",
    "8d5v",
    "7pbp",
    "7ptl",
    "8sx7",
    "8a8c",
    "8em5",
    "8b43",
    "8bbt",
    "8ufn",
    "8ad2",
    "7sq4",
    "8ecx",
    "8tn8",
    "7zcx",
    "8ifx",
    "7uww",
    "8sx8",
    "7qih",
    "7qvb",
    "8uys",
    "7z8y",
    "8btz",
    "8pbv",
    "7qij",
    "8pko",
    "8on4",
    "8smq",
    "8fjp",
    "8okh",
    "7qr3",
    "7ubz",
    "8ok3",
    "7pzt",
    "7pbl",
    "7utd",
    "8ouy",
    "8fef",
    "8ork",
    "7yr6",
    "7qr4",
    "8s95",
    "8swn",
    "7pbr",
    "7ux8",
}


class CASP15Targets(TargetsSource):
    """The RCSB target data source."""

    def __init__(
        self,
        data_dir: str,
        components: str,
        clusters: str,
        chain_map: str,
        filters: List[StaticFilter],
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
        chain_map: str
            Path to the chain mapping file.
        filters : List[StaticFilter]
            The filters to apply.

        """
        super().__init__(data_dir, components, filters)

        with Path(clusters).open("r") as f:
            _clusters: Dict[str, str] = json.load(f)
            self._clusters = {k.lower(): v.lower() for k, v in _clusters.items()}

        with Path(chain_map).open("r") as f:
            _chain_map: Dict[str, str] = json.load(f)
            self._chain_map = {k.lower(): v.lower() for k, v in _chain_map.items()}

    def fetch(self) -> List[PDB]:
        """Get a list of raw data points.

        Returns
        -------
        List[Raw]
            A list of raw data points

        """
        data: List[PDB] = []

        for pdb_id in PDB_IDS:
            # Get path
            file = Path(self._data_dir) / pdb_id[1:3] / f"{pdb_id}.cif.gz"

            # Create the target
            target = PDB(id=pdb_id, path=str(file))
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
        # Get the PDB id
        pdb_id = data.id.lower()

        # Parse structure
        parsed = parse_mmcif(data.path, resource, use_assembly=False)
        structure = parsed.data
        structure_info = parsed.info

        # Create chain metadata
        chain_info = []
        for chain in structure.chains:
            key = f"{pdb_id}_{chain['entity_id']}"
            chain_info.append(
                ChainInfo(
                    chain_id=int(chain["asym_id"]),
                    chain_name=chain["name"],
                    msa_id=self._chain_map.get(key, -1),
                    template_id=self._chain_map.get(key, -1),
                    mol_type=int(chain["mol_type"]),
                    cluster_id=self._clusters.get(key, -1),
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

        # Create record
        record = Record(
            id=data.id,
            structure=structure_info,
            chains=chain_info,
            interfaces=interface_info,
        )

        return Target(structure=structure, record=record)
