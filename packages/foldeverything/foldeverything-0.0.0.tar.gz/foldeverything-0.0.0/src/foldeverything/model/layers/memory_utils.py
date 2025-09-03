import torch


def memory_hook(module, input, output, p=""):
    allocated_memory = torch.cuda.memory_allocated()
    name = str(module).split("(")[0]
    l = [
        "Sequential",
        "LayerNorm",
        "SwiGLU",
        "Transition",
        "PreLayerNorm",
        "Rearrange",
        "AttentionPairBias",
        "Sigmoid",
        "AdaLN",
        "ReLU",
        "FourierEmbedding",
        "ConditionedTransitionBlock",
        "TriangularUpdate",
        "SiLU",
    ]

    if name not in l:
        print(
            f"Memory allocated after forward pass of {p} {name}: {allocated_memory / 1024 ** 2:.2f} MB"
        )


def memory_print(where):
    allocated_memory = torch.cuda.memory_allocated()
    print(f"Memory allocated at {where}: {allocated_memory / 1024 ** 2:.2f} MB")


def backward_memory_hook(module, grad_input, grad_output, p=""):
    allocated_memory = torch.cuda.memory_allocated()
    name = str(module).split("(")[0]
    print(
        f"Memory allocated after backward pass of {p} {name}: {allocated_memory / 1024 ** 2:.2f} MB"
    )

