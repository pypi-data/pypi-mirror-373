import importlib
from typing import Tuple

import torch
from torch import Tensor, nn

from foldeverything.data import const
from foldeverything.model.layers.attention import AttentionPairBias
from foldeverything.model.layers.axial_samples import SamplesAxialAttention
from foldeverything.model.layers.dropout import get_dropout_mask
from foldeverything.model.layers.transition import Transition
from foldeverything.model.layers.triangular import (
    TriangleMultiplicationIncoming,
    TriangleMultiplicationOutgoing,
)

from foldeverything.model.openfold.triangular_attention import (
    TriangleAttentionEndingNode,
    TriangleAttentionStartingNode,
)

trifast_is_installed = importlib.util.find_spec("trifast") is not None
if trifast_is_installed:
    from foldeverything.model.openfold.fast_triangular_attention import (
        FastTriangleAttentionEndingNode,
        FastTriangleAttentionStartingNode,
    )


class PairformerModule(nn.Module):
    """Pairformer module."""

    def __init__(
        self,
        token_s: int,
        token_z: int,
        num_blocks: int,
        num_heads: int = 16,
        dropout: float = 0.25,
        pairwise_head_width: int = 32,
        pairwise_num_heads: int = 4,
        post_layer_norm: bool = False,
        activation_checkpointing: bool = False,
        use_trifast: bool = False,
    ) -> None:
        super().__init__()
        self.token_z = token_z
        self.num_blocks = num_blocks
        self.dropout = dropout
        self.num_heads = num_heads
        self.post_layer_norm = post_layer_norm
        self.activation_checkpointing = activation_checkpointing

        self.layers = nn.ModuleList()
        for i in range(num_blocks):
            self.layers.append(
                PairformerLayer(
                    token_s,
                    token_z,
                    num_heads,
                    dropout,
                    pairwise_head_width,
                    pairwise_num_heads,
                    post_layer_norm,
                    use_trifast,
                ),
            )

    def forward(
        self,
        s: Tensor,
        z: Tensor,
        mask: Tensor,
        pair_mask: Tensor,
    ) -> Tuple[Tensor, Tensor]:
        if not self.training:
            if z.shape[1] > const.chunk_size_threshold:
                chunk_size_tri_attn = 128
            else:
                chunk_size_tri_attn = 512
        else:
            chunk_size_tri_attn = None

        for layer in self.layers:
            if self.activation_checkpointing:
                s, z = torch.utils.checkpoint.checkpoint(
                    layer, s, z, mask, pair_mask, chunk_size_tri_attn
                )
            else:
                s, z = layer(s, z, mask, pair_mask, chunk_size_tri_attn)
        return s, z


class PairformerLayer(nn.Module):
    """Pairformer module."""

    def __init__(
        self,
        token_s: int,
        token_z: int,
        num_heads: int = 16,
        dropout: float = 0.25,
        pairwise_head_width: int = 32,
        pairwise_num_heads: int = 4,
        post_layer_norm: bool = False,
        use_trifast: bool = False,
    ) -> None:
        super().__init__()
        self.token_z = token_z
        self.dropout = dropout
        self.num_heads = num_heads
        self.post_layer_norm = post_layer_norm

        self.pre_norm_s = nn.LayerNorm(token_s)
        self.attention = AttentionPairBias(token_s, token_z, num_heads)

        self.tri_mul_out = TriangleMultiplicationOutgoing(token_z)
        self.tri_mul_in = TriangleMultiplicationIncoming(token_z)

        if use_trifast:
            self.tri_att_start = FastTriangleAttentionStartingNode(
                token_z, pairwise_head_width, pairwise_num_heads, inf=1e9
            )
            self.tri_att_end = FastTriangleAttentionEndingNode(
                token_z, pairwise_head_width, pairwise_num_heads, inf=1e9
            )
        else:
            self.tri_att_start = TriangleAttentionStartingNode(
                token_z, pairwise_head_width, pairwise_num_heads, inf=1e9
            )
            self.tri_att_end = TriangleAttentionEndingNode(
                token_z, pairwise_head_width, pairwise_num_heads, inf=1e9
            )

        self.transition_s = Transition(token_s, token_s * 4)
        self.transition_z = Transition(token_z, token_z * 4)

        self.s_post_norm = (
            nn.LayerNorm(token_s) if self.post_layer_norm else nn.Identity()
        )

    def forward(
        self,
        s: Tensor,
        z: Tensor,
        mask: Tensor,
        pair_mask: Tensor,
        chunk_size_tri_attn: int = None,
    ) -> Tuple[Tensor, Tensor]:
        # Compute pairwise stack
        dropout = get_dropout_mask(self.dropout, z, self.training)
        z = z + dropout * self.tri_mul_out(z, mask=pair_mask)

        dropout = get_dropout_mask(self.dropout, z, self.training)
        z = z + dropout * self.tri_mul_in(z, mask=pair_mask)

        dropout = get_dropout_mask(self.dropout, z, self.training)
        z = z + dropout * self.tri_att_start(
            z,
            mask=pair_mask,
            chunk_size=chunk_size_tri_attn,
        )

        dropout = get_dropout_mask(self.dropout, z, self.training, columnwise=True)
        z = z + dropout * self.tri_att_end(
            z,
            mask=pair_mask,
            chunk_size=chunk_size_tri_attn,
        )

        z = z + self.transition_z(z)

        # Compute sequence stack
        with torch.autocast("cuda", enabled=False):
            s_normed = self.pre_norm_s(s.float())
            s = s.float() + self.attention(
                s=s_normed, z=z.float(), mask=mask.float(), k_in=s_normed
            )
            s = s + self.transition_s(s)
            s = self.s_post_norm(s)

        return s, z


class PairformerNoSeqModule(nn.Module):
    """Pairformer module without sequence track."""

    def __init__(
        self,
        token_z: int,
        num_blocks: int,
        dropout: float = 0.25,
        pairwise_head_width: int = 32,
        pairwise_num_heads: int = 4,
        post_layer_norm: bool = False,
        activation_checkpointing: bool = False,
        use_trifast: bool = False,
    ) -> None:
        super().__init__()
        self.token_z = token_z
        self.num_blocks = num_blocks
        self.dropout = dropout
        self.post_layer_norm = post_layer_norm
        self.activation_checkpointing = activation_checkpointing

        self.layers = nn.ModuleList()
        for i in range(num_blocks):
            self.layers.append(
                PairformerNoSeqLayer(
                    token_z,
                    dropout,
                    pairwise_head_width,
                    pairwise_num_heads,
                    post_layer_norm,
                    use_trifast,
                ),
            )

    def forward(
        self,
        z: Tensor,
        pair_mask: Tensor,
    ) -> Tensor:
        if not self.training:
            if z.shape[1] > const.chunk_size_threshold:
                chunk_size_tri_attn = 128
            else:
                chunk_size_tri_attn = 512
        else:
            chunk_size_tri_attn = None

        for layer in self.layers:
            if self.activation_checkpointing:
                z = torch.utils.checkpoint.checkpoint(
                    layer, z, pair_mask, chunk_size_tri_attn
                )
            else:
                z = layer(z, pair_mask, chunk_size_tri_attn)
        return z


class PairformerNoSeqLayer(nn.Module):
    """Pairformer module without sequence track."""

    def __init__(
        self,
        token_z: int,
        dropout: float = 0.25,
        pairwise_head_width: int = 32,
        pairwise_num_heads: int = 4,
        post_layer_norm: bool = False,
        use_trifast: bool = False,
    ) -> None:
        super().__init__()
        self.token_z = token_z
        self.dropout = dropout
        self.post_layer_norm = post_layer_norm
        self.tri_mul_out = TriangleMultiplicationOutgoing(token_z)
        self.tri_mul_in = TriangleMultiplicationIncoming(token_z)

        if use_trifast:
            self.tri_att_start = FastTriangleAttentionStartingNode(
                token_z, pairwise_head_width, pairwise_num_heads, inf=1e9
            )
            self.tri_att_end = FastTriangleAttentionEndingNode(
                token_z, pairwise_head_width, pairwise_num_heads, inf=1e9
            )
        else:
            self.tri_att_start = TriangleAttentionStartingNode(
                token_z, pairwise_head_width, pairwise_num_heads, inf=1e9
            )
            self.tri_att_end = TriangleAttentionEndingNode(
                token_z, pairwise_head_width, pairwise_num_heads, inf=1e9
            )

        self.transition_z = Transition(token_z, token_z * 4)

    def forward(
        self,
        z: Tensor,
        pair_mask: Tensor,
        chunk_size_tri_attn: int = None,
    ) -> Tensor:
        # Compute pairwise stack
        dropout = get_dropout_mask(self.dropout, z, self.training)
        z = z + dropout * self.tri_mul_out(z, mask=pair_mask)

        dropout = get_dropout_mask(self.dropout, z, self.training)
        z = z + dropout * self.tri_mul_in(z, mask=pair_mask)

        dropout = get_dropout_mask(self.dropout, z, self.training)
        z = z + dropout * self.tri_att_start(
            z,
            mask=pair_mask,
            chunk_size=chunk_size_tri_attn,
        )

        dropout = get_dropout_mask(self.dropout, z, self.training, columnwise=True)
        z = z + dropout * self.tri_att_end(
            z,
            mask=pair_mask,
            chunk_size=chunk_size_tri_attn,
        )

        z = z + self.transition_z(z)
        return z
