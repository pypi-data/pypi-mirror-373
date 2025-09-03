from typing import Iterator, List, Optional, Any
from collections import defaultdict

import numpy as np
import torch
from numpy.random import RandomState
import random
from torch.utils.data import DistributedSampler

from foldeverything.data.sample_new.sampler import Sample, Sampler
from foldeverything.task.train.data import Dataset
import math
from functools import reduce


def lcm(a, b):
    return abs(a * b) // math.gcd(a, b)


def lcm_list(numbers):
    return reduce(lcm, numbers)


class SamplerWrapperValidation(  # noqa: D101
    Sampler, DistributedSampler
):  # Inherit from DistributedSampler for Lightning check
    def __init__(
        self,
        datasets: List[Dataset],
        groups: List[List] = [[0, 1, 2]],
        batch_size: int = 1,
        num_replicas: int = 1,
        rank: int = 0,
        group_to_aid_to_known_ids_list: Optional[Any] = None,
    ) -> None:
        if torch.distributed.is_initialized():
            num_replicas = torch.distributed.get_world_size()
            rank = torch.distributed.get_rank()
        if rank >= num_replicas or rank < 0:
            msg = f"Invalid rank {rank}, rank should be in the interval [0, {num_replicas - 1}]"  # noqa: E501
            raise ValueError(msg)

        self.groups = groups
        groups_union = list(set([g for groups_d in groups for g in groups_d]))
        lcm_groups = lcm_list([g + 1 for g in groups_union])
        assert (
            batch_size % lcm_groups == 0
        ), "Batch size should be divisible by the LCM of groups"
        self.rank = rank
        self.effective_batch_size = num_replicas * batch_size
        map_idx_to_aid_dataset = {}
        map_aid_dataset_to_idx = defaultdict(list)
        count = 0
        for dataset_idx, dataset in enumerate(datasets):
            records = dataset.manifest.records
            for record in records:
                aid = record.affinity.aid
                map_idx_to_aid_dataset[count] = (aid, dataset_idx)
                map_aid_dataset_to_idx[(aid, dataset_idx)].append(count)
                count += 1
        self.map_idx_to_aid_dataset = map_idx_to_aid_dataset

        group_to_aid_to_known_ids = {}
        for group in groups_union:
            aid_to_known_ids = {}
            for aid_dataset, list_ids in map_aid_dataset_to_idx.items():
                if group not in groups[aid_dataset[1]]:
                    continue
                if (
                    group_to_aid_to_known_ids_list is not None
                    and group in group_to_aid_to_known_ids_list[aid_dataset[1]]
                ):
                    known_ids = group_to_aid_to_known_ids_list[aid_dataset[1]][group][
                        aid_dataset[0]
                    ]
                else:
                    known_ids = random.sample(list_ids, group)
                aid_to_known_ids[aid_dataset] = known_ids
            group_to_aid_to_known_ids[group] = aid_to_known_ids
        self.group_to_aid_to_known_ids = group_to_aid_to_known_ids

        self.group_to_total_size = {}
        total_size = len(map_idx_to_aid_dataset)
        for group in groups_union:
            size_group = 0
            for dataset_idx, dataset in enumerate(datasets):
                if group not in groups[dataset_idx]:
                    continue
                removed = sum(
                    len(known_ids) if aid_dataset[1] == dataset_idx else 0
                    for aid_dataset, known_ids in group_to_aid_to_known_ids[
                        group
                    ].items()
                )
                total_size = len(datasets[dataset_idx].manifest.records)
                size = (total_size - removed) * (group + 1)
                size_group += size
            self.group_to_total_size[group] = size_group - size_group % batch_size

        self.total_size_per_rank = (
            sum(self.group_to_total_size.values()) // self.effective_batch_size
        ) * batch_size

    def __iter__(self) -> Iterator[Sample]:
        """Sample a structure from the dataset infinitely.

        Parameters
        ----------

        Yields
        ------
        Sample
            A data sample.

        """  # noqa: D414
        indices_group = {}
        unique_idx_cross_transformer = 0
        for group, aid_to_known_ids in self.group_to_aid_to_known_ids.items():
            indices = []
            for idx, aid_dataset in self.map_idx_to_aid_dataset.items():
                if group not in self.groups[aid_dataset[1]]:
                    continue
                known_ids = aid_to_known_ids[aid_dataset]
                if idx in known_ids:
                    continue
                else:
                    indices.append((idx, group, unique_idx_cross_transformer, 0))
                    indices += [
                        (i, group, unique_idx_cross_transformer, 1) for i in known_ids
                    ]
                unique_idx_cross_transformer += 1
            indices_group[group] = indices

        indices_drop_last = []
        for group, indices in indices_group.items():
            indices_drop_last += indices[: self.group_to_total_size[group]]

        indices_rank = indices_drop_last[
            self.rank
            * self.total_size_per_rank : (self.rank + 1)
            * self.total_size_per_rank
        ]
        return iter(indices_rank)

    def __len__(self) -> int:  # noqa: D105
        return self.total_size_per_rank
