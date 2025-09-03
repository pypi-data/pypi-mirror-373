from typing import List

from foldeverything.data.data import Record
from foldeverything.data.filter.dynamic.filter import DynamicFilter


class MethodFilter(DynamicFilter):
    """Filter a data record based on a method source of data."""

    def __init__(
        self,
        methods: List[str] = None,
        methods_to_ignore: List[str] = None
    ) -> None:
        """Initialize the filter.

        Parameters
        ----------
        subset : str
            The subset of data to consider, one per line.

        """
        if methods is None and methods_to_ignore is None:
            raise ValueError("One of methods or methods_to_ignore should not be None")

        if methods is not None and methods_to_ignore is not None:
            raise ValueError("One of methods or methods_to_ignore should be None")

        self.methods = [x.upper() for x in methods] if methods is not None else None
        self.methods_to_ignore = [x.upper() for x in methods_to_ignore] if methods_to_ignore is not None else None

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
        if self.methods is not None:
            return record.structure.method.upper() in self.methods

        if self.methods_to_ignore is not None:
            return record.structure.method.upper() not in self.methods_to_ignore
