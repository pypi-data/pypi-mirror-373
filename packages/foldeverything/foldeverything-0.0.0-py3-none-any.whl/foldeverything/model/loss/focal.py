# LICENSE HEADER MANAGED BY add-license-header
#
# Copyright 2018 Kornia Team
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from __future__ import annotations

from typing import Optional

import torch
from torch import nn, Tensor
from torch.nn.functional import one_hot


def binary_focal_loss_with_logits(
    pred: Tensor,
    target: Tensor,
    alpha: Optional[float] = 0.25,
    gamma: float = 2.0,
    reduction: str = "none",
) -> Tensor:
    log_probs_pos: Tensor = nn.functional.logsigmoid(pred)
    log_probs_neg: Tensor = nn.functional.logsigmoid(-pred)

    pos_term: Tensor = -log_probs_neg.exp().pow(gamma) * target * log_probs_pos
    neg_term: Tensor = -log_probs_pos.exp().pow(gamma) * (1.0 - target) * log_probs_neg
    if alpha is not None:
        pos_term = 2 * alpha * pos_term
        neg_term = 2 * (1.0 - alpha) * neg_term

    loss_tmp: Tensor = pos_term + neg_term

    if reduction == "none":
        loss = loss_tmp
    elif reduction == "mean":
        loss = torch.mean(loss_tmp)
    elif reduction == "sum":
        loss = torch.sum(loss_tmp)
    else:
        raise NotImplementedError(f"Invalid reduction mode: {reduction}")
    return loss
