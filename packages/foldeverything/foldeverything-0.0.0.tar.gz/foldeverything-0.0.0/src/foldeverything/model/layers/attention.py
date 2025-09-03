import torch
from einops.layers.torch import Rearrange
from torch import Tensor, nn
import foldeverything.model.layers.initialize as init
import torch.nn.functional as F
from torch.nn.attention.flex_attention import flex_attention
from torch.nn.functional import scaled_dot_product_attention
from typing import Callable


class AttentionPairBias(nn.Module):
    """Attention pair bias layer."""

    def __init__(
        self,
        c_s: int,
        c_z: int = None,
        num_heads: int = None,
        inf: float = 1e6,
        compute_pair_bias: bool = True,
        global_mask: bool = False,
        use_qk_norm: bool = False,
    ) -> None:
        """Initialize the attention pair bias layer.

        Parameters
        ----------
        c_s : int
            The input sequence dimension.
        c_z : int
            The input pairwise dimension.
        num_heads : int
            The number of heads.
        inf : float, optional
            The inf value, by default 1e6

        """
        super().__init__()

        assert c_s % num_heads == 0

        self.c_s = c_s
        self.num_heads = num_heads
        self.head_dim = c_s // num_heads
        self.inf = inf
        self.global_mask = global_mask
        self.proj_q = nn.Linear(c_s, c_s)
        self.proj_k = nn.Linear(c_s, c_s, bias=False)
        self.proj_v = nn.Linear(c_s, c_s, bias=False)
        self.proj_g = nn.Linear(c_s, c_s, bias=False)

        self.use_qk_norm = use_qk_norm
        if use_qk_norm:
            self.q_norm = nn.LayerNorm(self.head_dim)
            self.k_norm = nn.LayerNorm(self.head_dim)

        self.compute_pair_bias = compute_pair_bias
        if compute_pair_bias:
            self.proj_z = nn.Sequential(
                nn.LayerNorm(c_z),
                nn.Linear(c_z, num_heads, bias=False),
                Rearrange("b ... h -> b h ..."),
            )
        else:
            self.proj_z = Rearrange("b ... h -> b h ...")

        self.proj_o = nn.Linear(c_s, c_s, bias=False)
        init.final_init_(self.proj_o.weight)

    def forward(
        self,
        s: Tensor,
        z: Tensor,
        mask: Tensor,
        k_in: Tensor,
        multiplicity: int = 1,
    ) -> Tensor:
        """Forward pass.

        Parameters
        ----------
        s : torch.Tensor
            The input sequence tensor (B, S, D)
        z : torch.Tensor
            The input pairwise tensor or bias (B, N, N, D)
        mask : torch.Tensor
            The pairwise mask tensor (B, N, N)

        Returns
        -------
        torch.Tensor
            The output sequence tensor.

        """
        B = s.shape[0]

        # Compute projections
        q = self.proj_q(s).view(B, -1, self.num_heads, self.head_dim)
        k = self.proj_k(k_in).view(B, -1, self.num_heads, self.head_dim)
        v = self.proj_v(k_in).view(B, -1, self.num_heads, self.head_dim)
        """
        TODO
        The k and v part should be done like this instead for efficiency reasons in the next version of boltz
        self.proj_kv = nn.Linear(c_s, 2*c_s, bias=False)
        kv = self.proj_kv(k_in).view(B, -1, self.num_heads, 2*self.head_dim).permute(0, 2, 1, 3)
        k,v = torch.chunk(kv, chunks=2, dim=3) # chunking (B,H,N,2C) into 2x (B,H,N,C)
        """

        if self.use_qk_norm:
            q = self.q_norm(q)
            k = self.k_norm(k)

        bias = self.proj_z(z)
        bias = bias.repeat_interleave(multiplicity, 0)

        g = self.proj_g(s).sigmoid()

        with torch.autocast("cuda", enabled=False):
            # Compute attention weights
            attn = torch.einsum("bihd,bjhd->bhij", q.float(), k.float())
            attn = attn / (self.head_dim**0.5) + bias.float()
            attn = attn + (1 - mask[:, None, None].float()) * -self.inf
            attn = attn.softmax(dim=-1)

            # Compute output
            o = torch.einsum("bhij,bjhd->bihd", attn, v.float()).to(v.dtype)
        o = o.reshape(B, -1, self.c_s)
        o = self.proj_o(g * o)

        return o


class SDPAttentionPairBias(nn.Module):
    """Attention pair bias layer."""

    def __init__(
        self,
        c_s: int,
        c_z: int = None,
        num_heads: int = None,
        inf: float = 1e6,
        compute_pair_bias: bool = True,
        use_qk_norm: bool = False,
    ) -> None:
        """Initialize the attention pair bias layer.

        Parameters
        ----------
        c_s : int
            The input sequence dimension.
        c_z : int
            The input pairwise dimension.
        num_heads : int
            The number of heads.
        inf : float, optional
            The inf value, by default 1e6

        """
        super().__init__()

        assert c_s % num_heads == 0

        self.c_s = c_s
        self.num_heads = num_heads
        self.head_dim = c_s // num_heads
        self.inf = inf

        self.proj_q = nn.Linear(c_s, c_s)
        self.proj_k = nn.Linear(c_s, c_s, bias=False)
        self.proj_v = nn.Linear(c_s, c_s, bias=False)
        self.proj_g = nn.Linear(c_s, c_s, bias=False)

        self.use_qk_norm = use_qk_norm
        if use_qk_norm:
            self.q_norm = nn.LayerNorm(self.head_dim)
            self.k_norm = nn.LayerNorm(self.head_dim)

        self.compute_pair_bias = compute_pair_bias
        if compute_pair_bias:
            self.proj_z = nn.Sequential(
                nn.LayerNorm(c_z),
                nn.Linear(c_z, num_heads, bias=False),
                Rearrange("b ... h -> b h ..."),
            )
        else:
            self.proj_z = Rearrange("b ... h -> b h ...")

        self.proj_o = nn.Linear(c_s, c_s, bias=False)
        init.final_init_(self.proj_o.weight)

    def forward(
        self,
        s: Tensor,
        z: Tensor,
        mask: Tensor,
        k_in: Tensor,
        multiplicity: int = 1,
    ) -> Tensor:
        """Forward pass.

        Parameters
        ----------
        s : torch.Tensor
            The input sequence tensor (B, S, D)
        z : torch.Tensor
            The input pairwise tensor or bias (B, N, N, D)
        mask : torch.Tensor
            The pairwise mask tensor (B, N, N)

        Returns
        -------
        torch.Tensor
            The output sequence tensor.

        """

        B = s.shape[0]

        # Compute projections
        q = (
            self.proj_q(s)
            .view(B, -1, self.num_heads, self.head_dim)
            .permute(0, 2, 1, 3)
        ).contiguous()
        k = (
            self.proj_k(k_in)
            .view(B, -1, self.num_heads, self.head_dim)
            .permute(0, 2, 1, 3)
        ).contiguous()
        v = (
            self.proj_v(k_in)
            .view(B, -1, self.num_heads, self.head_dim)
            .permute(0, 2, 1, 3)
        ).contiguous()

        if self.use_qk_norm:
            q = self.q_norm(q)
            k = self.k_norm(k)

        bias = self.proj_z(z)
        bias = bias.repeat_interleave(multiplicity, 0)
        bias = bias + (1 - mask[:, None, None].float()) * -self.inf

        g = self.proj_g(s).sigmoid()

        with torch.autocast("cuda", enabled=False):
            # Compute attention weights
            o = scaled_dot_product_attention(q, k, v, attn_mask=bias)
        o = o.reshape(B, -1, self.c_s)
        o = self.proj_o(g * o)

        return o


# class FlexAttentionPairBias(nn.Module):
#     """Attention pair bias layer."""

#     def __init__(
#         self,
#         c_s: int,
#         c_z: int = None,
#         num_heads: int = None,
#         inf: float = 1e6,
#         compute_pair_bias: bool = True,
#     ) -> None:
#         """Initialize the attention pair bias layer.

#         Parameters
#         ----------
#         c_s : int
#             The input sequence dimension.
#         c_z : int
#             The input pairwise dimension.
#         num_heads : int
#             The number of heads.
#         inf : float, optional
#             The inf value, by default 1e6

#         """
#         super().__init__()

#         assert c_s % num_heads == 0

#         self.c_s = c_s
#         self.num_heads = num_heads
#         self.head_dim = c_s // num_heads
#         self.inf = inf

#         self.proj_q = nn.Linear(c_s, c_s)
#         self.proj_kv = nn.Linear(c_s, 2 * c_s, bias=False)
#         self.proj_g = nn.Linear(c_s, c_s, bias=False)

#         self.compute_pair_bias = compute_pair_bias
#         if compute_pair_bias:
#             self.proj_z = nn.Sequential(
#                 nn.LayerNorm(c_z),
#                 nn.Linear(c_z, num_heads, bias=False),
#                 Rearrange("b ... h -> b h ..."),
#             )
#         else:
#             self.proj_z = Rearrange("b ... h -> b h ...")

#         self.proj_o = nn.Linear(c_s, c_s, bias=False)
#         init.final_init_(self.proj_o.weight)

#     @torch.compile(fullgraph=True, dynamic=True)
#     def projection_attention_package(
#         self,
#         B: int,
#         q: Tensor,
#         k: Tensor,
#         v: Tensor,
#         score_mod: Callable[[Tensor, Tensor, Tensor, Tensor, Tensor], Tensor],
#     ) -> Tensor:
#         """packaging projection and flex attention"""

#         o = flex_attention(
#             q,
#             k,
#             v,
#             score_mod=score_mod,
#             kernel_options={
#                 "FORCE_USE_FLEX_ATTENTION": True,
#                 "BLOCK_M": 16,
#                 "BLOCK_N": 16,
#                 "BLOCK_K": 8,
#                 "num_stages": 1,
#             },
#         )
#         o = o.to(v.dtype)

#         return o

#     def forward(
#         self,
#         s: Tensor,
#         z: Tensor,
#         mask: Tensor,
#         k_in: Tensor,
#         multiplicity: int = 1,
#     ) -> Tensor:
#         """Forward pass.

#         Parameters
#         ----------
#         s : torch.Tensor
#             The input sequence tensor (B, S, D)
#         z : torch.Tensor
#             The input pairwise tensor or bias (B, N, N, D)
#         mask : torch.Tensor
#             The pairwise mask tensor (B, N, N)

#         Returns
#         -------
#         torch.Tensor
#             The output sequence tensor.

#         """

#         bias = self.proj_z(z)
#         bias = bias.repeat_interleave(multiplicity, 0)
#         bias = bias + (1 - mask[:, None, None].float()) * -self.inf

#         B = s.shape[0]
#         q = (
#             self.proj_q(s)
#             .view(B, -1, self.num_heads, self.head_dim)
#             .permute(0, 2, 1, 3)
#             .contiguous()
#         )
#         kv = (
#             self.proj_kv(k_in)
#             .view(B, -1, 2 * self.num_heads, self.head_dim)
#             .permute(0, 2, 1, 3)
#             .contiguous()
#         )
#         k, v = torch.chunk(kv, chunks=2, dim=1)
#         print(q.shape, k.shape, v.shape, B, self.num_heads, self.head_dim, bias.shape, multiplicity)
#         print(bias[:10,:2,0,0])

#         def score_mod(
#             score: Tensor, batch: Tensor, head: Tensor, q_idx: Tensor, k_idx: Tensor
#         ) -> Tensor:
#             return score + bias[batch, head, q_idx, k_idx]

#         with torch.autocast("cuda", enabled=False):
#             o = self.projection_attention_package(B, q, k, v, score_mod)
#         o = o.reshape(B, -1, self.c_s)
#         g = self.proj_g(s).sigmoid()
#         o = self.proj_o(g * o)

#         return o


class AttentionNoPairBias(nn.Module):
    """Attention without pair bias layer."""

    def __init__(
        self,
        c_s: int,
        num_heads: int,
        inf: float = 1e6,
        global_mask: bool = False,
        use_qk_norm: bool = False,
    ) -> None:
        """Initialize the attention layer.

        Parameters
        ----------
        c_s : int
            The input sequence dimension.
        num_heads : int
            The number of heads.
        inf : float, optional
            The inf value, by default 1e6

        """
        super().__init__()

        assert c_s % num_heads == 0

        self.c_s = c_s
        self.num_heads = num_heads
        self.head_dim = c_s // num_heads
        self.inf = inf
        self.global_mask = global_mask
        self.proj_q = nn.Linear(c_s, c_s)
        self.proj_k = nn.Linear(c_s, c_s, bias=False)
        self.proj_v = nn.Linear(c_s, c_s, bias=False)
        self.proj_g = nn.Linear(c_s, c_s, bias=False)

        self.use_qk_norm = use_qk_norm
        if use_qk_norm:
            self.q_norm = nn.LayerNorm(self.head_dim)
            self.k_norm = nn.LayerNorm(self.head_dim)

        self.proj_o = nn.Linear(c_s, c_s, bias=False)
        init.final_init_(self.proj_o.weight)

    def forward(self, s: Tensor, mask: Tensor, k_in: Tensor) -> Tensor:
        """Forward pass.

        Parameters
        ----------
        s : torch.Tensor
            The input sequence tensor (B, S, D)
        z : torch.Tensor
            The input pairwise tensor (B, N, N, D)
        mask : torch.Tensor
            The pairwise mask tensor (B, N, N)

        Returns
        -------
        torch.Tensor
            The output sequence tensor.

        """
        B = s.shape[0]

        # Compute projections
        q = self.proj_q(s).view(B, -1, self.num_heads, self.head_dim)
        k = self.proj_k(k_in).view(B, -1, self.num_heads, self.head_dim)
        v = self.proj_v(k_in).view(B, -1, self.num_heads, self.head_dim)
        """
        TODO
        The k and v part should be done like this instead for efficiency reasons in the next version of boltz
        self.proj_kv = nn.Linear(c_s, 2*c_s, bias=False)
        kv = self.proj_kv(k_in).view(B, -1, self.num_heads, 2*self.head_dim).permute(0, 2, 1, 3)
        k,v = torch.chunk(kv, chunks=2, dim=3) # chunking (B,H,N,2C) into 2x (B,H,N,C)
        """

        if self.use_qk_norm:
            q = self.q_norm(q)
            k = self.k_norm(k)

        g = self.proj_g(s).sigmoid()

        with torch.autocast("cuda", enabled=False):
            # Compute attention weights
            attn = torch.einsum("bihd,bjhd->bhij", q.float(), k.float())
            attn = attn / (self.head_dim**0.5)
            if self.global_mask:
                attn = attn + (1 - mask[None, None, :].float()) * -self.inf
            else:
                attn = attn + (1 - mask[:, None, None].float()) * -self.inf
            attn = attn.softmax(dim=-1)

            # Compute output
            o = torch.einsum("bhij,bjhd->bihd", attn, v.float()).to(v.dtype)
        o = o.reshape(B, -1, self.c_s)
        o = self.proj_o(g * o)

        return o


class CrossAttention(nn.Module):
    def __init__(
        self,
        c_s: int,
        c_z: int = None,
        num_heads: int = None,
        inf: float = 1e6,
        compute_pair_bias: bool = True,
    ):
        super().__init__()
        self.c_s = c_s
        self.c_z = c_z
        self.num_heads = num_heads
        self.head_dim = c_s // num_heads
        self.inf = inf
        self.compute_pair_bias = compute_pair_bias
        self.proj_q = nn.Linear(c_s, c_s)
        self.proj_k = nn.Linear(c_s, c_s, bias=False)
        self.proj_v = nn.Linear(c_s, c_s, bias=False)
        self.proj_g = nn.Linear(c_s, c_s, bias=False)
        self.proj_o = nn.Linear(c_s, c_s, bias=False)
        init.final_init_(self.proj_o.weight)

    def forward(
        self,
        s,
        k_in,
        mask,
        bias=None,
        multiplicity=1,
    ):
        B = s.shape[0]
        q = self.proj_q(s).view(B, -1, self.num_heads, self.head_dim)
        k = self.proj_k(k_in).view(B, -1, self.num_heads, self.head_dim)
        v = self.proj_v(k_in).view(B, -1, self.num_heads, self.head_dim)

        if bias is not None:
            bias = self.proj_z(bias)
            bias = bias.repeat_interleave(multiplicity, 0)
            bias = bias + (1 - mask[:, None, None].float()) * -self.inf

        g = self.proj_g(s).sigmoid()
        with torch.autocast("cuda", enabled=False):
            attn = torch.einsum("bihd, bjhd->bhij", q.float(), k.float())
            attn = (
                attn / self.head_dim**0.5 + bias.float()
                if bias is not None
                else attn / self.head_dim**0.5
            )
            attn = attn.softmax(dim=-1)
            o = torch.einsum("bhij,bjhd->bihd", attn, v.float()).to(v.dtype)
        o = o.reshape(B, -1, self.c_s)
        o = self.proj_o(g * o)
        return o
