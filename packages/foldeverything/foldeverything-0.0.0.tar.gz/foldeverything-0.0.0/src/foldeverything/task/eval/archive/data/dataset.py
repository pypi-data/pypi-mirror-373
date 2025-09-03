from abc import ABC, abstractmethod
from typing import Iterator, List

# from foldeverything.eval.protein import Target
Target = None


class Dataset(ABC):
    """A dataset for evaluating protein structure prediction."""

    def __init__(self, cache_dir: str) -> None:
        """Initialize the dataset.

        Parameters
        ----------
        cache_dir : str
            The directory to store the dataset.

        """
        self.cache_dir = cache_dir

        # Download the dataset
        self.download(cache_dir)

        # Load the dataset
        self._data = self.load(cache_dir)

    @property
    def name(self) -> str:
        """The name of the dataset.

        Returns
        -------
        str
            The name of the metric.

        """
        name = self.__class__.__name__
        return name

    @property
    def fasta(self) -> str:
        """The dataset in FASTA format.

        Returns
        -------
        str
            The dataset in FASTA format.

        """
        fasta = []

        for protein in self._data:
            fasta.append(">" + protein.name)
            fasta.append(protein.sequence)

        fasta = "\n".join(fasta)
        return fasta

    @abstractmethod
    def download(self, cache_dir: str) -> None:
        """Download the dataset.

        Parameters
        ----------
        cache_dir : str
            The directory to store the dataset.

        """
        raise NotImplementedError

    @abstractmethod
    def load(self, cache_dir: str) -> List[Target]:
        """Load the dataset.

        Parameters
        ----------
        cache_dir : str
            The directory to store the dataset.

        Returns
        -------
        List[Protein]
            The dataset.

        """
        raise NotImplementedError

    def __iter__(self) -> Iterator[Target]:
        """Iterate over the dataset.

        Returns
        -------
        Iterator[Target]
            An iterator over the dataset.

        """
        return iter(self._data)

    def __getitem__(self, idx: int) -> Target:
        """Get a protein from the dataset.

        Parameters
        ----------
        idx : int
            The index of the protein target.

        Returns
        -------
        Target
            The protein target.

        """
        return self._data[idx]

    def __len__(self) -> int:
        """Return the length of the dataset.

        Returns
        -------
        int
            The length of the dataset.

        """
        return len(self._data)
