from typing import List

from foldeverything.data.data import Record
from foldeverything.data.filter.dynamic.filter import DynamicFilter


class MDFilter(DynamicFilter):
    """Filter a data record based on a MD attributes of data."""

    def __init__(self, temperature_max: float, md_null_pass: bool = True) -> None:
        """Initialize the filter.

        Parameters
        ----------
        subset : str
            The subset of data to consider, one per line.

        """
        self.temperature_max = temperature_max
        self.md_null_pass = md_null_pass

    def filter(self, record: Record) -> bool:
        """Filter a data record.

        Parameters
        ----------
        record : Record
            The object to consider filtering in / out.

        Returns
        -------
        bool
            True if the data passes the filter, False otherwise.

        """
        if record.md is None:
            return self.md_null_pass

        T = record.md.temperature
        if T is None:
            return self.md_null_pass

        return T <= self.temperature_max

