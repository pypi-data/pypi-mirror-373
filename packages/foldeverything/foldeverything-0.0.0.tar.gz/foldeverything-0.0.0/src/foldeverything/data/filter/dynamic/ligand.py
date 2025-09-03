from foldeverything.data.data import Record
from foldeverything.data.filter.dynamic.filter import DynamicFilter
import pickle
from typing import List


class Ligand(DynamicFilter):
    """A filter that filters complexes with id in pickled list path."""

    def __init__(self, paths: List[str]):
        self.paths = paths
        IGNORES = []
        for path in paths:
            with open(path, "r") as f:
                IGNORE = f.read().splitlines()
                IGNORES.extend(IGNORE)
        self.IGNORE_LIGANDS = set(IGNORES)

    def filter(self, record: Record) -> bool:
        """Filter complexes with error ligands.

        Parameters
        ----------
        record : Record
            The record to filter.

        Returns
        -------
        bool
            Whether the record should be keps.

        """
        ligand_ids = [chain.ligand_id for chain in record.chains]

        return all([ligand_id not in self.IGNORE_LIGANDS for ligand_id in ligand_ids])
