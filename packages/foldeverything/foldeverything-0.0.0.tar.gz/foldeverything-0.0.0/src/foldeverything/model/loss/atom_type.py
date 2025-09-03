from typing import Dict

import torch
from torch import Tensor
import torch.nn.functional as F
from typing import Optional

def atom_type_loss_fn(
    output: Dict[str, Tensor],
    feats: Dict[str, Tensor],
    pred_mask: Optional[Tensor] = None,
) -> Tensor:
    """Compute the res_type loss.

    Parameters
    ----------
    output : Dict[str, Tensor]
        Output of the model
    feats : Dict[str, Tensor]
        Input features

    Returns
    -------
    Tensor
        The globally averaged loss.
    """
    with torch.autocast("cuda", enabled=False):

        atom_design_mask = (
            feats["atom_to_token"].float() @ feats["design_mask"].unsqueeze(-1).float()
        ).squeeze(-1)
        loss_mask = feats["atom_pad_mask"] * atom_design_mask

        pred = output["atom_type"]
        true = feats["ref_element"].float()

        multiplicity = pred.shape[0] // true.shape[0]
        true = true.repeat_interleave(multiplicity, 0)
        loss_mask = loss_mask.repeat_interleave(multiplicity, 0)
        if pred_mask is not None:
            loss_mask = loss_mask * pred_mask.view(-1, 1)


        pred_flat = pred.reshape(-1, pred.shape[-1])
        true_flat = true.reshape(-1, true.shape[-1])

        loss = F.cross_entropy(pred_flat, true_flat, reduction="none")
        loss = loss.reshape(pred.shape[0], -1)

        if loss_mask.sum() == 0:
            loss = loss.sum() * 0.0
        else:
            loss = (loss * loss_mask).sum() / loss_mask.sum()

        return loss
