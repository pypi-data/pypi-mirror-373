from typing import Dict, Optional

import torch
from torch import Tensor


def bond_len_loss_fn(
    output: Dict[str, Tensor],
    feats: Dict[str, Tensor],
    pred_mask: Optional[Tensor] = None,
    l1: bool = True,
) -> Tensor:
    """Bond-length regression loss with design mask pattern."""
    with torch.autocast("cuda", enabled=False):

        pred: Tensor = output["bond_len_pred"]  # (B, N, N)
        center_coords: Tensor = feats["center_coords"].float()  # (N, 3) or (B0, N, 3)
        true = torch.cdist(center_coords, center_coords)  # (N, N)

        mult = pred.shape[0] // true.shape[0]
        true = true.repeat_interleave(mult, 0)

        token_mask = feats["design_mask"] * feats["token_pad_mask"]  # (B, N)
        pair_mask = token_mask[:, :, None] * token_mask[:, None, :]  # (B, N, N)
        pair_mask = pair_mask.repeat_interleave(mult, 0)
        if pred_mask is not None:
            pair_mask = pair_mask * pred_mask.view(-1, 1, 1)
        diff = pred - true
        per = diff.abs() if l1 else diff.pow(2)
        per = per * pair_mask

        if pair_mask.sum() == 0:
            return per.sum() * 0.0
        loss = per.sum() / pair_mask.sum()
        return loss
