from pathlib import Path

import numpy as np
import torch

from foldeverything.data.data import (
    MSA,
    Input,
    Record,
    Structure,
    Template,
)

def load_record(record_id: str, record_dir: Path) -> Record:
    """Load the given record.

    Parameters
    ----------
    record_id : str
        The record id to load.
    record_dir : Path
        The path to the record directory.

    Returns
    -------
    Record
        The loaded record.
    """
    return Record.load(record_dir / f"{record_id}.json")


def load_structure(record: Record, struct_dir: Path) -> Input:
    """Load the given input data.

    Parameters
    ----------
    record : str
        The record to load.
    target_dir : Path
        The path to the data directory.

    Returns
    -------
    Input
        The loaded input.

    """
    if (struct_dir / f"{record.id}.npz").exists():
        structure_path = struct_dir / f"{record.id}.npz"
    else:
        structure_path = struct_dir / f"{record.id}" / f"{record.id}_model_0.npz"
    return Structure.load(structure_path)


def load_msas(chain_ids: set[int], record: Record, msa_dir: Path) -> Input:
    """Load the given input data.

    Parameters
    ----------
    chain_ids : set[int]
        The chain ids to load.
    record : Record
        The record to load.
    msa_dir : Path
        The path to the MSA directory.

    Returns
    -------
    Input
        The loaded input.

    """
    msas = {}
    for chain in record.chains:
        if chain.chain_id not in chain_ids:
            continue

        msa_id = chain.msa_id
        if msa_id != -1:
            msa_path = msa_dir / f"{msa_id}.npz"
            msa = MSA.load(msa_path)
            msas[chain.chain_id] = msa

    return msas


def load_templates(
    chain_ids: set[int],
    record: Record,
    template_dir: Path,
    max_templates: int,
    no_template_prob: float,
    training: bool,
    random: np.random.Generator,
) -> dict[str, list[Template]]:
    """Load the given input data.

    Parameters
    ----------
    record : str
        The record to load.
    target_dir : Path
        The path to the data directory.
    msa_dir : Path
        The path to the MSA directory.
    template_dir : Path
        The path to the template directory.
    max_templates : int
        The maximum number of templates to load.
    no_template_prob : float
        The probability of not loading any templates.
    training : bool
        Whether the data is for training.
    random : np.random.Generator
        The random number generator.

    Returns
    -------
    dict[str, list[Template]]
        The loaded templates.

    """
    templates = {}
    for chain in record.chains:
        if chain.chain_id not in chain_ids:
            continue

        # Check if chain has templates, skipping non proteins
        template_ids = chain.template_ids
        if template_ids is None:
            continue

        # Pick how many templates to sample
        max_chain_templates = min(max_templates, len(template_ids))

        # If 0, skips
        if (max_chain_templates == 0) or (random.random() < no_template_prob):
            continue

        # Sample for training, pick firsts for validation
        if training:
            max_chain_templates = random.integers(1, max_chain_templates + 1)
            template_indices = torch.randperm(len(template_ids))
            template_indices = template_indices[:max_chain_templates]
            template_ids = [template_ids[idx.item()] for idx in template_indices]
        else:
            template_ids = template_ids[:max_chain_templates]

        # Load templates
        templates[chain.chain_id] = []
        for template_name in template_ids:
            template_path = template_dir / f"{template_name}.npz"
            template = Template.load(template_path)
            templates[chain.chain_id].append(template)

    return templates