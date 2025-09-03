from typing import Tuple, List, Set

import numpy as np

from foldeverything.types import Polymer
from foldeverything.eval.metrics.metric import Metric, prepare_coords


def efficient_distances(
    points: np.ndarray, cutoff: float, pairs_array=None
) -> Tuple[Set[Tuple[int, int]], np.ndarray]:
    from scipy.spatial import cKDTree

    if pairs_array is None:
        # Create a KDTree for efficient nearest neighbor search
        tree = cKDTree(points)

        # Query the tree for pairs within the cutoff distance
        pairs = tree.query_pairs(cutoff)
        pairs_array = np.array(list(pairs))

    # Calculate the distances for these pairs only
    # distances = np.sqrt(np.sum((points[i] - points[j])**2) for i, j in pairs)
    # Create index arrays for the first and second elements of each pair
    i_indices = pairs_array[:, 0]
    j_indices = pairs_array[:, 1]

    # Use advanced indexing to calculate the distances
    distances = np.sqrt(
        np.sum((points[i_indices, :] - points[j_indices, :]) ** 2, axis=-1)
    )

    return pairs_array, distances


def lddt(
    pred: np.ndarray,
    target: np.ndarray,
    cutoff: float = 15.0,
    per_residue: bool = False,
    efficient_mode: bool = None,
) -> float:
    """Measure (approximate) lDDT for a batch of coordinates.

    lDDT reference:
    Mariani, V., Biasini, M., Barbato, A. & Schwede, T.
    lDDT: A local superposition-free score for comparing
    protein structures and models using distance difference
    tests. Bioinformatics 29, 2722–2728 (2013).

    lDDT is a measure of the difference between the true
    distance matrix and the distance matrix of the predicted
    points.  The difference is computed only on points closer
    than cutoff *in the true structure*. This function does
    not compute the exact lDDT value that the original paper
    describes because it does not include terms for physical
    feasibility (e.g. bond length violations). Therefore this
    is only an approximate lDDT score.

    Parameters
    ----------
    pred: np.ndarray
        (N, 3) array of predicted 3D points
    target: np.ndarray
        (N, 3) array of true 3D points
    cutoff: float
        Maximum distance for a pair of points to be included
    per_residue: If true, return score for each residue.
        Note that the overall lDDT is not exactly the mean of
        the per_residue lDDT's because some residues have more
        contacts than others.
    efficient_mode : bool
        If true, use a more memory-efficient method for large
        polymers. This is recommended for polymers with more
        than ~1000 points.

    Returns
    -------
    float
        An (approximate, see above) lDDT score in the range 0-1.

    """
    assert len(pred.shape) == 2
    assert len(target.shape) == 2
    assert pred.shape[-1] == 3
    assert target.shape[-1] == 3

    # Compute true and predicted distance matrices.
    # For large polymers, this can be quite memory-intensive.
    num_points = pred.shape[0]
    if efficient_mode is None:
        efficient_mode = num_points > 4_000

    if not efficient_mode:
        if num_points > 4_000:
            print(
                f"Warning: Large polymer with {num_points} points. This will be slow, use a lot of memory, and may crash. "
                f"Consider setting efficient_mode=True."
            )

        dmat_true = np.sqrt(
            1e-10 + np.sum((target[:, None] - target[None, :]) ** 2, axis=-1)
        )

        dists_to_score = (dmat_true < cutoff).astype(np.float32) * (
            1.0 - np.eye(dmat_true.shape[1])
        )  # Exclude self-interaction.

        dmat_predicted = np.sqrt(
            1e-10 + np.sum((pred[:, None] - pred[None, :]) ** 2, axis=-1)
        )

        # Shift unscored distances to be far away.
        dmat_predicted += (1 - dists_to_score) * (cutoff * 100.0)
        dist_l1 = np.abs(dmat_true - dmat_predicted)

        # True lDDT uses a number of fixed bins.
        # We ignore the physical plausibility correction to lDDT, though.
        score = 0.25 * (
            (dist_l1 < 0.5).astype(np.float32)
            + (dist_l1 < 1.0).astype(np.float32)
            + (dist_l1 < 2.0).astype(np.float32)
            + (dist_l1 < 4.0).astype(np.float32)
        )

        # Normalize over the appropriate axes.
        reduce_axes = (-1,) if per_residue else (-2, -1)
        norm = 1.0 / (1e-10 + np.sum(dists_to_score, axis=reduce_axes))
        score = norm * (1e-10 + np.sum(dists_to_score * score, axis=reduce_axes))

    else:
        assert (
            not per_residue
        ), "Per-residue calculation not available in efficient mode."
        # For large polymers, we use a more memory-efficient method.
        target_pairs, dists_true = efficient_distances(target, cutoff)
        pred_pairs, dists_pred = efficient_distances(
            pred, cutoff, pairs_array=target_pairs
        )
        dist_l1 = np.abs(dists_true - dists_pred)

        # True lDDT uses a number of fixed bins.
        # We ignore the physical plausibility correction to lDDT, though.
        score = 0.25 * (
            (dist_l1 < 0.5).astype(np.float32)
            + (dist_l1 < 1.0).astype(np.float32)
            + (dist_l1 < 2.0).astype(np.float32)
            + (dist_l1 < 4.0).astype(np.float32)
        )

        num_pairs = len(target_pairs)
        score = np.sum(score) / num_pairs

    return score


class LDDT(Metric):
    """lDDT metric for polymer structure prediction."""

    def compute(self, predicted: Polymer, target: Polymer) -> float:
        """Compute lDDT between the predicted and target polymers.

        Parameters
        ----------
        predicted : Polymer
            The predicted polymer.
        target : Polymer
            The target polymer.

        Returns
        -------
        float
            The lDDT between the predicted and target polymers.

        """
        pred_coords, target_coords = prepare_coords(predicted, target)

        return lddt(pred_coords, target_coords)
