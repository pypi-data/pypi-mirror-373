# started from code from https://github.com/lucidrains/alphafold3-pytorch, MIT License, Copyright (c) 2024 Phil Wang

import torch
from torch import nn, sigmoid
from torch.nn import (
    LayerNorm,
    Linear,
    Module,
    ModuleList,
    Sequential,
)

from foldeverything.model.layers.attention import (
    AttentionNoPairBias,
    AttentionPairBias,
    # FlexAttentionPairBias,
    SDPAttentionPairBias,
    CrossAttention,
)
from foldeverything.model.modules.utils import LinearNoBias, SwiGLU, default


class AdaLN(Module):
    """Algorithm 26"""

    def __init__(self, dim, dim_single_cond):
        super().__init__()
        self.a_norm = LayerNorm(dim, elementwise_affine=False, bias=False)
        self.s_norm = LayerNorm(dim_single_cond, bias=False)
        self.s_scale = Linear(dim_single_cond, dim)
        self.s_bias = LinearNoBias(dim_single_cond, dim)

    def forward(self, a, s):
        a = self.a_norm(a)
        s = self.s_norm(s)
        a = sigmoid(self.s_scale(s)) * a + self.s_bias(s)
        return a


class ConditionedTransitionBlock(Module):
    """Algorithm 25"""

    def __init__(self, dim_single, dim_single_cond, expansion_factor=2):
        super().__init__()

        self.adaln = AdaLN(dim_single, dim_single_cond)

        dim_inner = int(dim_single * expansion_factor)
        self.swish_gate = Sequential(
            LinearNoBias(dim_single, dim_inner * 2),
            SwiGLU(),
        )
        self.a_to_b = LinearNoBias(dim_single, dim_inner)
        self.b_to_a = LinearNoBias(dim_inner, dim_single)

        output_projection_linear = Linear(dim_single_cond, dim_single)
        nn.init.zeros_(output_projection_linear.weight)
        nn.init.constant_(output_projection_linear.bias, -2.0)

        self.output_projection = nn.Sequential(output_projection_linear, nn.Sigmoid())

    def forward(
        self,
        a,  # Float['... d']
        s,
    ):  # -> Float['... d']:
        a = self.adaln(a, s)
        b = self.swish_gate(a) * self.a_to_b(a)
        a = self.output_projection(s) * self.b_to_a(b)

        return a


class DiffusionTransformer(Module):
    """Algorithm 23"""

    def __init__(
        self,
        depth,
        heads,
        dim=384,
        dim_single_cond=None,
        pair_bias_attn=True,
        flex_attention=False,
        sdp_attention=False,
        use_qk_norm=False,
        activation_checkpointing=False,
        post_layer_norm=False,
        global_mask=False,
    ):
        super().__init__()
        self.activation_checkpointing = activation_checkpointing

        dim_single_cond = default(dim_single_cond, dim)
        self.pair_bias_attn = pair_bias_attn

        self.layers = ModuleList()
        for _ in range(depth):
            self.layers.append(
                DiffusionTransformerLayer(
                    heads,
                    dim,
                    dim_single_cond,
                    post_layer_norm,
                    pair_bias_attn,
                    flex_attention,
                    sdp_attention,
                    use_qk_norm,
                    global_mask,
                )
            )

    def forward(
        self,
        a,  # Float['bm n d'],
        s,  # Float['bm n ds'],
        bias=None,  # Float['b n n dp']
        mask=None,  # Bool['b n'] | None = None
        to_keys=None,
        multiplicity=1,
        use_uniform_bias=False,
    ):
        if self.pair_bias_attn:
            B, N, M, D = bias.shape
            L = len(self.layers)
            bias = bias.view(B, N, M, L, D // L) if not use_uniform_bias else bias

        for i, layer in enumerate(self.layers):
            if self.pair_bias_attn:
                bias_l = bias[:, :, :, i]
            else:
                bias_l = None

            if self.activation_checkpointing:
                a = torch.utils.checkpoint.checkpoint(
                    layer,
                    a,
                    s,
                    bias_l if not use_uniform_bias else bias,
                    mask,
                    to_keys,
                    multiplicity,
                )

            else:
                a = layer(
                    a,  # Float['bm n d'],
                    s,  # Float['bm n ds'],
                    bias_l if not use_uniform_bias else bias,  # Float['b n n dp']
                    mask,  # Bool['b n'] | None = None
                    to_keys,
                    multiplicity,
                )
        return a


class DiffusionTransformerLayer(Module):
    """Algorithm 23"""

    def __init__(
        self,
        heads,
        dim=384,
        dim_single_cond=None,
        post_layer_norm=False,
        pair_bias_attn=True,
        flex_attention=False,
        sdp_attention=False,
        use_qk_norm=False,
        global_mask=False,
    ):
        super().__init__()

        dim_single_cond = default(dim_single_cond, dim)

        self.adaln = AdaLN(dim, dim_single_cond)

        self.pair_bias = pair_bias_attn

        if pair_bias_attn:
            if flex_attention:
                self.pair_bias_attn = FlexAttentionPairBias(
                    c_s=dim, num_heads=heads, compute_pair_bias=False
                )
            elif sdp_attention:
                self.pair_bias_attn = SDPAttentionPairBias(
                    c_s=dim,
                    num_heads=heads,
                    compute_pair_bias=False,
                    use_qk_norm=use_qk_norm,
                )
            else:
                self.pair_bias_attn = AttentionPairBias(
                    c_s=dim,
                    num_heads=heads,
                    compute_pair_bias=False,
                    global_mask=global_mask,
                    use_qk_norm=use_qk_norm,
                )
        else:
            self.no_pair_bias_attn = AttentionNoPairBias(
                dim, num_heads=heads, global_mask=global_mask, use_qk_norm=use_qk_norm
            )

        self.output_projection_linear = Linear(dim_single_cond, dim)
        nn.init.zeros_(self.output_projection_linear.weight)
        nn.init.constant_(self.output_projection_linear.bias, -2.0)

        self.output_projection = nn.Sequential(
            self.output_projection_linear, nn.Sigmoid()
        )
        self.transition = ConditionedTransitionBlock(
            dim_single=dim, dim_single_cond=dim_single_cond
        )

        if post_layer_norm:
            self.post_lnorm = nn.LayerNorm(dim)
        else:
            self.post_lnorm = nn.Identity()

    def forward(
        self,
        a,  # Float['bm n d'],
        s,  # Float['bm n ds'],
        bias=None,  # Float['b n n dp']
        mask=None,  # Bool['b n'] | None = None
        to_keys=None,
        multiplicity=1,
    ):
        b = self.adaln(a, s)

        k_in = b
        if to_keys is not None:
            k_in = to_keys(b)
            mask = to_keys(mask.unsqueeze(-1)).squeeze(-1)

        if self.pair_bias:
            b = self.pair_bias_attn(
                s=b,
                z=bias,
                mask=mask,
                multiplicity=multiplicity,
                k_in=k_in,
            )
        else:
            b = self.no_pair_bias_attn(s=b, mask=mask, k_in=k_in)

        b = self.output_projection(s) * b

        a = a + b
        a = a + self.transition(a, s)

        a = self.post_lnorm(a)
        return a


class AtomTransformer(Module):
    """Algorithm 7"""

    def __init__(
        self,
        attn_window_queries,
        attn_window_keys,
        **diffusion_transformer_kwargs,
    ):
        super().__init__()
        self.attn_window_queries = attn_window_queries
        self.attn_window_keys = attn_window_keys
        self.diffusion_transformer = DiffusionTransformer(
            **diffusion_transformer_kwargs
        )

    def forward(
        self,
        q,  # Float['b m d'],
        c,  # Float['b m ds'],
        bias,  # Float['b m m dp']
        to_keys,
        mask,  # Bool['b m'] | None = None
        multiplicity=1,
    ):
        W = self.attn_window_queries
        H = self.attn_window_keys

        B, N, D = q.shape
        NW = N // W

        # reshape tokens
        q = q.view((B * NW, W, -1))
        c = c.view((B * NW, W, -1))
        mask = mask.view(B * NW, W)
        bias = bias.repeat_interleave(multiplicity, 0)
        bias = bias.view((bias.shape[0] * NW, W, H, -1))

        to_keys_new = lambda x: to_keys(x.view(B, NW * W, -1)).view(B * NW, H, -1)

        # main transformer
        q = self.diffusion_transformer(
            a=q,
            s=c,
            bias=bias,
            mask=mask.float(),
            multiplicity=1,
            to_keys=to_keys_new,
        )

        q = q.view((B, NW * W, D))
        return q


class AllAtomTransformer(Module):
    "AtomTransformer with Flash/FlexAttention for gloabl attention"

    def __init__(self, **diffusion_transformer_kwargs):
        super().__init__()
        self.diffusion_transformer = DiffusionTransformer(
            **diffusion_transformer_kwargs
        )

    def forward(self, q, c, atom_trans_bias, mask, multiplicity=1):
        q = self.diffusion_transformer(
            a=q,
            s=c,
            bias=atom_trans_bias,
            mask=mask.float(),
            multiplicity=multiplicity,
            use_uniform_bias=True,
        )
        return q


class AnchorTransformer(Module):
    "Transformer to perform anchor cross-attention"

    def __init__(
        self,
        depth,
        heads,
        dim=384,
        dim_single_cond=None,
        flex_attention=False,
        sdp_attention=False,
        activation_checkpointing=False,
        post_layer_norm=False,
        global_mask=False,
    ):
        super().__init__()
        self.activation_checkpointing = activation_checkpointing

        dim_single_cond = default(dim_single_cond, dim)

        self.layers = ModuleList()
        for _ in range(depth):
            self.layers.append(
                AnchorTransformerLayer(
                    heads,
                    dim,
                    post_layer_norm,
                )
            )

    def forward(self, q, q_a, c, c_a, bias, mask, to_keys, multiplicity=1):
        for i, layer in enumerate(self.layers):
            if self.activation_checkpointing:
                q = torch.utils.checkpoint.checkpoint(
                    layer,
                    q,
                    q_a,
                    c,
                    c_a,
                    bias,
                    mask,
                    multiplicity,
                )
            else:
                q = layer(
                    q,
                    q_a,
                    c,
                    c_a,
                    bias,
                    mask,
                    multiplicity,
                )
        return q


class AnchorTransformerLayer(Module):
    "AnchorTransformer layer to perform anchor cross-attention"

    def __init__(
        self,
        heads,
        dim=384,
        post_layer_norm=False,
    ):
        super().__init__()
        self.adaln = AdaLN(dim, dim)

        self.cross_attn = CrossAttention(
            c_s=dim, num_heads=heads, compute_pair_bias=False
        )

        self.transition = ConditionedTransitionBlock(
            dim_single=dim, dim_single_cond=dim
        )

        if post_layer_norm:
            self.post_lnorm = nn.LayerNorm(dim)
        else:
            self.post_lnorm = nn.Identity()

    def forward(self, q, q_a, c, c_a, bias, mask, multiplicity=1):
        q = self.adaln(q, c)
        k_a = self.adaln(q_a, c_a)

        b = self.cross_attn(q, k_a, mask, multiplicity=multiplicity)
        q = q + b
        q = q + self.transition(q, c)

        q = self.post_lnorm(q)
        return q
