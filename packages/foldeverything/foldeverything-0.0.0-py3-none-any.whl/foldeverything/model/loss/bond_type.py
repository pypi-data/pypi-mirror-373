from typing import Dict, Optional

import torch
import torch.nn.functional as F
from torch import Tensor
from foldeverything.data import const


def bond_type_loss_fn(
    output: Dict[str, Tensor],
    feats: Dict[str, Tensor],
    pred_mask: Optional[Tensor] = None,
) -> Tensor:
    """Bond-type categorical loss following design mask pattern."""
    with torch.autocast("cuda", enabled=False):
        pred: Tensor = output["bond_type_logits"]  # (B, N, N, C)

        true_ids = feats["type_bonds"].long()  # (N, N)
        C = len(const.bond_type_ids) + 1
        true = F.one_hot(true_ids, num_classes=C).float()  # (N, N, C)

        mult = pred.shape[0] // true.shape[0]
        true = true.repeat_interleave(mult, 0)  # (B, N, N, C)

        token_mask = feats["design_mask"] * feats["token_pad_mask"]  # (B, N)
        pair_mask = token_mask[:, :, None] * token_mask[:, None, :]  # (B, N, N)
        pair_mask = pair_mask.repeat_interleave(mult, 0)  # (B, N, N)

        if pred_mask is not None:
            pair_mask = pair_mask * pred_mask.view(-1, 1, 1)
        pred_flat = pred.reshape(-1, C)  # (B*N*N, C)
        true_flat = true.reshape(-1, C)  # (B*N*N, C)

        loss = F.cross_entropy(pred_flat, true_flat, reduction="none")  # (B*N*N)
        loss = loss.reshape(pred.shape[0], -1)
        loss_mask = pair_mask.reshape(pred.shape[0], -1)
        if loss_mask.sum() == 0:
            return loss.sum() * 0.0

        loss = (loss * loss_mask).sum() / loss_mask.sum()
        return loss
