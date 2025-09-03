from collections import Counter
from typing import Dict, Iterator, List

import numpy as np
from numpy.random import RandomState

from foldeverything.data.data import Record
from foldeverything.data.sample.sampler import Sample, Sampler


class AffinitySampler(Sampler):
    def __init__(
        self,
        importance_active: float = 1.0,
        importance_inactive: float = 1.0,
        only_k: bool = False,
    ) -> None:
        self.importance_active = importance_active
        self.importance_inactive = importance_inactive
        self.only_k = only_k

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
        items, outcomes, aids, activity_names = [], [], [], []

        for record in records:
            for chain_id, chain in enumerate(record.chains):
                if not chain.valid:
                    continue
                if chain.mol_type == 3:
                    items.append((record, chain_id))
                    # TODO: modify this with the weight function depending confidence, positive/negative, quality, affinity_type, protein_ID, smile_ID etc.
                    # TODO: add flag for main affinity molecule and add condition
                    outcomes.append(record.affinity.outcome)
                    aids.append(record.affinity.aid)
                    activity_names.append(record.affinity.activity_name)
        weight_active = self.importance_active
        weight_inactive = self.importance_inactive
        weight_outcome = {1: weight_active, 0: weight_inactive}
        count_aid_positives_dict = Counter(
            [aid for aid, outcome in zip(aids, outcomes) if outcome == 1]
        )
        count_aid_negatives_dict = Counter(
            [aid for aid, outcome in zip(aids, outcomes) if outcome == 0]
        )
        weights = []
        for outcome, aid, activity_name in zip(outcomes, aids, activity_names):
            if count_aid_negatives_dict[aid] == 0 or count_aid_positives_dict[aid] == 0:
                weights.append(0.0)
            elif self.only_k and not activity_name in ["Ki", "Kd"]:
                weights.append(0.0)
            else:
                if outcome == 1:
                    weights.append(weight_outcome[outcome])
                else:
                    weights.append(
                        count_aid_positives_dict[aid]
                        / count_aid_negatives_dict[aid]
                        * weight_outcome[outcome]
                    )
        # Sample infinitely
        weights = np.array(weights) / np.sum(weights)
        while True:
            item_idx = random.choice(len(items), p=weights)
            record, index = items[item_idx]
            yield Sample(record=record, chain_id=index)

    def get_sample_validation(self, record: Record) -> Sample:
        for chain_id, chain in enumerate(record.chains):
            if not chain.valid:
                continue
            if chain.mol_type == 3:
                break
        return Sample(record=record, chain_id=chain_id)
