from abc import ABC, abstractmethod
from os import PathLike
from typing import List

from foldeverything.complex import Complex
from foldeverything.eval.data.dataset import Dataset
# from foldeverything.eval.protein import Prediction


class Model(ABC):
    """Abstract class for predictors."""

    @abstractmethod
    def predict(self, dataset: Dataset, outdir: PathLike) -> List[Complex]:
        """Predict the target structures for the given dataset.

        Parameters
        ----------
        dataset : Dataset
            The dataset to predict on.
        outdir: PathLike
            Path to the predicted structures.

        Returns
        -------
        List[Complex]
            Predicted complexes in the same order as the dataset.

        """
        raise NotImplementedError
