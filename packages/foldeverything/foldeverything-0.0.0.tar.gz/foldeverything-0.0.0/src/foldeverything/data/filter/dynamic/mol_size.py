import pickle

from foldeverything.data.data import Record
from foldeverything.data.filter.dynamic.filter import DynamicFilter


class SizeFilter(DynamicFilter):
    """A filter that filters structures based on their size."""

    def __init__(self, max_num_atoms: int = 100, cid_to_num_atoms: str = "") -> None:
        """Initialize the filter.

        Parameters
        ----------
        min_chains : int
            The minimum number of chains allowed.
        max_chains : int
            The maximum number of chains allowed.

        """
        self.max_num_atoms = max_num_atoms
        with open(cid_to_num_atoms, "rb") as f:
            self.cid_to_num_atoms = pickle.load(f)

    def filter(self, record: Record) -> bool:
        """Filter structures based on their resolution.

        Parameters
        ----------
        record : Record
            The record to filter.

        Returns
        -------
        bool
            Whether the record should be filtered.

        """
        cid = record.affinity.cid
        if cid in self.cid_to_num_atoms:
            return self.cid_to_num_atoms[cid] <= self.max_num_atoms
        else:
            return False
