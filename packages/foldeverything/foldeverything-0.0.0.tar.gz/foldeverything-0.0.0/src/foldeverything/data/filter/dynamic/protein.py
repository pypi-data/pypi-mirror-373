from foldeverything.data.data import Record
from foldeverything.data.filter.dynamic.filter import DynamicFilter
import pickle
from typing import List


class Protein(DynamicFilter):
    """A filter that filters complexes with id in pickled list path."""

    def __init__(self, paths: List[str], reverse: bool = False):
        self.paths = paths
        IGNORES = []
        for path in paths:
            with open(path, "r") as f:
                IGNORE = f.read().splitlines()
                IGNORES.extend(IGNORE)
        self.IGNORE_PROTEINS = set(IGNORES)
        self.reverse = reverse

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
        protein_id = record.protein_id
        if self.reverse:
            return protein_id in self.IGNORE_PROTEINS
        else:
            return protein_id not in self.IGNORE_PROTEINS
