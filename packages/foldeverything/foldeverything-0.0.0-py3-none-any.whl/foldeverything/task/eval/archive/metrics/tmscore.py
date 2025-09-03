import numpy as np

from foldeverything.types import Polymer
from foldeverything.eval.metrics.metric import Metric, prepare_coords


def tmscore(predicted: np.ndarray, target: np.ndarray) -> float:
    """Compute the TMscore between the predicted and target coordinates.

    Assumes the prediction and targets are already aligned,
    and that L_target = L_common, as defined here:
    https://en.wikipedia.org/wiki/Template_modeling_score

    Parameters
    ----------
    predicted : np.ndarray
        The predicted coordinates, of shape (N, 3).
    target : np.ndarray
        The target coordinates, of shape (N, 3).

    Returns
    -------
    float
        The TMscore score between the predicted and target coordinates.

    """
    # Compute distances
    distances = np.sqrt(np.sum((predicted - target) ** 2, axis=-1))

    # Compute d0: checked against reference code
    # https://seq2fun.dcmb.med.umich.edu//TM-score/TMscore.cpp
    L = len(predicted)
    if L <= 21:
        d0 = 0.5
    else:
        d0 = 1.24 * ((L - 15) ** (1 / 3)) - 1.8

    score = (1 / (1 + (distances / d0) ** 2)).mean()
    return score


class TMscore(Metric):
    """TMscore metric for polymer structure prediction."""

    def __init__(self):
        """Initialize the TMscore metric."""
        super().__init__(mode="backbone")

    def compute(self, predicted: Polymer, target: Polymer) -> float:
        """Compute the TMscore between the predicted and target polymer.

        Assumes the prediction and targets are already aligned.

        Parameters
        ----------
        predicted : Polymer
            The predicted polymer.
        target : Polymer
            The target polymer.

        Returns
        -------
        float
            The TMscore score between the predicted and target polymer.

        """

        pred_coords, target_coords = prepare_coords(predicted, target)
        return tmscore(pred_coords, target_coords)
