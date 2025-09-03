from typing import List, Optional, Union

from foldeverything.data.data import Record
from foldeverything.data.filter.dynamic.filter import DynamicFilter


class IDFilter(DynamicFilter):

    def __init__(self, ids, reverse: bool = False):
        if isinstance(ids, str):
            ids = [ids]

        self.ids = ids
        self.reverse = reverse

    def filter(self, record: Record) -> bool:
        if self.reverse:
            return record.id not in self.ids
        else:
            return record.id in self.ids
