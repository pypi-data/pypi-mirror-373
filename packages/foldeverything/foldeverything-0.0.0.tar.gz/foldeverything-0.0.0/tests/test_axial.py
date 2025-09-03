import time

import pandas as pd
import torch
import triton
from profiling import clear_memory, current_memory, memory_measure
from torch import nn
from torch.nn.attention import SDPBackend, sdpa_kernel
from torch.nn.functional import scaled_dot_product_attention


class MiniAxialAttention(nn.Module):
    """A bi-directional axial Flash-attention layer."""

    def __init__(
        self,
        dim: int,
        hidden: int,
        no_heads: int,
        backend: SDPBackend = SDPBackend.FLASH_ATTENTION,
    ) -> None:
        """Initialize the MiniAxialAttention layer.

        Parameters
        ----------
        dim: int
            Input dimension
        hidden: int
            Per-head hidden dimension
        no_heads: int
            Number of attention heads

        """
        super().__init__()

        self.dim = dim
        self.hidden = hidden
        self.no_heads = no_heads
        self.backend = backend

        qkv_dim = 3 * self.hidden * self.no_heads
        out_dim = 2 * self.hidden * self.no_heads

        self.norm = nn.LayerNorm(self.dim)
        self.linear_qkv1 = nn.Linear(self.dim, qkv_dim, bias=False)
        self.linear_qkv2 = nn.Linear(self.dim, qkv_dim, bias=False)
        self.linear_o = nn.Linear(out_dim, self.dim, bias=False)
        self.linear_g = nn.Linear(out_dim, self.dim, bias=False)

    def attention(self, qkv: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
        """Apply self-attention to the input tensor.

        Parameters
        ----------
        qkv: torch.Tensor
            Input data of shape (batch, seq_len, seq_len, dim)
        slen: torch.Tensor
            Sequence lengths of shape (batch,)

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

        # Only enable specific backend
        with sdpa_kernel(self.backend):
            o = scaled_dot_product_attention(q, k, v, attn_mask=mask)

        # Convert back to dense tensor
        o = o.transpose(-2, -3).contiguous()
        o = o.view(bs, slen1, slen2, -1)

        # Convert back to original dtype
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


# Set hyperparameters
C_Z = 128
BATCH_SIZE = 1
SEQ_LEN = [64, 128, 256, 512]
PRECISION = torch.bfloat16
device = "cuda:0"
torch.set_grad_enabled(True)

# Preload modules
default = MiniAxialAttention(C_Z, C_Z // 4, 4, backend=SDPBackend.MATH)
default.cuda()

efficient = MiniAxialAttention(C_Z, C_Z // 4, 4, backend=SDPBackend.EFFICIENT_ATTENTION)
efficient.cuda()

flash = MiniAxialAttention(C_Z, C_Z // 4, 4, backend=SDPBackend.EFFICIENT_ATTENTION)
flash.cuda()

cudnn = MiniAxialAttention(C_Z, C_Z // 4, 4, backend=SDPBackend.CUDNN_ATTENTION)
cudnn.cuda()
cudnn = torch.compile(cudnn, fullgraph=True, dynamic=False)


def backward(model, z, pair_mask):
    out = model(z, pair_mask)
    out.sum().backward()
    model.zero_grad()


def speed(func, its=10, warmup=10):
    for _ in range(warmup):
        func()
    torch.cuda.synchronize()
    start = time.time()
    for _ in range(its):
        func()
    torch.cuda.synchronize()
    time_a = time.time() - start
    time_a /= its
    return time_a


# Full model
@triton.testing.perf_report(
    triton.testing.Benchmark(
        x_names=["size"],
        x_vals=SEQ_LEN,
        line_arg="provider",  # Argument name whose value corresponds to a different line in the plot.
        line_vals=[
            "Default",
            "Flash",
            "Efficient",
            "Cudnn",
        ],  # Possible values for `line_arg`.
        line_names=[
            "Default",
            "Flash",
            "Efficient",
            "Cudnn",
        ],  # Label name for the lines.
        plot_name="performance",  # Name for the plot. Used also as a file name for saving the plot.
        args={},  # Values for function arguments not in `x_names` and `y_name`.
    )
)
def benchmark(size, provider):
    clear_memory(device)

    # Now run the benchmark
    z = torch.randn(
        (BATCH_SIZE, size, size, C_Z),
        device=device,
        dtype=PRECISION,
        requires_grad=False,
    )
    pair_mask = torch.ones(
        (BATCH_SIZE, size, size),
        device=device,
        dtype=PRECISION,
        requires_grad=False,
    ).bool()

    if provider == "Cudnn":
        pair_mask = pair_mask.unsqueeze(1)

    with torch.autocast("cuda", dtype=PRECISION):
        if provider == "Default":
            ms = speed(lambda: backward(default, z, pair_mask))
        elif provider == "Flash":
            ms = speed(lambda: backward(flash, z, pair_mask))
        elif provider == "Efficient":
            ms = speed(lambda: backward(efficient, z, pair_mask))
        elif provider == "Cudnn":
            ms = speed(lambda: backward(cudnn, z, pair_mask))

    # Compute throughput in sequences per second
    return ms / BATCH_SIZE


print("Speed")
benchmark.run(print_data=True, show_plots=False)

start_mem = current_memory(device)

df = []
for size in SEQ_LEN:
    print(size)
    z = torch.randn(
        (BATCH_SIZE, size, size, C_Z),
        device=device,
        dtype=PRECISION,
        requires_grad=False,
    )
    pair_mask = torch.ones(
        (BATCH_SIZE, size, size),
        device=device,
        dtype=PRECISION,
        requires_grad=False,
    ).bool()

    with torch.autocast("cuda", dtype=PRECISION):
        memory_default = memory_measure(
            lambda: backward(default, z, pair_mask), device=device
        )
        memory_efficient = memory_measure(
            lambda: backward(efficient, z, pair_mask), device=device
        )
        memory_flash = memory_measure(
            lambda: backward(flash, z, pair_mask), device=device
        )
        memory_cudnn = memory_measure(
            lambda: backward(cudnn, z, pair_mask.unsqueeze(1)), device=device
        )
        df.append(
            {
                "size": size,
                "Default": memory_default - start_mem,
                "Efficient": memory_efficient - start_mem,
                "Flash": memory_flash - start_mem,
                "Cudnn": memory_cudnn - start_mem,
            }
        )

df = pd.DataFrame(df)
print("Memory")
print(df)
