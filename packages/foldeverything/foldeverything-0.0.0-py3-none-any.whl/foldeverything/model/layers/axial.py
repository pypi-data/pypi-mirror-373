import torch
from torch import nn
from torch.nn.attention import SDPBackend, sdpa_kernel
from torch.nn.functional import scaled_dot_product_attention

from foldeverything.model.layers import initialize as init


class MiniAxialAttention(nn.Module):
    """A bi-directional axial Flash-attention layer."""

    def __init__(self, dim: int, hidden: int, no_heads: int) -> None:
        """Initialize the MiniAxialAttention layer.

        Parameters
        ----------
        dim: int
            Input dimension
        hidden: int
            Per-head hidden dimension
        no_heads: int
            Number of attention heads
        gating: bool, optional
            Whether the output should be gated using query data

        """
        super().__init__()

        self.dim = dim
        self.hidden = hidden
        self.no_heads = no_heads

        qkv_dim = 3 * self.hidden * self.no_heads
        out_dim = 2 * self.hidden * self.no_heads

        self.norm = nn.LayerNorm(self.dim)
        self.linear_qkv1 = nn.Linear(self.dim, qkv_dim, bias=False)
        self.linear_qkv2 = nn.Linear(self.dim, qkv_dim, bias=False)
        self.linear_o = nn.Linear(out_dim, self.dim, bias=False)
        self.linear_g = nn.Linear(out_dim, self.dim, bias=False)

        init.bias_init_one_(self.norm.weight)
        init.bias_init_zero_(self.norm.bias)

        init.glorot_uniform_init_(self.linear_qkv1.weight)
        init.glorot_uniform_init_(self.linear_qkv2.weight)

        init.final_init_(self.linear_o.weight)
        init.gating_init_(self.linear_g.weight)

    def attention(
        self,
        qkv: torch.Tensor,
        mask: torch.Tensor,
    ) -> torch.Tensor:
        """Apply self-attention to the input tensor.

        Parameters
        ----------
        qkv: torch.Tensor
            Input data of shape (batch, seq_len, seq_len, dim)
        mask: torch.Tensor
            Masking tensor of shape (batch, seq_len, seq_len)

        Returns
        -------
        torch.Tensor
            Output data of shape (batch, seq_len, seq_len, dim)

        """
        # Compute Q, K, V
        bs, slen1, slen2, _ = qkv.shape
        qkv = qkv.view(bs * slen1, slen2, self.no_heads, -1)
        q, k, v = qkv.chunk(3, dim=-1)

        q = q.transpose(-2, -3)
        k = k.transpose(-2, -3)
        v = v.transpose(-2, -3)

        # Expand mask (can't expand without copying for bs > 1)
        mask = mask.unsqueeze(1).expand(-1, slen1, -1, -1)
        mask = mask.contiguous().view(bs * slen1, 1, slen2, slen2)

        # Only enable specific backend
        with sdpa_kernel(SDPBackend.EFFICIENT_ATTENTION):
            o = scaled_dot_product_attention(q, k, v, attn_mask=mask)

        # Convert back to dense tensor
        o = o.transpose(-2, -3).contiguous()
        o = o.view(bs, slen1, slen2, -1)
        return o

    def forward(
        self,
        x: torch.Tensor,
        mask: torch.Tensor,
    ) -> torch.Tensor:
        """Forward pass through the BiFlashAttention layer.

        Parameters
        ----------
        x: torch.Tensor
            Input data of shape (batch, seq_len, seq_len, dim)
        mask: torch.Tensor
            Masking tensor of shape (batch, seq_len, seq_len)

        Returns
        -------
        torch.Tensor
            Output data of shape (batch, seq_len, seq_len, dim)

        """
        # Input normalization
        x = self.norm(x)

        # Outgoing attention
        o = self.attention(self.linear_qkv1(x), mask)

        # Incoming attention
        x = x.transpose(1, 2)
        o2 = self.attention(self.linear_qkv2(x), mask)
        o2 = o2.transpose(1, 2)

        # Output gating
        o = torch.cat([o, o2], dim=-1)
        o = self.linear_o(o) * self.linear_g(o).sigmoid()
        return o


class AxialAttentionStart(nn.Module):
    """A axial Flash-attention layer."""

    def __init__(self, dim: int, hidden: int, no_heads: int) -> None:
        """Initialize the MiniAxialAttention layer.

        Parameters
        ----------
        dim: int
            Input dimension
        hidden: int
            Per-head hidden dimension
        no_heads: int
            Number of attention heads
        gating: bool, optional
            Whether the output should be gated using query data

        """
        super().__init__()

        self.dim = dim
        self.hidden = hidden
        self.no_heads = no_heads

        qkv_dim = 3 * self.hidden * self.no_heads
        out_dim = 2 * self.hidden * self.no_heads

        self.norm = nn.LayerNorm(self.dim)
        self.linear_qkv = nn.Linear(self.dim, qkv_dim, bias=False)
        self.linear_o = nn.Linear(out_dim, self.dim, bias=False)
        self.linear_g = nn.Linear(out_dim, self.dim, bias=False)

        init.bias_init_one_(self.norm.weight)
        init.bias_init_zero_(self.norm.bias)
        init.glorot_uniform_init_(self.linear_qkv.weight)
        init.final_init_(self.linear_o.weight)
        init.gating_init_(self.linear_g.weight)

    def attention(
        self,
        qkv: torch.Tensor,
        mask: torch.Tensor,
    ) -> torch.Tensor:
        """Apply self-attention to the input tensor.

        Parameters
        ----------
        qkv: torch.Tensor
            Input data of shape (batch, seq_len, seq_len, dim)
        mask: torch.Tensor
            Masking tensor of shape (batch, seq_len, seq_len)

        Returns
        -------
        torch.Tensor
            Output data of shape (batch, seq_len, seq_len, dim)

        """
        # Compute Q, K, V
        bs, slen1, slen2, _ = qkv.shape
        qkv = qkv.view(bs * slen1, slen2, self.no_heads, -1)
        q, k, v = qkv.chunk(3, dim=-1)

        q = q.transpose(-2, -3)
        k = k.transpose(-2, -3)
        v = v.transpose(-2, -3)

        # Expand mask (can't expand without copying for bs > 1)
        mask = mask.unsqueeze(1).expand(-1, slen1, -1, -1)
        mask = mask.contiguous().view(bs * slen1, 1, slen2, slen2)

        # Only enable specific backend
        with sdpa_kernel(SDPBackend.EFFICIENT_ATTENTION):
            o = scaled_dot_product_attention(q, k, v, attn_mask=mask)

        # Convert back to dense tensor
        o = o.transpose(-2, -3).contiguous()
        o = o.view(bs, slen1, slen2, -1)
        return o

    def forward(
        self,
        x: torch.Tensor,
        mask: torch.Tensor,
    ) -> torch.Tensor:
        """Forward pass through the BiFlashAttention layer.

        Parameters
        ----------
        x: torch.Tensor
            Input data of shape (batch, seq_len, seq_len, dim)
        mask: torch.Tensor
            Masking tensor of shape (batch, seq_len, seq_len)

        Returns
        -------
        torch.Tensor
            Output data of shape (batch, seq_len, seq_len, dim)

        """
        # Input normalization
        x = self.norm(x)

        # Outgoing attention
        o = self.attention(self.linear_qkv(x), mask)

        # Output gating
        o = self.linear_o(o) * self.linear_g(o).sigmoid()
        return o


class AxialAttentionEnd(AxialAttentionStart):
    """A axial Flash-attention layer."""

    def forward(
        self,
        x: torch.Tensor,
        mask: torch.Tensor,
    ) -> torch.Tensor:
        """Forward pass through the BiFlashAttention layer.

        Parameters
        ----------
        x: torch.Tensor
            Input data of shape (batch, seq_len, seq_len, dim)
        mask: torch.Tensor
            Masking tensor of shape (batch, seq_len, seq_len)

        Returns
        -------
        torch.Tensor
            Output data of shape (batch, seq_len, seq_len, dim)

        """
        # Input normalization
        x = self.norm(x)

        # Incoming attention
        x = x.transpose(1, 2)
        o2 = self.attention(self.linear_qkv(x), mask)
        o2 = o2.transpose(1, 2)

        # Output gating
        o = self.linear_o(o) * self.linear_g(o).sigmoid()
        return o
