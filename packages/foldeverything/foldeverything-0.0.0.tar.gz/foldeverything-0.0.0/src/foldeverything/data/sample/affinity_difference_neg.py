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
        num_consecutive_active: int = 1,
        num_consecutive_inactive: int = 1,
        num_filter_active: int = 1,
    ) -> None:
        self.num_consecutive_active = num_consecutive_active
        self.num_consecutive_inactive = num_consecutive_inactive
        self.num_filter_active = num_filter_active

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
        confidences = {}
        for record in records:
            for chain_id, chain in enumerate(record.chains):
                if not chain.valid:
                    continue
                if chain.mol_type == 3:
                    items[record.affinity.aid].append(
                        (record, chain_id, record.affinity.outcome)
                    )
                    confidences[record.id] = record.affinity.confidence[
                        1
                    ]  # PLDDT ligand median confidence
        items_list = []
        weights = []

        for value in items.values():
            positives = []
            negatives = []
            for tup in value:
                confidence = confidences[tup[0].id]
                if confidence > 0.25:
                    if tup[2] == 1:
                        positives.append((tup[0], tup[1]))
                    else:
                        negatives.append((tup[0], tup[1]))
            weights.append(
                len(positives) if len(positives) >= self.num_filter_active else 0
            )
            items_list.append((positives, negatives))

        weights = np.array(weights) / np.sum(weights)
        # Sample infinitely
        while True:
            item_idx = random.choice(len(items_list), p=weights)
            positives, negatives = items_list[item_idx]
            sample_positives = sample_fn(
                positives,
                k=min(self.num_consecutive_active, len(positives)),
            )
            sample_negatives = sample_fn(
                negatives,
                k=min(self.num_consecutive_inactive, len(negatives)),
            )
            for sample in sample_positives:
                record, index = sample
                yield Sample(record=record, chain_id=index)
            for sample in sample_negatives:
                record, index = sample
                yield Sample(record=record, chain_id=index)

    def get_sample_validation(self, record: Record) -> Sample:
        for chain_id, chain in enumerate(record.chains):
            if not chain.valid:
                continue
            if chain.mol_type == 3:
                break
        return Sample(record=record, chain_id=chain_id)
