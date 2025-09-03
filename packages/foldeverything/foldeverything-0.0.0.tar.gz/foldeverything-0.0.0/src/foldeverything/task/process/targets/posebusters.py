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
    "5sb2",
    "5sd5",
    "5sis",
    "6zk5",
    "7a9h",
    "7afx",
    "7an5",
    "7bka",
    "7dql",
    "7dua",
    "7ecr",
    "7ed2",
    "7elt",
    "7epv",
    "7es1",
    "7f51",
    "7f5d",
    "7f8t",
    "7fb7",
    "7fha",
    "7frx",
    "7ft9",
    "7jhq",
    "7kc5",
    "7l00",
    "7l03",
    "7lcu",
    "7lev",
    "7lou",
    "7m3h",
    "7m6k",
    "7mgt",
    "7mmh",
    "7moi",
    "7msr",
    "7mwn",
    "7mwu",
    "7my1",
    "7n03",
    "7n4n",
    "7n4w",
    "7n6f",
    "7ngw",
    "7nlv",
    "7nr8",
    "7nsw",
    "7nu0",
    "7nxo",
    "7off",
    "7ofk",
    "7oli",
    "7op9",
    "7oso",
    "7oz9",
    "7ozc",
    "7p1f",
    "7p1m",
    "7p4c",
    "7p5t",
    "7pgx",
    "7pih",
    "7pjq",
    "7pk0",
    "7pom",
    "7pri",
    "7prm",
    "7pt3",
    "7q25",
    "7q27",
    "7q2b",
    "7q5i",
    "7qe4",
    "7qf4",
    "7qfm",
    "7qgp",
    "7qhg",
    "7qhl",
    "7qpp",
    "7qta",
    "7r3d",
    "7r59",
    "7r6j",
    "7r7r",
    "7r9n",
    "7rc3",
    "7rh3",
    "7rkw",
    "7ror",
    "7rou",
    "7rsv",
    "7rws",
    "7sdd",
    "7sfo",
    "7siu",
    "7suc",
    "7sza",
    "7t0d",
    "7t1d",
    "7t3e",
    "7tb0",
    "7tbu",
    "7te8",
    "7th4",
    "7thi",
    "7tm6",
    "7tom",
    "7ts6",
    "7tsf",
    "7tuo",
    "7txk",
    "7typ",
    "7u0u",
    "7u3j",
    "7uas",
    "7uaw",
    "7uj4",
    "7uj5",
    "7ujf",
    "7ulc",
    "7umw",
    "7uq3",
    "7ush",
    "7utw",
    "7uxs",
    "7uy4",
    "7uyb",
    "7v14",
    "7v3n",
    "7v3s",
    "7v43",
    "7vb8",
    "7vbu",
    "7vc5",
    "7vkz",
    "7vq9",
    "7vwf",
    "7vyj",
    "7w05",
    "7w06",
    "7wcf",
    "7wdt",
    "7wkl",
    "7wl4",
    "7wpw",
    "7wqq",
    "7wux",
    "7wuy",
    "7wy1",
    "7x5n",
    "7x9k",
    "7xbv",
    "7xfa",
    "7xg5",
    "7xi7",
    "7xjn",
    "7xpo",
    "7xqz",
    "7xrl",
    "7yzu",
    "7z1q",
    "7z2o",
    "7z7f",
    "7zcc",
    "7zdy",
    "7zf0",
    "7zhp",
    "7zl5",
    "7zoc",
    "7ztl",
    "7zu2",
    "7zzw",
    "8a1h",
    "8a2d",
    "8aau",
    "8aem",
    "8ap0",
    "8aql",
    "8auh",
    "8ay3",
    "8b8h",
    "8bom",
    "8bti",
    "8c3n",
    "8c5m",
    "8cnh",
    "8csd",
    "8d19",
    "8d39",
    "8d5d",
    "8dhg",
    "8dko",
    "8dp2",
    "8dsc",
    "8eab",
    "8ex2",
    "8exl",
    "8eye",
    "8f8e",
    "8fav",
    "8flv",
    "8fo5",
    "8g0v",
    "8g6p",
    "8gfd",
    "8hfn",
    "8ho0",
    "8slg",
}


class PoseBustersTargets(TargetsSource):
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
