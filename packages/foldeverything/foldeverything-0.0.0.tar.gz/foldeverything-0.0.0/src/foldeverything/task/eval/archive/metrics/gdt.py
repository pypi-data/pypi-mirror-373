from typing import List

import numpy as np

from foldeverything.eval.protein import Protein
from foldeverything.eval.metrics.metric import Metric, prepare_coords


def gdt(pred: np.ndarray, target: np.ndarray, cutoffs: List[float]) -> float:
    """Compute the GDT between the predicted and target coordinates.

    Assumes the prediciton and targets are already aligned.

    Parameters
    ----------
    pred : np.ndarray
        The predicted coordinates, of shape (N, 3).
    target : np.ndarray
        The target coordinates, of shape (N, 3).

    Returns
    -------
    float
        The GDT score between the predicted and target coordinates.

    """
    distances = np.sqrt(np.sum((pred - target) ** 2, axis=-1))

    scores = []
    for c in cutoffs:
        score = np.mean(distances <= c, axis=-1)
        scores.append(score)

    return sum(scores) / len(scores)


class GDT_TS(Metric):
    """GDT_TS metric for protein structure prediction."""

    def __init__(self):
        """Initialize the GDT_TS metric."""
        # GDT_TS is only defined on alpha carbon atoms
        super().__init__(atoms=["CA"])

    def compute(self, pred: Protein, target: Protein) -> float:
        """Compute the GDT_TS between the predicted and target protein.

        Assumes the prediciton and targets are already aligned.

        Parameters
        ----------
        pred : Protein
            The predicted protein.
        target : Protein
            The target protein.

        Returns
        -------
        float
            The GDT_TS score between the predicted and target protein.

        """
        cutoffs = [1.0, 2.0, 4.0, 8.0]
        pred_coords, target_coords = prepare_coords(pred, target)
        return gdt(pred_coords, target_coords, cutoffs)


class GDT_HA(Metric):
    """GDT_HA metric for protein structure prediction."""

    def __init__(self):
        """Initialize the GDT_HA metric."""
        # GDT_HA is only defined on alpha carbon atoms
        super().__init__(atoms=["CA"])

    def compute(self, pred: Protein, target: Protein) -> float:
        """Compute the GDT_HA between the predicted and target protein.

        Assumes the prediciton and targets are already aligned.

        Parameters
        ----------
        pred : Protein
            The predicted protein.
        target : Protein
            The target protein.

        Returns
        -------
        float
            The GDT_HA score between the predicted and target protein.

        """
        cutoffs = [0.5, 1.0, 2.0, 4.0]
        pred_coords, target_coords = prepare_coords(pred, target)
        return gdt(pred_coords, target_coords, cutoffs)
