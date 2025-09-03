from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterator, List, Optional

from numpy.random import RandomState
from torch.utils.data import Sampler

from foldeverything.data.data import Record


@dataclass
class Sample:
    """A sample with optional chain and interface IDs.

    Attributes
    ----------
    record : Record
        The record.
    chain_id : Optional[int]
        The chain ID.
    interface_id : Optional[int]
        The interface ID.
    """

    record: Record
    chain_id: Optional[int] = None
    interface_id: Optional[int] = None


class Sampler(Sampler):
    """Abstract base class for samplers."""

    @abstractmethod
    def __iter__(self, records: List[Record], random: RandomState) -> Iterator[Sample]:
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
        raise NotImplementedError

    @abstractmethod
    def __len__(self) -> int:
        """Get the number of samples per epoch.

        Returns
        -------
        len : int
            Number of samples per epoch.

        """
        raise NotImplementedError

    # def get_sample_validation(self, record: Record) -> Sample:
    #     """Sample chain_id and interface_id.

    #     Parameters
    #     ----------
    #     record : Record
    #         The record to sample from.

    #     Returns
    #     -------
    #     Sample
    #         A data sample.

    #     """
    #     raise NotImplementedError
