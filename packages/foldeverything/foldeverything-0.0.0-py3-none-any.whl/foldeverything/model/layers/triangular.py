import torch
from torch import Tensor, nn

from foldeverything.model.layers import initialize as init


class MiniTriangularUpdate(nn.Module):
    """Perform a bi-directional triangular update.

    This module differs from the original multiplicative
    update introduced in AlphaFold2 in several ways. First,
    we merge the incoming and outgoing layers in a single
    update. Second, and related to the  above change, we
    down-project the input to D // 4. This allows us to keep
    memory constant. Third, we modify the output gate to be
    a function of the output instead of the intput, which
    allows us to use the same gating kernel for both the
    input and output gates, and thereby save some more memory.

    """

    def __init__(self, dim: int = 128) -> None:
        """Initialize the TriangularUpdate module.

        Parameters
        ----------
        dim: int
            The dimension of the input, default 128

        """
        super().__init__()

        self.norm_in = nn.LayerNorm(dim, eps=1e-5)
        self.p_in = nn.Linear(dim, dim, bias=False)
        self.g_in = nn.Linear(dim, dim, bias=False)

        self.norm_out = nn.LayerNorm(dim // 2)
        self.p_out = nn.Linear(dim // 2, dim, bias=False)
        self.g_out = nn.Linear(dim // 2, dim, bias=False)

        init.bias_init_one_(self.norm_in.weight)
        init.bias_init_zero_(self.norm_in.bias)

        init.lecun_normal_init_(self.p_in.weight)
        init.gating_init_(self.g_in.weight)

        init.bias_init_one_(self.norm_out.weight)
        init.bias_init_zero_(self.norm_out.bias)

        init.final_init_(self.p_out.weight)
        init.gating_init_(self.g_out.weight)

    def forward(self, x: Tensor, mask: Tensor) -> Tensor:
        """Perform a forward pass.

        Parameters
        ----------
        x: torch.Tensor
            The input data of shape (B, N, N, D)
        mask: torch.Tensor
            The input mask of shape (B, N, N)

        Returns
        -------
        x: torch.Tensor
            The output data of shape (B, N, N, D)

        """
        # Input gating: D -> D
        x = self.norm_in(x)
        x = self.p_in(x) * self.g_in(x).sigmoid()

        # Apply mask
        x = x * mask.unsqueeze(-1)

        # Split input and cast to float
        with torch.autocast("cuda", enabled=False):
            a1, b1, a2, b2 = torch.chunk(x.float(), 4, dim=-1)

            # Triangular projection
            x1 = torch.einsum("bikd,bjkd->bijd", a1, b1)
            x2 = torch.einsum("bkid,bkjd->bijd", a2, b2)

            # Merge outputs
            x = torch.cat([x1, x2], dim=-1).to(x.dtype)

        # Output gating: D / 2 -> D
        x = self.norm_out(x)
        x = self.p_out(x) * self.g_out(x).sigmoid()

        return x


class TriangleMultiplicationOutgoing(nn.Module):
    """TriangleMultiplicationOutgoing."""

    def __init__(self, dim: int = 128) -> None:
        """Initialize the TriangularUpdate module.

        Parameters
        ----------
        dim: int
            The dimension of the input, default 128

        """
        super().__init__()

        self.norm_in = nn.LayerNorm(dim, eps=1e-5)
        self.p_in = nn.Linear(dim, 2 * dim, bias=False)
        self.g_in = nn.Linear(dim, 2 * dim, bias=False)

        self.norm_out = nn.LayerNorm(dim)
        self.p_out = nn.Linear(dim, dim, bias=False)
        self.g_out = nn.Linear(dim, dim, bias=False)

        init.bias_init_one_(self.norm_in.weight)
        init.bias_init_zero_(self.norm_in.bias)

        init.lecun_normal_init_(self.p_in.weight)
        init.gating_init_(self.g_in.weight)

        init.bias_init_one_(self.norm_out.weight)
        init.bias_init_zero_(self.norm_out.bias)

        init.final_init_(self.p_out.weight)
        init.gating_init_(self.g_out.weight)

    def forward(self, x: Tensor, mask: Tensor) -> Tensor:
        """Perform a forward pass.

        Parameters
        ----------
        x: torch.Tensor
            The input data of shape (B, N, N, D)
        mask: torch.Tensor
            The input mask of shape (B, N, N)

        Returns
        -------
        x: torch.Tensor
            The output data of shape (B, N, N, D)

        """
        # Input gating: D -> D
        x = self.norm_in(x)
        x_in = x
        x = self.p_in(x) * self.g_in(x).sigmoid()

        # Apply mask
        x = x * mask.unsqueeze(-1)

        # Split input and cast to float
        with torch.autocast("cuda", enabled=False):
            a, b = torch.chunk(x.float(), 2, dim=-1)

            # Triangular projection
            x = torch.einsum("bikd,bjkd->bijd", a, b).to(x.dtype)

        # Output gating
        x = self.p_out(self.norm_out(x)) * self.g_out(x_in).sigmoid()

        return x


class TriangleMultiplicationIncoming(nn.Module):
    """TriangleMultiplicationIncoming."""

    def __init__(self, dim: int = 128) -> None:
        """Initialize the TriangularUpdate module.

        Parameters
        ----------
        dim: int
            The dimension of the input, default 128

        """
        super().__init__()

        self.norm_in = nn.LayerNorm(dim, eps=1e-5)
        self.p_in = nn.Linear(dim, 2 * dim, bias=False)
        self.g_in = nn.Linear(dim, 2 * dim, bias=False)

        self.norm_out = nn.LayerNorm(dim)
        self.p_out = nn.Linear(dim, dim, bias=False)
        self.g_out = nn.Linear(dim, dim, bias=False)

        init.bias_init_one_(self.norm_in.weight)
        init.bias_init_zero_(self.norm_in.bias)

        init.lecun_normal_init_(self.p_in.weight)
        init.gating_init_(self.g_in.weight)

        init.bias_init_one_(self.norm_out.weight)
        init.bias_init_zero_(self.norm_out.bias)

        init.final_init_(self.p_out.weight)
        init.gating_init_(self.g_out.weight)

    def forward(self, x: Tensor, mask: Tensor) -> Tensor:
        """Perform a forward pass.

        Parameters
        ----------
        x: torch.Tensor
            The input data of shape (B, N, N, D)
        mask: torch.Tensor
            The input mask of shape (B, N, N)

        Returns
        -------
        x: torch.Tensor
            The output data of shape (B, N, N, D)

        """
        # Input gating: D -> D
        x = self.norm_in(x)
        x_in = x
        x = self.p_in(x) * self.g_in(x).sigmoid()

        # Apply mask
        x = x * mask.unsqueeze(-1)

        # Split input and cast to float
        with torch.autocast("cuda", enabled=False):
            a, b = torch.chunk(x.float(), 2, dim=-1)

            # Triangular projection
            x = torch.einsum("bkid,bkjd->bijd", a, b).to(x.dtype)

        # Output gating
        x = self.p_out(self.norm_out(x)) * self.g_out(x_in).sigmoid()

        return x
