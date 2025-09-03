from foldeverything.data.data import Record
from foldeverything.data.filter.dynamic.filter import DynamicFilter
import pickle
from typing import List


class FilterID(DynamicFilter):
    """A filter that filters complexes with id in pickled list path."""

    def __init__(self, paths: List[str], reverse: bool = False):
        self.paths = paths
        self.reverse = reverse
        IGNORES = []
        for path in paths:
            with open(path, "rb") as f:
                IGNORE = pickle.load(f)
                IGNORES.extend(IGNORE)
        self.IGNORE = set(IGNORES)

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
        if self.reverse:
            return record.id in self.IGNORE
        else:
            return record.id not in self.IGNORE
