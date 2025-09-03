from typing import Dict

import numpy as np
import scipy

from foldeverything.complex import Complex
from foldeverything.types import Polymer
from foldeverything.eval.metrics.metric import Metric, prepare_coords
from foldeverything.eval.utils import write_complex


def _w_coefs(d: np.ndarray, d0: float = 8.0, eps: float = 1e-8) -> np.ndarray:
    """Compute the weights for the CODM score.

    Parameters
    ----------
    d : np.ndarray, (N,N)
        The difference between CA atoms of residue pair k.
    d0 : float
        The reference distance. Default is 8.0 angstroms.

    Returns
    -------
    np.ndarray, (N,N)
        The weights for the CODM score.
    """
    return 1.0 / ((4.0 * np.pi * (d**2)) * (1.0 + (d / d0) ** 2) + eps)


def weighted_covariance(x: np.ndarray, y: np.ndarray, w: np.ndarray) -> float:
    """Compute the weighted covariance between two arrays.

    Parameters
    ----------
    x : np.ndarray
        The first array.
    y : np.ndarray
        The second array.
    w : np.ndarray
        The weights.

    Returns
    -------
    float
        The weighted covariance.
    """
    wxm = np.average(x, weights=w)
    wym = np.average(y, weights=w)
    return np.sum(w * (x - wxm) * (y - wym)) / np.sum(w)


def codm_score(pred_dist: np.ndarray, target_dist: np.ndarray) -> float:
    """Compute CODM score

    CoDM score is a weighted Pearson’s correlation of the
    distance matrices of the target and model structures. It
    ranges over [-1,1]. Each element k of the distance
    matrix, where k is the residue pair index that ranges
    from 1 to n^2, is weighted by w_k given by

    w_k = w_{k,m} + w_{k,t}

    with

    w_{k,t) = \frac{1}{4 \pi d^2_{k,t}} \dot \frac{1}{1 + (d_{k,t}/d_0)^2}

    d_{k,t} is the difference between CA atoms of residue pair k
    in the target structure. d_{k,m} is the same for the model (aka predicted).

    d_0 is a reference distance. The source uses d_0 = 8.0 angstroms.

    https://onlinelibrary.wiley.com/doi/pdf/10.1002/prot.24470

    Parameters
    ----------
    pred_dist: np.ndarray, (N,N)
        The predicted distance map between CA atoms.
    target_dist: np.ndarray, (N,N)
        The target distance map between CA atoms.
    """

    # Exclude the diagonal, those are always 0
    iu, ju = np.triu_indices(pred_dist.shape[0], k=+1)
    # il, jl = np.tril_indices(pred_dist.shape[0], k=-1)
    # off_diag = (np.concatenate([iu, il]), np.concatenate([ju, jl]))
    keep_locs = iu, ju

    pred_dist = pred_dist[keep_locs].flatten()
    target_dist = target_dist[keep_locs].flatten()

    # Compute the weights
    w_km = _w_coefs(pred_dist)
    w_kt = _w_coefs(target_dist)
    w = w_km + w_kt

    # scipy.stats.pearsonr can't take weights, so we do this manually
    weighted_cov = weighted_covariance(pred_dist, target_dist, w)
    weighted_var_x = weighted_covariance(pred_dist, pred_dist, w)
    weighted_var_y = weighted_covariance(target_dist, target_dist, w)
    codm_score = weighted_cov / np.sqrt(weighted_var_x * weighted_var_y)

    return codm_score


class CoDM(Metric):
    """
    Correlation of Distance Matrix score

    "Tai, Chin‐Hsien, et al. "Assessment of template‐free modeling in CASP10 and ROLL." Proteins: Structure, Function, and Bioinformatics 82 (2014): 57-83.
    https://onlinelibrary.wiley.com/doi/pdf/10.1002/prot.24470
    """

    def __init__(self) -> None:
        super().__init__(mode="backbone")

    def compute(self, predicted: Polymer, target: Polymer) -> Dict[str, float]:
        """
        TODO Should we use the distance matrix directly?
        """

        pred_coords, target_coords = prepare_coords(predicted, target)
        pred_dist = scipy.spatial.distance.cdist(pred_coords, pred_coords)
        target_dist = scipy.spatial.distance.cdist(target_coords, target_coords)

        score = codm_score(pred_dist, target_dist)

        return {"codm": score}
