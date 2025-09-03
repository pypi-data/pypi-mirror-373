from typing import Dict, Tuple

import torch
from torch import Tensor


def tistogram_loss(
    output: Dict[str, Tensor],
    feats: Dict[str, Tensor],
    min_dist: float = 2.0,
    max_dist: float = 22.0,
    disto_bins: int = 64,
) -> Tuple[Tensor, Tensor]:
    """Compute the  distogram loss.

    Parameters
    ----------
    output : Dict[str, Tensor]
        Output of the model
    feats : Dict[str, Tensor]
        Input features
    disto_bins : int
        Number of bins for the distogram.
    min_dist : float
        Minimum distance for the distogram.
    max_dist : float
        Maximum distance for the distogram.

    Returns
    -------
    Tensor
        The globally averaged loss.
    Tensor
        Per example loss.

    """
    # Get predicted distograms
    pred = output["ptistogram"]
    axis = output["tistogram_axis"]

    # Compute target distogram
    t_center = feats["disto_center"]  # B, N, 3
    dist = t_center[:, axis, None, :] - t_center[:, None, :, :]
    dist_norm = dist / (torch.norm(dist, dim=-1, keepdim=True) + 1e-5)
    angles = (dist_norm[:, :, None, :, :] * dist_norm[:, :, :, None, :]).sum(
        -1, keepdim=True
    )

    boundaries = torch.cos(
        torch.linspace(0, torch.pi, disto_bins - 1, device=angles.device)
    )
    distogram = (angles > boundaries).sum(dim=-1).long()
    target = torch.nn.functional.one_hot(distogram, num_classes=disto_bins)

    # Combine target mask and padding mask
    mask = feats["token_disto_mask"]
    mask = mask * (1 - torch.eye(mask.shape[1])[None]).to(pred)
    mask = mask[:, None, :] * mask[:, axis, :, None] * mask[:, axis, None, :]

    # Compute the distogram loss
    errors = -1 * torch.sum(
        target * torch.nn.functional.log_softmax(pred, dim=-1),
        dim=-1,
    )
    loss = torch.sum(errors * mask) / (torch.sum(mask) + 1e-5)
    return loss
