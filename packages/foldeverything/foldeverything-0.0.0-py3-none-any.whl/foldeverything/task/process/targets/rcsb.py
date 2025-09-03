import json
from pathlib import Path
from typing import Dict, List, Optional

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


class RCSBTargets(TargetsSource):
    """The RCSB target data source."""

    def __init__(
        self,
        data_dir: str,
        moldir: str,
        clusters: str,
        chain_map: str,
        template_map: str,
        filters: List[StaticFilter],
        max_file_size: Optional[int] = None,
    ) -> None:
        """Initialize the data source.

        Parameters
        ----------
        data_dir : str
            Path to the directory containing the PDB archive.
        clusters: str
            Path to the cluster map.
        chain_map: str
            Path to the chain mapping file.
        filters : List[StaticFilter]
            The filters to apply.

        """
        super().__init__(data_dir, moldir, filters)
        self.max_file_size = max_file_size

        with Path(clusters).open("r") as f:
            _clusters: Dict[str, str] = json.load(f)
            self._clusters = {k.lower(): v.lower() for k, v in _clusters.items()}

        with Path(chain_map).open("r") as f:
            _chain_map: Dict[str, str] = json.load(f)
            self._chain_map = {k.lower(): v.lower() for k, v in _chain_map.items()}

        with Path(template_map).open("r") as f:
            _template_map: Dict[str, str] = json.load(f)
            self._template_map = {k.lower(): v for k, v in _template_map.items()}

    def fetch(self) -> List[PDB]:
        """Get a list of raw data points.

        Returns
        -------
        List[Raw]
            A list of raw data points

        """
        data: List[PDB] = []

        excluded = 0
        for file in self._data_dir.rglob("*.cif*"):
            # If it's assembly data, only use the first assembly
            if "assembly" in str(file) and "-assembly1" not in str(file):
                continue

            # The clustering file is annotated by pdb_entity id
            pdb_id = str(file.stem).split(".")[0].lower()
            if "-assembly1" in pdb_id:
                pdb_id = pdb_id.replace("-assembly1", "")

            # Check file size and skip if too large
            if self.max_file_size is not None and (
                file.stat().st_size > self.max_file_size
            ):
                excluded += 1
                continue

            # Create the target
            target = PDB(id=pdb_id, path=str(file))
            data.append(target)

        print(f"Excluded {excluded} files due to size.")
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
        parsed = parse_mmcif(
            data.path,
            mols=resource,
            moldir=self._moldir,
            use_assembly=True,
        )
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
                    template_ids=self._template_map.get(key, None),
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
