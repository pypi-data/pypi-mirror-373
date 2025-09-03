import torch
from torch import nn
from torch.nn.attention import SDPBackend, sdpa_kernel
from torch.nn.functional import scaled_dot_product_attention

from foldeverything.model.layers import initialize as init



class SamplesAxialAttention(nn.Module):

    def __init__(self, dim: int, hidden: int, no_heads: int, pair: bool) -> None:
        """Initialize the SamplesAxialAttention layer.
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
        self.pair = pair

        qkv_dim = 3 * self.hidden * self.no_heads
        out_dim = self.hidden * self.no_heads

        self.norm = nn.LayerNorm(self.dim)
        self.linear_qkv = nn.Linear(self.dim, qkv_dim, bias=False)
        self.linear_o = nn.Linear(out_dim, self.dim, bias=False)
        self.linear_g = nn.Linear(out_dim, self.dim, bias=False)

        init.bias_init_one_(self.norm.weight)
        init.bias_init_zero_(self.norm.bias)

        init.glorot_uniform_init_(self.linear_qkv.weight)

        init.final_init_(self.linear_o.weight)
        init.gating_init_(self.linear_g.weight)

    def samples_z_axial_attention(
            self,
            qkv: torch.Tensor,
            mask: torch.Tensor,
            multiplicity: int,
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
        bs, slen1, slen2, d = qkv.shape
        qkv = qkv.view(bs // multiplicity, multiplicity, slen1, slen2, self.no_heads, d // self.no_heads)
        qkv = qkv.permute(0, 2, 3, 1, 4, 5)
        qkv = qkv.reshape((bs // multiplicity) * slen1 * slen2, multiplicity, self.no_heads, -1)
        q, k, v = qkv.chunk(3, dim=-1)

        q = q.transpose(-2, -3)
        k = k.transpose(-2, -3)
        v = v.transpose(-2, -3)

        # Expand mask
        mask = mask.view(bs // multiplicity, multiplicity, slen1, slen2, 1).permute(0, 2, 3, 1, 4) \
            .expand(-1, -1, -1, -1, multiplicity)
        mask = mask.view(bs // multiplicity * slen1 * slen2, 1, multiplicity, multiplicity)

        # Only enable specific backend
        with sdpa_kernel(backends=[SDPBackend.MATH]):
            o = scaled_dot_product_attention(q, k, v, attn_mask=mask)

        # Convert back to dense tensor
        o = o.transpose(-2, -3).contiguous()
        o = o.view(bs // multiplicity, slen1, slen2, multiplicity, -1).permute(0, 3, 1, 2, 4).reshape(bs, slen1, slen2, -1)
        return o

    def samples_s_axial_attention(
            self,
            qkv: torch.Tensor,
            mask: torch.Tensor,
            multiplicity: int,
    ) -> torch.Tensor:
        """Apply self-attention to the input tensor.

        Parameters
        ----------
        qkv: torch.Tensor
            Input data of shape (batch, seq_len, dim)
        mask: torch.Tensor
            Masking tensor of shape (batch, seq_len)

        Returns
        -------
        torch.Tensor
            Output data of shape (batch, seq_len, dim)

        """
        # Compute Q, K, V
        bs, slen, d = qkv.shape
        qkv = qkv.view(bs // multiplicity, multiplicity, slen, self.no_heads, d // self.no_heads)
        qkv = qkv.permute(0, 2, 1, 3, 4)
        qkv = qkv.reshape((bs // multiplicity) * slen, multiplicity, self.no_heads, -1)
        q, k, v = qkv.chunk(3, dim=-1)

        q = q.transpose(-2, -3)
        k = k.transpose(-2, -3)
        v = v.transpose(-2, -3)

        # Expand mask
        mask = mask.view(bs // multiplicity, multiplicity, slen, 1).permute(0, 2, 1, 3).expand(-1, -1, -1, multiplicity)
        mask = mask.view(bs // multiplicity * slen, 1, multiplicity, multiplicity)

        # Only enable specific backend
        with sdpa_kernel(backends=[SDPBackend.MATH]):
            o = scaled_dot_product_attention(q, k, v, attn_mask=mask)

        # Convert back to dense tensor
        o = o.transpose(-2, -3).contiguous()
        o = o.view(bs // multiplicity, slen, multiplicity, -1).permute(0, 2, 1, 3).reshape(bs, slen, -1)
        return o

    def forward(
        self,
        x: torch.Tensor,
        mask: torch.Tensor,
        multiplicity: int,
    ) -> torch.Tensor:
        """Forward pass through the BiFlashAttention layer.

        Parameters
        ----------
        z: torch.Tensor
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

        # Attention
        if self.pair:
            o = self.samples_z_axial_attention(self.linear_qkv(x), mask, multiplicity)
        else:
            o = self.samples_s_axial_attention(self.linear_qkv(x), mask, multiplicity)

        # Output gating
        o = self.linear_o(o) * self.linear_g(o).sigmoid()
        return o
