import torch
import torch.nn.functional as F
import triton
import triton.language as tl
import gc


@triton.autotune(
    configs=[triton.Config({}, num_warps=4, num_stages=2)],
    key=["C1", "C2"],
)
@triton.jit
def fwd_kernel(
    X_ptr,
    W1_ptr,
    W2_ptr,
    W3_ptr,
    O_ptr,
    M: tl.constexpr,
    C1: tl.constexpr,
    C2: tl.constexpr,
    BLOCK_SIZE_M: tl.constexpr,
    BLOCK_SIZE_C2: tl.constexpr,
):
    # Get program id
    pid_m = tl.program_id(0)

    # Create block pointers
    x_block_ptr = tl.make_block_ptr(
        base=X_ptr,
        shape=(M, C1),
        strides=(C1, 1),
        offsets=(pid_m * BLOCK_SIZE_M, 0),
        block_shape=(BLOCK_SIZE_M, C1),
        order=(1, 0),
    )

    w1_block_ptr = tl.make_block_ptr(
        base=W1_ptr,
        shape=(C1, C2),
        strides=(C2, 1),
        offsets=(0, 0),
        block_shape=(C1, BLOCK_SIZE_C2),
        order=(1, 0),
    )

    w2_block_ptr = tl.make_block_ptr(
        base=W2_ptr,
        shape=(C1, C2),
        strides=(C2, 1),
        offsets=(0, 0),
        block_shape=(C1, BLOCK_SIZE_C2),
        order=(1, 0),
    )

    w3_block_ptr = tl.make_block_ptr(
        base=W3_ptr,
        shape=(C2, C1),
        strides=(C1, 1),
        offsets=(0, 0),
        block_shape=(BLOCK_SIZE_C2, C1),
        order=(1, 0),
    )

    o_block_ptr = tl.make_block_ptr(
        base=O_ptr,
        shape=(M, C1),
        strides=(C1, 1),
        offsets=(pid_m * BLOCK_SIZE_M, 0),
        block_shape=(BLOCK_SIZE_M, C1),
        order=(1, 0),
    )

    # Load data
    x = tl.load(x_block_ptr)
    dtype = x.dtype

    # Compute output
    accum_x = tl.zeros((BLOCK_SIZE_M, C1), dtype=tl.float32)
    for _ in range(0, tl.cdiv(C2, BLOCK_SIZE_C2)):
        # Compute swish
        w = tl.load(w1_block_ptr).to(dtype)
        h = tl.dot(x, w, allow_tf32=False)
        h *= tl.sigmoid(h)

        # Compute linear
        w = tl.load(w2_block_ptr).to(dtype)
        h *= tl.dot(x, w, allow_tf32=False)
        h = h.to(dtype)

        # Compute output
        w = tl.load(w3_block_ptr).to(dtype)
        accum_x += tl.dot(h, w, allow_tf32=False)

        # Advance pointers
        w1_block_ptr = tl.advance(w1_block_ptr, (0, BLOCK_SIZE_C2))
        w2_block_ptr = tl.advance(w2_block_ptr, (0, BLOCK_SIZE_C2))
        w3_block_ptr = tl.advance(w3_block_ptr, (BLOCK_SIZE_C2, 0))

    # Store output
    accum_x = accum_x.to(dtype)
    tl.store(o_block_ptr, accum_x)


@triton.jit
def bwd_kernel(
    DX_ptr,
    DO_ptr,
    X_ptr,
    W1_ptr,
    W2_ptr,
    W3_ptr,
    DW1_ptr,
    DW2_ptr,
    DW3_ptr,
    M: tl.constexpr,
    C1: tl.constexpr,
    C2: tl.constexpr,
    BLOCK_SIZE_M: tl.constexpr,
    BLOCK_SIZE_C2: tl.constexpr,
):
    # TODO: Implement backward pass kernel
    pass


class TransitionFunction(torch.autograd.Function):
    @staticmethod
    def forward(ctx, X, W1, W2, W3):
        # Save inputs for backward
        ctx.save_for_backward(X, W1, W2, W3)

        B, N1, N2, C1 = X.shape
        M = B * N1 * N2
        C2 = W1.shape[1]

        X = X.contiguous()
        O = torch.empty_like(X)

        BLOCK_SIZE_M = 128
        BLOCK_SIZE_C2 = 32

        assert M > BLOCK_SIZE_M
        assert M % BLOCK_SIZE_M == 0
        assert C1 <= 128

        grid = lambda META: (triton.cdiv(M, BLOCK_SIZE_M),)
        fwd_kernel[grid](
            X,
            W1,
            W2,
            W3,
            O,
            M,
            C1,
            C2,
            BLOCK_SIZE_M,
            BLOCK_SIZE_C2,
        )
        return O

    @staticmethod
    def backward(ctx, grad_output):
        x, w1, w2, w3 = ctx.saved_tensors
        grad_x = grad_w1 = grad_w2 = grad_w3 = None

        # For now, use PyTorch's autograd as placeholder
        # This will be replaced with the backward kernel implementation
        with torch.enable_grad():
            x_temp = x.detach().requires_grad_()
            w1_temp = w1.detach().requires_grad_()
            w2_temp = w2.detach().requires_grad_()
            w3_temp = w3.detach().requires_grad_()

            # Compute forward
            h1 = F.linear(x_temp, w1_temp.t(), None)
            h1 = h1 * torch.sigmoid(h1)
            h2 = F.linear(x_temp, w2_temp.t(), None)
            h = h1 * h2
            output = F.linear(h, w3_temp.t(), None)

            # Compute gradients
            output.backward(grad_output)

            grad_x = x_temp.grad
            grad_w1 = w1_temp.grad
            grad_w2 = w2_temp.grad
            grad_w3 = w3_temp.grad

        return grad_x, grad_w1, grad_w2, grad_w3


# ---------------- TESTS ----------------#


def fused(x, W1, W2, W3):
    return TransitionFunction.apply(x, W1, W2, W3)


def unfused(x, W1, W2, W3):
    h1 = F.linear(x, W1, None)
    h1 = h1 * torch.sigmoid(h1)  # Swish activation
    h2 = F.linear(x, W2, None)
    h = h1 * h2
    x = F.linear(h, W3, None)
    return x


@torch.compile
def compiled(x, W1, W2, W3):
    h1 = F.linear(x, W1, None)
    h1 = h1 * torch.sigmoid(h1)  # Swish activation
    h2 = F.linear(x, W2, None)
    h = h1 * h2
    x = F.linear(h, W3, None)
    return x


def create_input(device, dtype=torch.float32, grad=False, size=256):
    B = 1
    C = 128
    H = C * 4
    N = size

    x = 0.1 * torch.randn((B, N, N, C), device=device, dtype=dtype)
    W1 = 0.1 * torch.randn((C, H), device=device, dtype=dtype)
    W2 = 0.1 * torch.randn((C, H), device=device, dtype=dtype)
    W3 = 0.1 * torch.randn((H, C), device=device, dtype=dtype)

    x.requires_grad = grad
    W1.requires_grad = grad
    W2.requires_grad = grad
    W3.requires_grad = grad

    return x, W1, W2, W3


def is_close(a, b, tol=1e-5):
    return ((a - b).abs().mean() / b.abs().mean()).item() < tol


def check_forward(f1, f2, device):
    # Initialize inputs
    x, W1, W2, W3 = create_input(device, dtype=torch.float32, grad=False)

    # Run forward
    y1 = f1(x, W1, W2, W3)
    y2 = f2(x, W1.t(), W2.t(), W3.t())

    # Check correctness
    if not is_close(y1, y2):
        print("Forward failed")
        return False
    return True


def check_backward(device):
    # Initialize inputs with gradients
    x, W1, W2, W3 = create_input(device, dtype=torch.float32, grad=True)
    grad_output = torch.randn_like(x)

    # Compute gradients with fused implementation
    y1 = fused(x, W1, W2, W3)
    y1.backward(grad_output)
    dx1, dw1_1, dw2_1, dw3_1 = x.grad, W1.grad, W2.grad, W3.grad

    # Clear gradients
    x.grad, W1.grad, W2.grad, W3.grad = None, None, None, None

    # Compute gradients with unfused implementation
    y2 = unfused(x, W1.t(), W2.t(), W3.t())
    y2.backward(grad_output)
    dx2, dw1_2, dw2_2, dw3_2 = x.grad, W1.grad, W2.grad, W3.grad

    # Check gradient correctness
    checks = [
        is_close(dx1, dx2),
        is_close(dw1_1, dw1_2),
        is_close(dw2_1, dw2_2),
        is_close(dw3_1, dw3_2),
    ]

    if not all(checks):
        print("Backward failed")
        return False
    return True


@triton.testing.perf_report(
    triton.testing.Benchmark(
        x_names=["size"],
        x_vals=[2**i for i in range(5, 13)],
        line_arg="provider",
        line_vals=[
            "triton-fwd",
            "triton-fwd-bwd",
            "torch-fwd",
            "torch-fwd-bwd",
            "torch-compile-fwd",
            "torch-compile-fwd-bwd",
        ],
        line_names=[
            "Triton (fwd)",
            "Triton (fwd+bwd)",
            "Torch (fwd)",
            "Torch (fwd+bwd)",
            "Torch-compile (fwd)",
            "Torch-compile (fwd+bwd)",
        ],
        plot_name="performance",
        args={},
    )
)
def benchmark(size, provider):
    # Create inputs for forward only
    x_fwd, W1_fwd, W2_fwd, W3_fwd = create_input(
        "cuda", dtype=torch.bfloat16, grad=False, size=size
    )

    # Create inputs for forward + backward
    x_bwd, W1_bwd, W2_bwd, W3_bwd = create_input(
        "cuda", dtype=torch.bfloat16, grad=True, size=size
    )
    grad_output = torch.randn_like(x_bwd)

    def run_fwd_bwd():
        y = provider_fn(x_bwd, W1_bwd, W2_bwd, W3_bwd)
        y.backward(grad_output)
        torch.cuda.synchronize()

    if provider == "triton-fwd":
        ms = triton.testing.do_bench(lambda: fused(x_fwd, W1_fwd, W2_fwd, W3_fwd))
    elif provider == "triton-fwd-bwd":
        provider_fn = fused
        ms = triton.testing.do_bench(run_fwd_bwd)
    elif provider == "torch-fwd":
        W1_fwd = W1_fwd.t().contiguous()
        W2_fwd = W2_fwd.t().contiguous()
        W3_fwd = W3_fwd.t().contiguous()
        ms = triton.testing.do_bench(lambda: unfused(x_fwd, W1_fwd, W2_fwd, W3_fwd))
    elif provider == "torch-fwd-bwd":
        W1_bwd = W1_bwd.t().contiguous()
        W2_bwd = W2_bwd.t().contiguous()
        W3_bwd = W3_bwd.t().contiguous()
        provider_fn = unfused
        ms = triton.testing.do_bench(run_fwd_bwd)
    elif provider == "torch-compile-fwd":
        W1_fwd = W1_fwd.t().contiguous()
        W2_fwd = W2_fwd.t().contiguous()
        W3_fwd = W3_fwd.t().contiguous()
        ms = triton.testing.do_bench(lambda: compiled(x_fwd, W1_fwd, W2_fwd, W3_fwd))
    elif provider == "torch-compile-fwd-bwd":
        W1_bwd = W1_bwd.t().contiguous()
        W2_bwd = W2_bwd.t().contiguous()
        W3_bwd = W3_bwd.t().contiguous()
        provider_fn = compiled
        ms = triton.testing.do_bench(run_fwd_bwd)

    return ms


def clear_gradients(*args):
    for arg in args:
        if isinstance(arg, torch.Tensor) and arg.grad is not None:
            arg.grad = None


def clear_memory(device):
    torch._C._cuda_clearCublasWorkspaces()
    torch._dynamo.reset()
    gc.collect()
    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats(device)


def peak_memory(f, *args, grad_output=None, device=None):
    for _ in range(10):
        # Clean everything
        clear_memory(device)
        clear_gradients(*args)

        # Run once
        out = f(*args)
        if grad_output is not None:
            out.backward(grad_output)

        # Measure peak memory
        torch.cuda.synchronize()
        memory = torch.cuda.max_memory_allocated(device)

    return memory


def memory_triton(device=None):
    # Clean everything
    clear_memory(device)

    # Initialize inputs for forward
    x_fwd, W1_fwd, W2_fwd, W3_fwd = create_input(
        device, dtype=torch.bfloat16, grad=False
    )

    # Initialize inputs for backward
    x_bwd, W1_bwd, W2_bwd, W3_bwd = create_input(
        device, dtype=torch.bfloat16, grad=True
    )
    grad_output = torch.randn_like(x_bwd)

    # Run forward measurement
    print("\nTriton Forward Memory:")
    print("Current memory: ", torch.cuda.memory_allocated(device) / (1024**3))
    memory_fwd = peak_memory(fused, x_fwd, W1_fwd, W2_fwd, W3_fwd, device=device)
    print("Peak memory: ", memory_fwd / (1024**3))

    # Run forward + backward measurement
    print("\nTriton Forward + Backward Memory:")
    print("Current memory: ", torch.cuda.memory_allocated(device) / (1024**3))
    memory_fwd_bwd = peak_memory(
        fused, x_bwd, W1_bwd, W2_bwd, W3_bwd, grad_output=grad_output, device=device
    )
    print("Peak memory: ", memory_fwd_bwd / (1024**3))

    return memory_fwd, memory_fwd_bwd


def memory_baseline(f, device=None):
    # Clean memory
    clear_memory(device)

    # Initialize inputs for forward
    x_fwd, W1_fwd, W2_fwd, W3_fwd = create_input(
        device, dtype=torch.bfloat16, grad=False
    )
    W1_fwd = W1_fwd.t().contiguous()
    W2_fwd = W2_fwd.t().contiguous()
    W3_fwd = W3_fwd.t().contiguous()

    # Initialize inputs for backward
    x_bwd, W1_bwd, W2_bwd, W3_bwd = create_input(
        device, dtype=torch.bfloat16, grad=True
    )
    W1_bwd = W1_bwd.t().contiguous()
    W2_bwd = W2_bwd.t().contiguous()
    W3_bwd = W3_bwd.t().contiguous()
    grad_output = torch.randn_like(x_bwd)

    # Run forward measurement
    print(f"\n{f.__name__} Forward Memory:")
    print("Current memory: ", torch.cuda.memory_allocated(device) / (1024**3))
    memory_fwd = peak_memory(f, x_fwd, W1_fwd, W2_fwd, W3_fwd, device=device)
    print("Peak memory: ", memory_fwd / (1024**3))

    # Run forward + backward measurement
    print(f"\n{f.__name__} Forward + Backward Memory:")
    print("Current memory: ", torch.cuda.memory_allocated(device) / (1024**3))
    memory_fwd_bwd = peak_memory(
        f, x_bwd, W1_bwd, W2_bwd, W3_bwd, grad_output=grad_output, device=device
    )
    print("Peak memory: ", memory_fwd_bwd / (1024**3))

    return memory_fwd, memory_fwd_bwd


def test():
    # Setup
    torch.manual_seed(0)
    device = torch.device("cuda")

    # Check forward correctness
    print("Checking forward pass...")
    if not check_forward(fused, unfused, device=device):
        return

    # Check backward correctness
    print("Checking backward pass...")
    if not check_backward(device):
        return

    # Compute performance
    print("\nPerformance")
    torch.set_grad_enabled(False)
    benchmark.run(print_data=True, show_plots=False)
    print("")

    # Compute memory
    print("\nMemory Analysis")
    triton_fwd, triton_fwd_bwd = memory_triton(device=device)
    unfused_fwd, unfused_fwd_bwd = memory_baseline(unfused, device=device)
    compiled_fwd, compiled_fwd_bwd = memory_baseline(compiled, device=device)

    print("\nMemory Savings:")
    print("Forward pass:")
    print("  vs unfused: ", unfused_fwd / triton_fwd)
    print("  vs compiled: ", compiled_fwd / triton_fwd)
    print("Forward + Backward pass:")
    print("  vs unfused: ", unfused_fwd_bwd / triton_fwd_bwd)
    print("  vs compiled: ", compiled_fwd_bwd / triton_fwd_bwd)
    print("")


if __name__ == "__main__":
    test()
