from collections import Counter
from typing import Dict, Iterator, List
from collections import defaultdict
import numpy as np
from numpy.random import RandomState
from random import sample as sample_fn

from foldeverything.data.data import Record
from foldeverything.data.sample.sampler import Sample, Sampler


class AffinitySampler(Sampler):
    def __init__(
        self,
        num_consecutive_actives: int = 2,
        num_filter_actives: int = 2,
    ) -> None:
        self.num_consecutive_actives = num_consecutive_actives
        self.num_filter_actives = num_filter_actives

    def sample(
        self,
        records: List[Record],
        random: RandomState,
    ) -> Iterator[Sample]:  # noqa: C901
        """Sample a structure from the dataset infinitely.

        Parameters
        ----------
        records : List[Record]
            The records to sample from.
        random : RandomState
            The random state for reproducibility.

        Yields
        ------
        Sample
            A data sample.

        """
        # Compute weights
        items = defaultdict(list)
        names = {}
        for record in records:
            for chain_id, chain in enumerate(record.chains):
                if not chain.valid:
                    continue
                if chain.mol_type == 3:
                    items[record.affinity.aid].append(
                        (record, chain_id, record.affinity.outcome)
                    )
                    names[record.id] = record.affinity.activity_name
        items_list = []
        weights = []

        for value in items.values():
            positives = []
            for tup in value:
                name = names[tup[0].id]
                if name in ["Ki", "Kd"] and tup[2] == 1:
                    positives.append((tup[0], tup[1]))
            weights.append(
                len(positives) if len(positives) >= self.num_filter_actives else 0
            )
            items_list.append(positives)

        weights = np.array(weights) / np.sum(weights)
        # Sample infinitely
        while True:
            item_idx = random.choice(len(items_list), p=weights)
            positives = items_list[item_idx]
            sample_positives = sample_fn(
                positives,
                k=min(self.num_consecutive_actives, len(positives)),
            )
            for sample in sample_positives:
                record, index = sample
                yield Sample(record=record, chain_id=index)

    def get_sample_validation(self, record: Record) -> Sample:
        for chain_id, chain in enumerate(record.chains):
            if not chain.valid:
                continue
            if chain.mol_type == 3:
                break
        return Sample(record=record, chain_id=chain_id)
