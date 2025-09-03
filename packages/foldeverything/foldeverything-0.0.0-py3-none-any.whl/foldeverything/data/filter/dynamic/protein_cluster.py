from foldeverything.data.data import Record
from foldeverything.data.filter.dynamic.filter import DynamicFilter
import pickle
from typing import List


class ProteinCluster(DynamicFilter):
    """A filter that filters complexes with id in pickled list path."""

    def __init__(self, paths: List[str], similarity: str = "09"):
        self.paths = paths
        IGNORES = []
        for path in paths:
            with open(path, "r") as f:
                IGNORE = f.read().splitlines()
                IGNORES.extend(IGNORE)
        self.IGNORE_CLUSTERS = set(IGNORES)
        self.similarity = similarity
        assert similarity in [
            "09",
            "06",
            "03",
        ], f"Invalid similarity {similarity}, must be in ['09', '06', '03']"

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
        if self.similarity == "09":
            cluster_ids = [
                chain.cluster_id_09
                for chain in record.chains
                if chain.cluster_id_09 is not None
            ]
        elif self.similarity == "06":
            cluster_ids = [
                chain.cluster_id_06
                for chain in record.chains
                if chain.cluster_id_06 is not None
            ]
        elif self.similarity == "03":
            cluster_ids = [
                chain.cluster_id_03
                for chain in record.chains
                if chain.cluster_id_03 is not None
            ]

        return all(
            [cluster_id not in self.IGNORE_CLUSTERS for cluster_id in cluster_ids]
        )
