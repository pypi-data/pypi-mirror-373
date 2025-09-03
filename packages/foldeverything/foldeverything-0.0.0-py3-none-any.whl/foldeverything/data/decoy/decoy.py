from dataclasses import dataclass, replace
from pathlib import Path
import random
from typing import Dict, List, Optional, Union

import numpy as np
from foldeverything.data.data import (
    MSA,
    Input,
    Manifest,
    Record,
    Structure,
    AffinityInfo,
    Bond,
)


def sample_decoys(
    input: Input,
    num_decoys: int,
    structures_cid_dir: Path,
    diff_decoys_size: List = [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5],
    protein_to_cids_binders: Dict = {},
    cid_to_num_atoms: Dict = {},
    num_atoms_to_cids_binders: Dict = {},
    cids_to_fps: Dict = {},
    training_cids: set = set(),
    tanimoto_threshold: float = 0.9,
):
    record = input.record
    cid = record.affinity.cid
    normalized_protein_accession = record.affinity.normalized_protein_accession
    exclude_cids = list(
        set(protein_to_cids_binders[normalized_protein_accession]) & set(training_cids)
    )
    num_atoms = cid_to_num_atoms[cid]
    sample_cids = []
    count_iter = 0
    while len(sample_cids) < num_decoys:
        count_iter += 1
        diff_size = random.choice(diff_decoys_size)  # noqa: S311
        cids_same_size = num_atoms_to_cids_binders[num_atoms + diff_size]
        tot_sample_cids = list(
            set(training_cids) & (set(cids_same_size) - set(exclude_cids))
        )
        if len(tot_sample_cids) == 0:
            continue
        sample_cid = random.choice(tot_sample_cids)  # noqa: S311
        similarities = max(
            [
                tanimoto_similarity(cids_to_fps[sample_cid], cids_to_fps[sample_cid_])
                for sample_cid_ in exclude_cids
            ]
        )
        if similarities < tanimoto_threshold or count_iter > 5 * num_decoys:
            sample_cids.append(sample_cid)
    return [
        build_decoy(input, sample_cid, structures_cid_dir) for sample_cid in sample_cids
    ]


def build_decoy(input: Input, sample_cid: int, structures_cid_dir: Path):
    # Load structures and record
    structure_input = input.structure
    structure_decoy = structures_cid_dir / f"{sample_cid}.npz"
    structure_decoy = Structure.load(structure_decoy)
    record_input = input.record
    affinity_input = record_input.affinity

    ligand_atom_start_idx = structure_input.chains["atom_idx"][-1]

    # Build new atoms
    atoms_new = structure_input.atoms[:ligand_atom_start_idx].copy()
    atoms_new = np.concatenate([atoms_new, structure_decoy.atoms.copy()])

    # Build new bonds
    bonds_new = np.array(
        [
            (atom_1 + ligand_atom_start_idx, atom_2 + ligand_atom_start_idx, type)
            for atom_1, atom_2, type in structure_decoy.bonds  # noqa: A001
        ],
        dtype=Bond,
    )

    # Build new residues
    residues_new = structure_input.residues.copy()
    residues_new["atom_num"][-1] = structure_decoy.residues["atom_num"]

    # Build new chains
    chains_new = structure_input.chains.copy()
    chains_new["atom_num"][-1] = structure_decoy.residues["atom_num"]

    # Build new coords
    coords_new = structure_input.coords[:ligand_atom_start_idx].copy()
    coords_new = np.concatenate([coords_new, structure_decoy.coords.copy()])

    # Build new affinity record
    affinity_new = AffinityInfo(
        affinity=10.0,
        outcome=0,
        activity_name=affinity_input.activity_name,
        activity_qualifier="=",
        sid=affinity_input.sid,
        cid=sample_cid,
        normalized_protein_accession=affinity_input.normalized_protein_accession,
        aid=affinity_input.aid,
        pair_id=affinity_input.pair_id,
    )

    # Build new input
    structure_new = replace(
        structure_input,
        atoms=atoms_new,
        bonds=bonds_new,
        residues=residues_new,
        chains=chains_new,
        coords=coords_new,
    )
    record_new = replace(record_input, affinity=affinity_new)
    input_new = replace(input, structure=structure_new, record=record_new)

    return input_new


def tanimoto_similarity(fp1, fp2):
    sum1 = fp1.sum()
    sum2 = fp2.sum()
    sumint = (fp1 & fp2).sum()
    return sumint / (sum1 + sum2 - sumint)
