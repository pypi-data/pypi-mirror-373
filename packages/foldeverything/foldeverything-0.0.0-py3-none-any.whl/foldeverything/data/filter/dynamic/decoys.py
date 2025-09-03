from foldeverything.data.data import Record
from foldeverything.data.filter.dynamic.filter import DynamicFilter
import pickle
from typing import List


class FilterID(DynamicFilter):
    """A filter that filters complexes with id in pickled list path."""

    def __init__(self, path: str, num_decoys: int = 3):
        self.path = path
        self.IGNORE = []

        with open(path, "rb") as f:
            dict_nums = pickle.load(f)

        for key, value in dict_nums.items():
            if value < num_decoys:
                self.IGNORE.append(key)

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
        return record.id not in self.IGNORE
