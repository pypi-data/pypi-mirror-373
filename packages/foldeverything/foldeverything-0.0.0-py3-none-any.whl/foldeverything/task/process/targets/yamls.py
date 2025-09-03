from pathlib import Path
from typing import List

import yaml

from foldeverything.data.data import (
    PDB,
    ChainInfo,
    Record,
    StructureInfo,
    Target,
)
from foldeverything.data.parse.yaml import parse_yaml
from foldeverything.task.process.process import Resource
from foldeverything.task.process.targets.target import TargetsSource


class YAMLTargets(TargetsSource):
    """The RCSB target data source."""

    def __init__(self, data_dir: str, moldir: str) -> None:
        """Initialize the data source.

        Parameters
        ----------
        data_dir : str
            Path to the directory containing the PDB archive.
        components : str
            Path to the processed CCD components dictionary.

        """
        filters = []
        super().__init__(data_dir, moldir, filters)

    def fetch(self) -> List[PDB]:
        """Get a list of raw data points.

        Returns
        -------
        List[Raw]
            A list of raw data points

        """
        data: List[PDB] = []

        for path in Path(self._data_dir).glob("*.yaml"):
            target_id = path.stem
            target = PDB(id=target_id, path=str(path))
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
        with Path(data.path).open("r") as f:
            yaml_data = yaml.safe_load(f)

        # Parse the yaml file
        structure = parse_yaml(yaml_data, mols=resource, moldir=self._moldir)

        # Map entity to msa id
        entity_to_msa_id = {}
        for entity_id, entity in enumerate(yaml_data["sequences"]):
            if "protein" not in entity:
                raise NotImplementedError

            if "msa" not in entity["protein"] or not entity["protein"]["msa"]:
                raise ValueError(f"No msa found for entity {entity_id}")

            if entity["protein"]["msa"] == "empty":
                entity_to_msa_id[entity_id] = -1
            else:
                entity_to_msa_id[entity_id] = Path(entity["protein"]["msa"]).stem

        # Create chain metadata
        chain_info = []
        for chain in structure.chains:
            info = ChainInfo(
                chain_id=int(chain["asym_id"]),
                chain_name=chain["name"],
                msa_id=entity_to_msa_id[chain["entity_id"]],
                mol_type=int(chain["mol_type"]),
                cluster_id=-1,
                num_residues=int(chain["res_num"]),
            )
            chain_info.append(info)

        num_chains = len(structure.chains)
        structure_info = StructureInfo(
            method="X-RAY DIFFRACTION",
            num_chains=num_chains,
        )

        # Create record
        record = Record(
            id=data.id,
            structure=structure_info,
            chains=chain_info,
            interfaces=[],
        )

        return Target(structure=structure, record=record)
