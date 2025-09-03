from abc import ABC, abstractmethod

from foldeverything.data.data import Structure, Tokenized


class Tokenizer(ABC):
    """Tokenize an input structure for training."""

    @abstractmethod
    def tokenize(self, struct: Structure, training: bool = False) -> Tokenized:
        """Tokenize the input data.

        Parameters
        ----------
        struct : Structure
            The input structure.
        training: bool
            Whether we are at training or inference time

        Returns
        -------
        Tokenized
            The tokenized data.

        """
        raise NotImplementedError
