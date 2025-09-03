from typing import Tuple

import torch
from torch import Tensor, nn

from foldeverything.model.layers.attention import AttentionPairBias
from foldeverything.model.layers.axial import AxialAttentionEnd, AxialAttentionStart
from foldeverything.model.layers.axial_samples import SamplesAxialAttention
from foldeverything.model.layers.dropout import (
    get_dropout_mask_columnwise,
    get_dropout_mask_rowise,
)
from foldeverything.model.layers.transition import Transition
from foldeverything.model.layers.triangular import (
    MiniTriangularUpdate,
    TriangleMultiplicationIncoming,
    TriangleMultiplicationOutgoing,
)


class MiniformerModule(nn.Module):
    """Miniformer module."""

    def __init__(
        self,
        token_s: int,
        token_z: int,
        num_blocks: int,
        num_heads: int = 16,
        dropout: float = 0.25,
        use_miniformer_plus: bool = False,
        use_trifast: bool = False,
        use_s_to_z: bool = False,
        post_layer_norm: bool = False,
        activation_checkpointing: bool = False,
    ) -> None:
        super().__init__()
        self.token_z = token_z
        self.use_s_to_z = use_s_to_z
        self.num_blocks = num_blocks
        self.dropout = dropout
        self.num_heads = num_heads
        self.post_layer_norm = post_layer_norm
        self.layers = nn.ModuleList()
        self.use_miniformer_plus = use_miniformer_plus
        self.activation_checkpointing = activation_checkpointing

        miniformer_cls = MiniformerPlusLayer if use_miniformer_plus else MiniformerLayer
        for i in range(num_blocks):
            self.layers.append(
                miniformer_cls(
                    token_s,
                    token_z,
                    num_heads,
                    dropout,
                    post_layer_norm,
                    use_s_to_z,
                ),
            )

    def forward(
        self,
        s: Tensor,
        z: Tensor,
        mask: Tensor,
        pair_mask: Tensor,
    ) -> Tuple[Tensor, Tensor]:

        for layer in self.layers:
            if self.activation_checkpointing:
                s, z = torch.utils.checkpoint.checkpoint(
                    layer, s, z, mask, pair_mask
                )
            else:
                s, z = layer(s, z, mask, pair_mask)
        return s, z


class MiniformerLayer(nn.Module):
    """Miniformer layer."""

    def __init__(
        self,
        token_s: int,
        token_z: int,
        num_heads: int = 16,
        dropout: float = 0.25,
        post_layer_norm: bool = False,
        use_s_to_z: bool = False,
    ) -> None:
        super().__init__()
        self.token_z = token_z
        self.dropout = dropout
        self.num_heads = num_heads
        self.post_layer_norm = post_layer_norm
        self.use_s_to_z = use_s_to_z

        self.pre_norm_s = nn.LayerNorm(token_s)
        self.attention = AttentionPairBias(token_s, token_z, num_heads)

        self.triangular = MiniTriangularUpdate(token_z)

        self.transition_s = Transition(token_s, token_s * 4)
        self.transition_z = Transition(token_z, token_z * 4)

        if self.post_layer_norm:
            self.s_post_norm = nn.LayerNorm(token_s)
        else:
            self.s_post_norm = nn.Identity()

        if self.use_s_to_z:
            self.s_to_z_1 = nn.Linear(token_s, token_z, bias=False)
            self.s_to_z_2 = nn.Linear(token_s, token_z, bias=False)

    def forward(
        self,
        s: Tensor,
        z: Tensor,
        mask: Tensor,
        pair_mask: Tensor,
    ) -> Tuple[Tensor, Tensor]:

        # Compute s to z messages
        if self.use_s_to_z:
            s_to_z = self.s_to_z_1(s)[:, :, None] + self.s_to_z_2(s)[:, None, :]
            z = z + s_to_z

        # Compute pairwise stack
        dropout = get_dropout_mask_rowise(self.dropout, z, self.training)
        z = z + dropout * self.triangular(z, mask=pair_mask)
        z = z + self.transition_z(z)

        # Compute sequence stack
        with torch.autocast("cuda", enabled=False):
            s_normed = self.pre_norm_s(s.float())
            s = s.float() + self.attention(s=s_normed, z=z.float(), mask=mask.float(), k_in=s_normed)
            s = s + self.transition_s(s)
            s = self.s_post_norm(s)

        return s, z


class MiniformerPlusLayer(nn.Module):
    """Miniformer layer."""

    def __init__(
        self,
        token_s: int,
        token_z: int,
        num_heads: int = 16,
        dropout: float = 0.25,
        post_layer_norm: bool = False,
    ) -> None:
        super().__init__()
        self.token_z = token_z
        self.dropout = dropout
        self.num_heads = num_heads
        self.post_layer_norm = post_layer_norm
        self.pre_norm_s = nn.LayerNorm(token_s)
        self.attention = AttentionPairBias(token_s, token_z, num_heads)
        self.mul_out = TriangleMultiplicationOutgoing(token_z)
        self.mul_in = TriangleMultiplicationIncoming(token_z)
        self.attn_start = AxialAttentionStart(token_z, hidden=token_z // 4, no_heads=4)
        self.attn_end = AxialAttentionEnd(token_z, hidden=token_z // 4, no_heads=4)
        self.transition_s = Transition(token_s, token_s * 4)
        self.transition_z = Transition(token_z, token_z * 4)

        if self.post_layer_norm:
            self.s_post_norm = nn.LayerNorm(token_s)
        else:
            self.s_post_norm = nn.Identity()

    def forward(
        self,
        s: Tensor,
        z: Tensor,
        mask: Tensor,
        pair_mask: Tensor,
    ) -> Tuple[Tensor, Tensor]:

        # Compute pairwise stack
        drop = get_dropout_mask_rowise(self.dropout, z, self.training)
        z = z + drop * self.mul_out(z, mask=pair_mask)

        drop = get_dropout_mask_rowise(self.dropout, z, self.training)
        z = z + drop * self.mul_in(z, mask=pair_mask)

        drop = get_dropout_mask_rowise(self.dropout, z, self.training)
        z = z + drop * self.attn_start(z, mask=pair_mask.bool())

        drop = get_dropout_mask_columnwise(self.dropout, z, self.training)
        z = z + drop * self.attn_end(mask=pair_mask.bool())

        # Compute transition
        z = z + self.transition_z(z)

        # Compute sequence stack
        s_normed = self.pre_norm_s(s)
        s = s + self.attention(s=s_normed, z=z, mask=mask, k_in=s_normed)
        s = s + self.transition_s(s)

        # Post-LN
        s = self.s_post_norm(s)

        return s, z


class MiniformerNoSeqModule(nn.Module):
    """Miniformer module without sequence track."""

    def __init__(
        self,
        token_z: int,
        num_blocks: int,
        dropout: float = 0.25,
        post_layer_norm: bool = False,
        activation_checkpointing: bool = False,
    ) -> None:
        super().__init__()
        self.token_z = token_z
        self.num_blocks = num_blocks
        self.dropout = dropout
        self.post_layer_norm = post_layer_norm
        self.layers = nn.ModuleList()
        self.activation_checkpointing = activation_checkpointing

        for i in range(num_blocks):
            self.layers.append(
                MiniformerNoSeqLayer(
                    token_z,
                    dropout,
                    post_layer_norm,
                ),
            )

    def forward(
        self,
        z: Tensor,
        pair_mask: Tensor,
    ) -> Tensor:

        for layer in self.layers:
            if self.activation_checkpointing:
                z = torch.utils.checkpoint.checkpoint(
                    layer, z, pair_mask
                )
            else:
                z = layer(z, pair_mask)
        return z


class MiniformerNoSeqLayer(nn.Module):
    """Miniformer layer without sequence track."""

    def __init__(
        self,
        token_z: int,
        dropout: float = 0.25,
        post_layer_norm: bool = False,
    ) -> None:
        super().__init__()
        self.token_z = token_z
        self.dropout = dropout
        self.post_layer_norm = post_layer_norm

        self.triangular = MiniTriangularUpdate(token_z)
        self.transition_z = Transition(token_z, token_z * 4)

        if self.post_layer_norm:
            self.z_post_norm = nn.LayerNorm(token_z)
        else:
            self.z_post_norm = nn.Identity()

    def forward(
        self,
        z: Tensor,
        pair_mask: Tensor,
        chunk_size_tri_attn: int = None,
    ) -> Tensor:

        # Compute pairwise stack
        dropout = get_dropout_mask_rowise(self.dropout, z, self.training)
        z = z + dropout * self.triangular(z, mask=pair_mask)
        z = z + self.transition_z(z)

        # Post-LN
        z = self.z_post_norm(z)
        return z
