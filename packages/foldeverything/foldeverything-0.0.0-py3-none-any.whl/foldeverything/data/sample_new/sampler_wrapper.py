from typing import Iterator, List, Optional

import numpy as np
import torch
from numpy.random import RandomState
from torch.utils.data import DistributedSampler

from foldeverything.data.sample_new.sampler import Sampler
from foldeverything.task.train.data import Dataset
from foldeverything.data.data import Record


class SamplerWrapper(  # noqa: D101
    Sampler, DistributedSampler
):  # Inherit from DistributedSampler for Lightning check
    def __init__(
        self,
        datasets: List[Dataset],
        samples_per_epoch: int = 100000,
        batch_size: int = 1,
        overfit: Optional[int] = None,
        random: Optional[RandomState] = np.random,
        num_replicas: int = 1,
        rank: int = 0,
        consecutive_sample_per_dataset: int = 1,
    ) -> None:
        if torch.distributed.is_initialized():
            num_replicas = torch.distributed.get_world_size()
        if torch.distributed.is_initialized():
            rank = torch.distributed.get_rank()
        if rank >= num_replicas or rank < 0:
            msg = f"Invalid rank {rank}, rank should be in the interval [0, {num_replicas - 1}]"  # noqa: E501
            raise ValueError(msg)

        self.samples = []
        for dataset in datasets:
            records = dataset.manifest.records
            if overfit is not None:
                records = records[:overfit]
            iterator = dataset.sampler.sample(records, random)
            self.samples.append(iterator)

        self.consecutive_sample_per_dataset = consecutive_sample_per_dataset
        self.adjusted_samples_per_epoch = (
            samples_per_epoch - samples_per_epoch % (batch_size * num_replicas)
        ) // num_replicas
        self.probs = [d.prob for d in datasets]
        self.random = random

    def __iter__(self) -> Iterator[Record]:
        """Sample a structure from the dataset infinitely.

        Parameters
        ----------

        Yields
        ------
        Sample
            A data sample.

        """  # noqa: D414
        while True:
            # Pick a random dataset
            dataset_idx = self.random.choice(
                len(self.probs),
                p=self.probs,
            )
            for _ in range(self.consecutive_sample_per_dataset):
                # Get a sample from the dataset
                record: Record = next(self.samples[dataset_idx])
                yield (record, dataset_idx)

    def __len__(self) -> int:  # noqa: D105
        return self.adjusted_samples_per_epoch
