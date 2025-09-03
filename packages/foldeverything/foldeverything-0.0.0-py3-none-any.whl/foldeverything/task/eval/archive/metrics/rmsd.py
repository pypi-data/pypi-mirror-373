import numpy as np

from foldeverything.complex import Complex
from foldeverything.types import Polymer
from foldeverything.eval.metrics.metric import Metric, prepare_coords


def rmsd(predicted: np.ndarray, target: np.ndarray) -> float:
    """Compute the RMSD between the predicted and target coordinates.

    Assumes the prediction and targets are already aligned.

    Parameters
    ----------
    predicted : np.ndarray
        The predicted coordinates, of shape (N, 3).
    target : np.ndarray
        The target coordinates, of shape (N, 3).

    Returns
    -------
    float
        The RMSD score between the predicted and target coordinates.

    """
    diff = predicted - target
    return np.sqrt(np.mean(np.sum(diff**2, axis=1)))


class RMSD(Metric):
    """RMSD metric for structure prediction."""

    def compute(self, predicted: Polymer, target: Polymer) -> float:
        """Compute the RMSD between the predicted and target structures.

        Assumes the predicted and target atoms are already aligned.

        Parameters
        ----------
        predicted : Polymer
            The predicted structure.
        target : Polymer
            The target structure.

        Returns
        -------
        float
            The RMSD score between the predicted and target structure.

        """
        pred_coords, target_coords = prepare_coords(predicted, target)
        return rmsd(pred_coords, target_coords)
