# Copyright (c) Meta Platforms, Inc. and affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import logging
import os
import sys
import typing as T
from pathlib import Path
from timeit import default_timer as timer
from typing import List, Optional

import esm
import torch
from esm.data import read_fasta


logger = logging.getLogger()
logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%y/%m/%d %H:%M:%S",
)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


PathLike = T.Union[str, Path]


def enable_cpu_offloading(model):
    from torch.distributed.fsdp import CPUOffload, FullyShardedDataParallel
    from torch.distributed.fsdp.wrap import enable_wrap, wrap

    torch.distributed.init_process_group(
        backend="nccl", init_method="tcp://localhost:9999", world_size=1, rank=0
    )

    wrapper_kwargs = dict(cpu_offload=CPUOffload(offload_params=True))

    with enable_wrap(wrapper_cls=FullyShardedDataParallel, **wrapper_kwargs):
        for layer_name, layer in model.layers.named_children():
            wrapped_layer = wrap(layer)
            setattr(model.layers, layer_name, wrapped_layer)
        model = wrap(model)

    return model


def init_model_on_gpu_with_cpu_offloading(model):
    model = model.eval()
    model_esm = enable_cpu_offloading(model.esm)
    del model.esm
    model.cuda()
    model.esm = model_esm
    return model


def create_batched_sequence_datasest(
    sequences: T.List[T.Tuple[str, str]], max_tokens_per_batch: int = 1024
) -> T.Generator[T.Tuple[T.List[str], T.List[str]], None, None]:
    batch_headers, batch_sequences, num_tokens = [], [], 0
    for header, seq in sequences:
        if (len(seq) + num_tokens > max_tokens_per_batch) and num_tokens > 0:
            yield batch_headers, batch_sequences
            batch_headers, batch_sequences, num_tokens = [], [], 0
        batch_headers.append(header)
        batch_sequences.append(seq)
        num_tokens += len(seq)

    yield batch_headers, batch_sequences


def run_esmfold(
    fasta: Path,
    pdb: Path,
    model_dir: Path,
    num_recycles: Optional[int] = None,
    max_tokens_per_batch: int = 1024,
    chunk_size: Optional[int] = None,
    cpu_only: bool = False,
    cpu_offload: bool = False,
    version: str = "esmfold_v1",
):
    """

    Parameters
    ----------
    fasta : Path
        Path to input FASTA file.
    pdb : Path
        Path to output PDB directory.
    model_dir : Path
        Parent path to Pretrained ESM data directory.
    num_recycles : int, optional
        Number of recycles to run.
        Defaults to number used in training (4).
    max_tokens_per_batch : int, optional
        Maximum number of tokens per gpu forward-pass.
        This will group shorter sequences together
        for batched prediction. Lowering this can help
        with out of memory issues, if these occur on
        short sequences.
    chunk_size : int, optional
        Chunks axial attention computation to reduce memory
        usage from O(L^2) to O(L). Equivalent to running a
        for loop over chunks of of each dimension. Lower values
        will result in lower memory usage at the cost of speed.
        Recommended values: 128, 64, 32. Default: None.
    cpu_only : bool, optional
        CPU only.
    cpu_offload : bool, optional
        Enable CPU offloading.

    """
    if not fasta.exists():
        raise FileNotFoundError(fasta)

    pdb.mkdir(exist_ok=True)

    # Read fasta and sort sequences by length
    logger.info(f"Reading sequences from {fasta}")
    all_sequences = sorted(read_fasta(fasta), key=lambda header_seq: len(header_seq[1]))
    logger.info(f"Loaded {len(all_sequences)} sequences from {fasta}")

    logger.info("Loading model")

    # Use pre-downloaded ESM weights from model_pth.
    if model_dir is not None:
        # if pretrained model path is available
        torch.hub.set_dir(model_dir)

    if version == "esmfold_v1":
        # for designability
        model = esm.pretrained.esmfold_v1()
    elif version == "esmfold_v0":
        # for folding ESM eval
        model = esm.pretrained.esmfold_v0()

    model = model.eval()
    model.set_chunk_size(chunk_size)

    if cpu_only:
        model.esm.float()  # convert to fp32 as ESM-2 in fp16 is not supported on CPU
        model.cpu()
    elif cpu_offload:
        model = init_model_on_gpu_with_cpu_offloading(model)
    else:
        model.cuda()
    logger.info("Starting Predictions")
    batched_sequences = create_batched_sequence_datasest(
        all_sequences, max_tokens_per_batch
    )

    num_completed = 0
    num_sequences = len(all_sequences)
    torch.set_grad_enabled(False)
    for headers, sequences in batched_sequences:
        start = timer()
        try:
            output = model.infer(sequences, num_recycles=num_recycles)
        except RuntimeError as e:
            if e.args[0].startswith("CUDA out of memory"):
                if len(sequences) > 1:
                    logger.info(
                        f"Failed (CUDA out of memory) to predict batch of size {len(sequences)}. "
                        "Try lowering `--max-tokens-per-batch`."
                    )
                else:
                    logger.info(
                        f"Failed (CUDA out of memory) on sequence {headers[0]} of length {len(sequences[0])}."
                    )

                continue
            raise

        output = {key: value.cpu() for key, value in output.items()}
        pdbs = model.output_to_pdb(output)
        tottime = timer() - start
        time_string = f"{tottime / len(headers):0.1f}s"
        if len(sequences) > 1:
            time_string = time_string + f" (amortized, batch size {len(sequences)})"
        for header, seq, pdb_string, mean_plddt, ptm in zip(
            headers, sequences, pdbs, output["mean_plddt"], output["ptm"]
        ):
            output_file = pdb / f"{header}.pdb"
            output_file.write_text(pdb_string)
            num_completed += 1
            logger.info(
                f"Predicted structure for {header} with length {len(seq)}, pLDDT {mean_plddt:0.1f}, "
                f"pTM {ptm:0.3f} in {time_string}. "
                f"{num_completed} / {num_sequences} completed."
            )

