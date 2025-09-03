import copy
from dataclasses import replace
import io
import multiprocessing
import numbers
import os
import pickle
from pathlib import Path
import random
import tempfile
import time
import traceback
from typing import Optional, Dict, Any, List
from collections import namedtuple
import subprocess
import re
from sklearn.cluster import DBSCAN
from Bio import PDB
from biotite import structure
from Bio.Seq import Seq
import json

from matplotlib import pyplot as plt
import matplotlib as mpl

mpl.rcParams["figure.max_open_warning"] = 100
import pydssp
import freesasa
import rdkit
from Bio import Align

from foldeverything.data.rmsd_computation import get_true_coordinates
from foldeverything.model.loss.diffusion import weighted_rigid_align
from foldeverything.task.predict.data_eval import EvalDataModule, collate
from foldeverything.task.predict.predict import Predict

freesasa.setVerbosity(1)
import torch
import numpy as np
import pandas as pd
from tqdm import tqdm
import wandb
from plip.structure.preparation import PDBComplex, LigandFinder
from collections import defaultdict

from foldeverything.data import const
from foldeverything.task.task import Task
from foldeverything.data.data import Structure
from foldeverything.data.write.mmcif import to_mmcif
from foldeverything.model.loss.validation import factored_lddt_loss, compute_subset_rmsd


def compute_rmsd(atom_coords: torch.Tensor, pred_atom_coords: torch.Tensor):
    rmsd, _ = compute_subset_rmsd(
        atom_coords,
        pred_atom_coords,
        atom_mask=torch.ones_like(atom_coords[..., 0]),
        align_weights=torch.ones_like(atom_coords[..., 0]),
        subset_mask=torch.ones_like(atom_coords[..., 0]),
        multiplicity=1,
    )
    return rmsd


def make_histogram(
    df,
    column_name: str,
):
    data = df[column_name].dropna()
    fig, ax = plt.subplots(figsize=(6, 4))

    ax.hist(data, bins=50, alpha=0.7, edgecolor="black", linewidth=0.5)
    ax.axvline(data.mean(), color="red", linestyle="dashed", linewidth=1)

    ax.set_title(
        f"{column_name.replace('_', ' ').capitalize()} Distribution", fontsize=12
    )
    ax.set_xlabel(column_name.replace("_", " "), fontsize=10)
    ax.set_ylabel("Count", fontsize=10)

    ax.grid(True, axis="y", linestyle="--", linewidth=0.5, alpha=0.6)
    ax.tick_params(axis="both", which="major", labelsize=8)

    plt.tight_layout()
    return fig


def get_folding_metrics(
    feat,
    folded,
    diffusion_samples,
    compute_lddts=True,
    store_confidence=True,
):
    batch = collate([feat])

    # Get best sample
    confidence = 0.8 * folded["iptm"] + 0.2 * folded["ptm"]
    best_idx = np.argmax(confidence)
    best_sample = {k: folded[k][best_idx] for k in const.eval_keys_confidence}
    best_sample["coords"] = folded["coords"][best_idx]

    # Compute RMSDs
    rmsd_out = get_true_coordinates(
        batch=batch,
        out={"sample_atom_coords": torch.from_numpy(best_sample["coords"])},
        diffusion_samples=1,
        symmetry_correction=False,
        protein_lig_rmsd=True,
    )
    true_coords_resolved_mask = rmsd_out["true_coords_resolved_mask"]
    true_coords_resolved_mask = true_coords_resolved_mask * batch[
        "has_structure"
    ].repeat_interleave(diffusion_samples, 0)

    # Add to metrics dictionary
    metrics = {k: best_sample[k] for k in const.eval_keys_confidence}
    metrics["rmsd"] = rmsd_out.get("rmsd").item()
    metrics["rmsd_prot"] = rmsd_out.get("rmsd_prot").item()
    metrics["rmsd_lig"] = rmsd_out.get("rmsd_lig").item()
    metrics["rmsd_design"] = rmsd_out.get("rmsd_design").item()
    metrics["rmsd_target"] = rmsd_out.get("rmsd_target").item()
    metrics["rmsd_design_target"] = rmsd_out.get("rmsd_design_target").item()

    metrics["min_interaction_pae<1.5"] = bool(metrics["min_interaction_pae"] <= 1.5)
    metrics["min_interaction_pae<2.5"] = bool(metrics["min_interaction_pae"] <= 2.5)
    metrics["design_ptm>80"] = bool(metrics["design_ptm"] >= 0.8)
    metrics["design_ptm>75"] = bool(metrics["design_ptm"] >= 0.75)
    metrics["rmsd<2.5"] = bool(metrics["rmsd"] <= 2.5)
    metrics["proteo_pass"] = (
        bool(metrics["rmsd"] <= 2.5)
        & bool(metrics["design_ptm"] >= 0.8)
        & bool(metrics["min_interaction_pae"] <= 1.5)
    )
    metrics["boltz2_pass"] = (
        bool(metrics["rmsd"] <= 2.5)
        & bool(metrics["design_ptm"] >= 0.75)
        & bool(metrics["min_interaction_pae"] <= 2.5)
    )
    metrics["designability_rmsd_2"] = bool(metrics["rmsd_design"] <= 2.0)
    metrics["designability_rmsd_4"] = bool(metrics["rmsd_design"] <= 4.0)

    # Comput LDDTs
    if compute_lddts:
        all_lddt_dict, _ = factored_lddt_loss(
            feats=batch,
            atom_mask=true_coords_resolved_mask,
            true_atom_coords=batch["coords"],
            pred_atom_coords=torch.from_numpy(best_sample["coords"]),
            multiplicity=diffusion_samples,
            representative_lddt=False,
            exclude_ions=False,
        )

        metrics.update({f"lddt_{k}": v.max().item() for k, v in all_lddt_dict.items()})
        metrics["designability_lddt_60"] = bool(metrics["lddt_intra_design"] >= 0.6)
        metrics["designability_lddt_65"] = bool(metrics["lddt_intra_design"] >= 0.65)
        metrics["designability_lddt_70"] = bool(metrics["lddt_intra_design"] >= 0.7)
        metrics["designability_lddt_75"] = bool(metrics["lddt_intra_design"] >= 0.75)
        metrics["designability_lddt_80"] = bool(metrics["lddt_intra_design"] >= 0.8)
        metrics["designability_lddt_85"] = bool(metrics["lddt_intra_design"] >= 0.85)
        metrics["designability_lddt_90"] = bool(metrics["lddt_intra_design"] >= 0.9)

    # Remove confidence keys if not storing confidence
    if not store_confidence:
        metrics = {
            k: v
            for k, v in metrics.items()
            if not any(conf_key in k for conf_key in const.eval_keys_confidence)
        }

    return metrics, best_sample["coords"]


def get_plip(pdb_buffer, atom_design_mask, small_molecule: bool = False):
    pdb_buffer.seek(0)  # ensure we read from the start
    lines = pdb_buffer.readlines()

    # Determine the chain ID from the ATOM records
    chain_id = None
    for line in lines:
        if line.startswith("ATOM"):
            atom_num = int(line[6:11].strip())
            _chain_id = line[21:22].strip()
            if atom_design_mask[atom_num - 1]:
                if chain_id is None:
                    chain_id = _chain_id
                elif _chain_id != chain_id:
                    raise RuntimeError(
                        "plip computation assumes all designed residues are in the same chain, but this is not the case!"
                        f" Chain {chain_id} and {_chain_id} are found."
                    )
    if chain_id is None:
        raise RuntimeError("No chain_id found for plip computation!")
    breakpoint()
    return plip_from_chain(pdb_buffer, chain_id, small_molecule)


def plip_from_chain(pdb_buffer, chain_id: str, small_molecule: bool = False):
    # Make a new PLIP PDB complex and load the pdb file

    mol = PDBComplex()
    mol.load_pdb(pdb_buffer.getvalue(), as_string=True)

    if small_molecule:
        mol.analyze()
    else:
        ligandfinder = LigandFinder(
            mol.protcomplex, mol.altconf, mol.modres, mol.covalent, mol.Mapper
        )

        peptide = ligandfinder.getpeptides(chain_id)

        plip_data = namedtuple(
            "ligand",
            "mol hetid chain position water members longname type atomorder can_to_pdb",
        )
        peptide = plip_data(
            mol=peptide.mol,
            hetid=peptide.hetid,
            chain=peptide.chain,
            position=peptide.position,
            water=peptide.water,
            members=peptide.members,
            longname=peptide.longname,
            type="PEPTIDE",
            atomorder=peptide.atomorder,
            can_to_pdb=peptide.can_to_pdb,
        )
        mol.characterize_complex(peptide)
    breakpoint()
    plip_metrics = {
        "plip_hbonds": 0,
        "plip_hydrophobic": 0,
        "plip_pistacking": 0,
        "plip_pication": 0,
        "plip_saltbridge": 0,
        "plip_waterbridge": 0,
        "plip_halogen": 0,
        "plip_metal": 0,
    }

    def cross(interaction_list):
        """Count number of cross chain interactions."""
        count = 0
        for item in interaction_list:
            chain_A = item.reschain
            chain_B = item.reschain_l
            if chain_A != chain_B and any([chain_A == chain_id, chain_B == chain_id]):
                count += 1
        return count
    breakpoint()
    for lig_id, interaction_set in mol.interaction_sets.items():
        breakpoint()
        if "UNK" in lig_id:
            continue
        plip_metrics["plip_hbonds"] += cross(
            interaction_set.hbonds_ldon + interaction_set.hbonds_pdon
        )
        plip_metrics["plip_hydrophobic"] += cross(interaction_set.hydrophobic_contacts)
        plip_metrics["plip_pistacking"] += cross(interaction_set.pistacking)
        plip_metrics["plip_pication"] += cross(interaction_set.pication_laro) + cross(
            interaction_set.pication_paro
        )
        plip_metrics["plip_saltbridge"] += cross(
            interaction_set.saltbridge_lneg + interaction_set.saltbridge_pneg
        )
        plip_metrics["plip_waterbridge"] += cross(interaction_set.water_bridges)
        plip_metrics["plip_halogen"] += cross(interaction_set.halogen_bonds)
        plip_metrics["plip_metal"] += cross(interaction_set.metal_complexes)

    return plip_metrics


def tm_score(coords1, coords2):
    num_atoms1 = coords1.shape[0]
    num_atoms2 = coords2.shape[0]

    atom_array1 = structure.AtomArray(num_atoms1)
    atom_array1.coord = coords1.numpy()
    atom_array1.element = np.array(["C"] * num_atoms1)
    atom_array1.atom_name = np.array(["CA"] * num_atoms1)
    atom_array1.res_name = np.array(["ALA"] * num_atoms1)
    atom_array1.chain_id = np.array(["A"] * num_atoms1)
    atom_array1.res_id = np.arange(1, num_atoms1 + 1)

    atom_array2 = structure.AtomArray(num_atoms2)
    atom_array2.coord = coords2.numpy()
    atom_array2.element = np.array(["C"] * num_atoms2)
    atom_array2.atom_name = np.array(["CA"] * num_atoms2)
    atom_array2.res_name = np.array(["ALA"] * num_atoms2)
    atom_array2.chain_id = np.array(["A"] * num_atoms2)
    atom_array2.res_id = np.arange(1, num_atoms2 + 1)

    try:
        # This fails with a value error if the structures are too dissimilar. In that event, we return 0 as the TM-Score
        aligned, transform, fixed_indices, mobile_indices = (
            structure.superimpose_structural_homologs(
                atom_array1, atom_array2, max_iterations=25
            )
        )
        tm_align_fixed = structure.tm_score(
            atom_array1,
            aligned,
            fixed_indices,
            mobile_indices,
        )
    except:
        tm_align_fixed = 0

    tm_score_rmsd_aligned = 0
    if num_atoms1 == num_atoms2:
        coords1 = weighted_rigid_align(
            coords1.float()[None],
            coords2.float()[None],
            weights=torch.ones(len(coords1)).float()[None],
            mask=torch.ones(len(coords2))[None],
        ).squeeze()

        atom_array1 = structure.AtomArray(num_atoms1)
        atom_array1.coord = coords1.numpy()
        atom_array1.element = np.array(["C"] * num_atoms1)
        atom_array1.atom_name = np.array(["CA"] * num_atoms1)
        atom_array1.res_name = np.array(["ALA"] * num_atoms1)
        atom_array1.chain_id = np.array(["A"] * num_atoms1)
        atom_array1.res_id = np.arange(1, num_atoms1 + 1)

        atom_array2 = structure.AtomArray(num_atoms2)
        atom_array2.coord = coords2.numpy()
        atom_array2.element = np.array(["C"] * num_atoms2)
        atom_array2.atom_name = np.array(["CA"] * num_atoms2)
        atom_array2.res_name = np.array(["ALA"] * num_atoms2)
        atom_array2.chain_id = np.array(["A"] * num_atoms2)
        atom_array2.res_id = np.arange(1, num_atoms2 + 1)
        try:
            _, _, fixed_indices, mobile_indices = (
                structure.superimpose_structural_homologs(
                    atom_array1, atom_array2, max_iterations=25
                )
            )
            tm_score_rmsd_aligned = structure.tm_score(
                atom_array1,
                atom_array2,
                fixed_indices,
                mobile_indices,
            )
        except:
            pass

    return tm_score_rmsd_aligned, tm_align_fixed


def vendi_from_sim(mat):
    mat = mat + mat.T
    np.fill_diagonal(mat, 1.0)
    eigvals, _ = np.linalg.eigh(mat / len(mat))
    eigvals = np.clip(eigvals, 0.0, None)
    return np.exp(np.nansum(-(eigvals * np.log(eigvals))))


def vendi_scores(
    all_ca_coords: List[np.ndarray],
    all_metrics: list = None,
    folding_metrics: bool = False,
    diversity_subset: int = None,
    compute_lddts: bool = True,
    backbone_folding_metrics: bool = False,
) -> float:
    if folding_metrics or diversity_subset is not None:
        assert all_metrics is not None
    if all_metrics is not None:
        assert len(all_ca_coords) == len(all_metrics)
    if diversity_subset is not None and diversity_subset < len(all_ca_coords):
        indices = random.sample(range(len(all_ca_coords)), diversity_subset)
        all_metrics = [all_metrics[i] for i in indices]
        all_ca_coords = [all_ca_coords[i] for i in indices]
    N = len(all_ca_coords)
    tm = np.zeros((N, N), dtype=np.float32)
    tm_fixed = np.zeros((N, N), dtype=np.float32)

    for i in tqdm(range(N), desc="Computing structure diversity."):
        for j in range(i + 1, N):
            tm_score_rmsd_aligned, tm_fixeds = tm_score(
                all_ca_coords[i], all_ca_coords[j]
            )
            tm[i, j] = tm_score_rmsd_aligned
            tm_fixed[i, j] = tm_fixeds

    scores = {
        "vendi_tm_fixed": vendi_from_sim(tm_fixed),
        "vendi_tm_align": vendi_from_sim(tm),
    }
    prefixes = []
    if folding_metrics:
        prefixes.append("")
    if backbone_folding_metrics:
        prefixes.append("bb_")
    for prefix in prefixes:
        mask_2 = np.array([m[f"{prefix}designability_rmsd_2"] for m in all_metrics])
        mask_4 = np.array([m[f"{prefix}designability_rmsd_4"] for m in all_metrics])
        mask_25 = np.array([m[f"{prefix}rmsd<2.5"] for m in all_metrics])
        scores.update(
            {
                f"vendi_tm_{prefix}rmsd<2.5": vendi_from_sim(
                    tm_fixed[mask_25][:, mask_25]
                )
                if np.sum(mask_25) > 0
                else 0.0,
                f"vendi_tm_{prefix}rmsd_2": vendi_from_sim(tm_fixed[mask_2][:, mask_2])
                if np.sum(mask_2) > 0
                else 0.0,
                f"vendi_tm_{prefix}rmsd_4": vendi_from_sim(tm_fixed[mask_4][:, mask_4])
                if np.sum(mask_4) > 0
                else 0.0,
            }
        )

        if compute_lddts:
            mask_60 = np.array(
                [m[f"{prefix}designability_lddt_60"] for m in all_metrics]
            )
            mask_65 = np.array(
                [m[f"{prefix}designability_lddt_65"] for m in all_metrics]
            )
            mask_70 = np.array(
                [m[f"{prefix}designability_lddt_70"] for m in all_metrics]
            )
            mask_75 = np.array(
                [m[f"{prefix}designability_lddt_75"] for m in all_metrics]
            )
            mask_80 = np.array(
                [m[f"{prefix}designability_lddt_80"] for m in all_metrics]
            )
            mask_85 = np.array(
                [m[f"{prefix}designability_lddt_85"] for m in all_metrics]
            )
            mask_90 = np.array(
                [m[f"{prefix}designability_lddt_90"] for m in all_metrics]
            )
            scores.update(
                {
                    f"vendi_tm_{prefix}lddt_60": vendi_from_sim(
                        tm_fixed[mask_60][:, mask_60]
                    )
                    if np.sum(mask_60) > 0
                    else 0.0,
                    f"vendi_tm_{prefix}lddt_65": vendi_from_sim(
                        tm_fixed[mask_65][:, mask_65]
                    )
                    if np.sum(mask_65) > 0
                    else 0.0,
                    f"vendi_tm_{prefix}lddt_70": vendi_from_sim(
                        tm_fixed[mask_70][:, mask_70]
                    )
                    if np.sum(mask_70) > 0
                    else 0.0,
                    f"vendi_tm_{prefix}lddt_75": vendi_from_sim(
                        tm_fixed[mask_75][:, mask_75]
                    )
                    if np.sum(mask_75) > 0
                    else 0.0,
                    f"vendi_tm_{prefix}lddt_80": vendi_from_sim(
                        tm_fixed[mask_80][:, mask_80]
                    )
                    if np.sum(mask_80) > 0
                    else 0.0,
                    f"vendi_tm_{prefix}lddt_85": vendi_from_sim(
                        tm_fixed[mask_85][:, mask_85]
                    )
                    if np.sum(mask_85) > 0
                    else 0.0,
                    f"vendi_tm_{prefix}lddt_90": vendi_from_sim(
                        tm_fixed[mask_90][:, mask_90]
                    )
                    if np.sum(mask_90) > 0
                    else 0.0,
                }
            )

    return scores


def vendi_sequences(all_seqs: List[np.ndarray], diversity_subset: int = None) -> float:
    if diversity_subset is not None and diversity_subset < len(all_seqs):
        all_seqs = random.sample(all_seqs, diversity_subset)

    N = len(all_seqs)
    sims = np.zeros((N, N), dtype=np.float32)
    aligner = Align.PairwiseAligner()
    for i in tqdm(range(N), desc="Computing sequence diversity."):
        for j in range(i + 1, N):
            seq1 = Seq(all_seqs[i])
            seq2 = Seq(all_seqs[j])
            alignments = aligner.align(seq1, seq2)

            similarity = alignments[0].score / max(len(seq1), len(seq2))
            sims[i, j] = similarity

    return {
        "vendi_seq_sim": vendi_from_sim(sims),
    }


def compute_novelty_foldseek(
    indir: Path,
    outdir: Path,
    reference_db: Path,
    files: List[str],
    foldseek_binary: str = "/data/rbg/users/hstark/foldseek/bin/foldseek",
) -> pd.DataFrame:
    if len(files) == 0:
        return np.nan

    aln_tsv = outdir / "aln.tsv"
    tmp_dir = outdir / "tmp"

    cmd = [
        foldseek_binary,
        "easy-search",
        str(indir),
        str(reference_db),
        str(aln_tsv),
        str(tmp_dir),
        "--format-output",
        "query,target,alntmscore,qtmscore,ttmscore",
        "--alignment-type",
        "1",
        "--exhaustive-search",
        "1",
    ]

    subprocess.run(cmd, check=True)

    df = pd.read_csv(
        aln_tsv,
        sep="\t",
        names=["query", "target", "alntmscore", "qtmscore", "ttmscore"],
    )
    df["tmscore"] = (df["qtmscore"] + df["ttmscore"]) / 2
    df = df.groupby("query").max().reset_index()
    queries = [Path(f).stem for f in files]
    df = df.set_index("query").reindex(queries, fill_value=0.0).reset_index()
    df_novelty = df[["query", "tmscore"]].rename(columns={"tmscore": "novelty"})
    return df_novelty


HYDROPHOBIC_RESIDUES = {"ALA", "VAL", "LEU", "ILE", "MET", "PHE", "PRO", "TRP"}


def run_freesasa_subprocess(pdb_path):
    """Run FreeSASA CLI safely in a subprocess and return per-atom SASA values and coordinates.
    This is to ensure that we do not stop the process in case freesasa throws a segfault due to running out of memory."""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdb") as tmp_pdb:
            tmp_pdb.write(Path(pdb_path).read_bytes())
            tmp_pdb.flush()

            json_output = tmp_pdb.name + ".json"
            cmd = ["freesasa", "-f", "json", "-o", json_output, tmp_pdb.name]
            result = subprocess.run(cmd, capture_output=True, timeout=10)

            if result.returncode != 0 or not os.path.exists(json_output):
                return None

            with open(json_output) as f:
                data = json.load(f)

            # Extract coordinates and SASA values
            coords = []
            sasa_vals = []

            for atom in data["atoms"]:
                resn = atom["residue"].strip()
                atomn = atom["name"].strip()
                if (
                    resn in HYDROPHOBIC_RESIDUES
                    and atomn.startswith("C")
                    and atom["area"] > 0
                ):
                    coords.append([atom["x"], atom["y"], atom["z"]])
                    sasa_vals.append(atom["area"])

            return np.array(coords), np.array(sasa_vals)

    except Exception:
        return None
    finally:
        try:
            os.remove(tmp_pdb.name)
            if os.path.exists(json_output):
                os.remove(json_output)
        except:
            pass


def largest_hydrophobic_patch_area(pdb_path, distance_cutoff=6.0):
    result = run_freesasa_subprocess(pdb_path)
    if result is None:
        return np.nan

    coords, sasa_vals = result
    if len(coords) == 0:
        return 0.0

    clustering = DBSCAN(eps=distance_cutoff, min_samples=1).fit(coords)
    labels = clustering.labels_

    max_patch_area = 0.0
    for label in np.unique(labels):
        area = sasa_vals[labels == label].sum()
        max_patch_area = max(max_patch_area, area)

    return max_patch_area


def compute_delta_sasa(pdb_io_buffer, atom_design_mask):
    with tempfile.NamedTemporaryFile("w+", suffix=".pdb", delete=False) as tmp:
        tmp.write(pdb_io_buffer.read())
        tmp_path = tmp.name
    struct_full = freesasa.Structure(tmp_path, options={"hetatm": True})
    os.remove(tmp_path)

    result = freesasa.calc(struct_full)
    design_sasa_bound = sum(
        result.atomArea(i)
        for i in range(struct_full.nAtoms())
        if atom_design_mask[i] == 1
    )

    # unbound sasa
    struct_lig = freesasa.Structure(None, options={"hetatm": True})
    for i in range(struct_full.nAtoms()):
        if atom_design_mask[i] == 1:
            chain = struct_full.chainLabel(i)
            resn = struct_full.residueName(i).strip()
            res_num = struct_full.residueNumber(i).strip()
            atom_name = struct_full.atomName(i).strip()
            x, y, z = struct_full.coord(i)
            struct_lig.addAtom(atom_name, resn, res_num, chain, x, y, z)
    design_sasa_unbound = freesasa.calc(struct_lig)
    design_sasa_unbound = design_sasa_unbound.totalArea()

    delta_sasa = design_sasa_unbound - design_sasa_bound
    return delta_sasa, design_sasa_unbound, design_sasa_bound


def compute_ss_metrics(dssp_pred, ss_conditioned):
    ss_metrics = {}
    conditioned_mask = ss_conditioned != 0
    if conditioned_mask.sum() == 0:
        return {
            "precision_loop": float("nan"),
            "recall_loop": float("nan"),
            "accuracy_loop": float("nan"),
            "precision_helix": float("nan"),
            "recall_helix": float("nan"),
            "accuracy_helix": float("nan"),
            "precision_sheet": float("nan"),
            "recall_sheet": float("nan"),
            "accuracy_sheet": float("nan"),
            "accuracy_overall": float("nan"),
        }
    types = {1: "loop", 2: "helix", 3: "sheet"}
    TP_total, total_conditioned = 0, conditioned_mask.sum().item()
    for i, name in types.items():
        TP = ((dssp_pred == i) & (ss_conditioned == i)).sum().item()
        FP = ((dssp_pred == i) & (ss_conditioned != i) & conditioned_mask).sum().item()
        FN = ((dssp_pred != i) & (ss_conditioned == i)).sum().item()
        precision = TP / (TP + FP) if (TP + FP) > 0 else float("nan")
        recall = TP / (TP + FN) if (TP + FN) > 0 else float("nan")
        accuracy = TP / (TP + FP + FN) if (TP + FP + FN) > 0 else float("nan")
        ss_metrics[f"precision_{name}"] = precision
        ss_metrics[f"recall_{name}"] = recall
        ss_metrics[f"accuracy_{name}"] = accuracy
        TP_total += TP

    accuracy_overall = (
        TP_total / total_conditioned if total_conditioned > 0 else float("nan")
    )
    ss_metrics["accuracy_overall"] = accuracy_overall
    return ss_metrics


def filter_resolved_atoms(structure: Structure) -> Structure:
    resolved_atom_indices = np.where(structure.atoms["is_present"])[0]
    return Structure.extract_atoms(structure, resolved_atom_indices)


def save_design_only_structure_to_pdb(
    atom_design_mask, structure, output_pdb_path: Path
):
    design_atom_indices = torch.where(atom_design_mask)[0].cpu().numpy()
    design_only_str = Structure.extract_atoms(
        structure, design_atom_indices, res_reindex=True
    )
    cif_text = to_mmcif(design_only_str)
    cif_io = io.StringIO(cif_text)
    mmcif_parser = PDB.MMCIFParser()
    pdb_writer = PDB.PDBIO()
    parsed_structure = mmcif_parser.get_structure("des_only", cif_io)
    pdb_writer.set_structure(parsed_structure)
    pdb_writer.save(str(output_pdb_path))


class EvaluateDesign(Task):
    """BoltzGen evaluation pipeline."""

    def __init__(
        self,
        name: str,
        data: EvalDataModule,
        design_dir: str = None,
        num_processes: int = 1,
        plip_original: bool = False,
        plip_refolded: bool = False,
        small_molecule_plips: bool = False,
        diversity_original: bool = False,
        diversity_refolded: bool = False,
        diversity_per_target_original: bool = False,
        diversity_per_target_refolded: bool = False,
        novelty_original: bool = False,
        novelty_refolded: bool = False,
        novelty_per_target_original: bool = False,
        novelty_per_target_refolded: bool = False,
        delta_sasa_original: bool = False,
        delta_sasa_refolded: bool = False,
        largest_hydrophobic: bool = False,
        compute_lddts: bool = True,  # computing LDDTs takes ~5-15 sec so it is optional
        run_clustering: bool = False,
        native: bool = False,
        sequence_recovery: bool = False,
        ss_condition: bool = False,
        backbone_folding_metrics: bool = False,
        debug: bool = False,
        wandb: Optional[Dict[str, Any]] = None,
        slurm: bool = False,
        diversity_subset: int = None,
        predict_task: Predict = None,
        affinity_task: Predict = None,
        use_prepred_affinitydir: bool = False,
        all_bb_rmsd: bool = False,
        use_prefolded_dir: bool = False,
        anchors_on: bool = False,
        foldseek_db: str = "/data/rbg/users/hstark/proteinblobs/data/foldseek_pdb/pdb",
        foldseek_binary: str = "/data/rbg/users/hstark/foldseek/bin/foldseek",
        skip_specific_ids: List[str] = None,
    ) -> None:
        """Initialize the task.

        Parameters
        ----------
        use_prefolded_dir : bool,
            Compute folding metrics and assume that the folding directory exists even if predict_staks is None.
            This is not needed if the predict tasks is not None.
        """
        super().__init__()
        self.name = name
        self.num_processes = num_processes
        self.foldseek_db = Path(foldseek_db)
        self.foldseek_binary = foldseek_binary
        self.skip_specific_ids = set(skip_specific_ids or [])
        self.data = data
        self.plip_original = plip_original
        self.plip_refolded = plip_refolded
        self.small_molecule_plips = small_molecule_plips
        self.diversity_original = diversity_original
        self.diversity_refolded = diversity_refolded
        self.diversity_per_target_original = diversity_per_target_original
        self.diversity_per_target_refolded = diversity_per_target_refolded
        self.novelty_original = novelty_original
        self.novelty_refolded = novelty_refolded
        self.novelty_per_target_original = novelty_per_target_original
        self.novelty_per_target_refolded = novelty_per_target_refolded
        self.delta_sasa_original = delta_sasa_original
        self.delta_sasa_refolded = delta_sasa_refolded
        self.largest_hydrophobic = largest_hydrophobic
        self.compute_lddts = compute_lddts
        self.run_clustering = run_clustering
        self.native = native
        self.sequence_recovery = sequence_recovery
        self.ss_condition = ss_condition
        self.backbone_folding_metrics = backbone_folding_metrics
        self.debug = debug
        self.wandb = wandb
        self.slurm = slurm
        self.diversity_subset = diversity_subset
        self.use_prefolded_dir = use_prefolded_dir
        self.use_prepred_affinitydir = use_prepred_affinitydir
        self.predict_task = predict_task
        self.affinity_task = affinity_task
        self.all_bb_rmsd = all_bb_rmsd
        self.anchors_on = anchors_on
        self.time = 0

        if design_dir is not None:
            self.init_datasets(design_dir)

        # Check that native structure is available if native metrics are desired
        if self.native and not self.data.return_native:
            raise ValueError("native=True requires return_native=True in data config.")
        if self.sequence_recovery and not self.native:
            raise ValueError(
                "sequence_recovery=True requires native structure (native=True)."
            )

        self.bindsite_adherence_thresholds = [3, 4, 5, 6, 7, 8, 9]

    def init_datasets(self, design_dir):
        self.design_dir = Path(design_dir)

        self.data.init_dataset(design_dir, skip_specific_ids=self.skip_specific_ids)
        if self.predict_task is not None:
            self.predict_task.data.init_dataset(
                design_dir, skip_specific_ids=self.skip_specific_ids
            )
            self.predict_task.writer.init_outdir(design_dir)

        if self.affinity_task is not None:
            self.affinity_task.data.init_dataset(
                design_dir, skip_specific_ids=self.skip_specific_ids
            )
            self.affinity_task.writer.init_outdir(design_dir)

        self.des_pdb_dir = Path(design_dir) / "des_pdbs"
        self.des_pdb_dir.mkdir(exist_ok=True, parents=True)
        self.des_refold_pdb_dir = Path(design_dir) / "des_refold_pdbs"
        self.des_refold_pdb_dir.mkdir(exist_ok=True, parents=True)
        self.refold_cif_dir = Path(design_dir) / "refold_cif"
        self.refold_cif_dir.mkdir(exist_ok=True, parents=True)

    def compute_metrics_from_feat(self, feat, suffix=None):
        sample_id = feat["id"]
        path = feat["path"]
        print(path.name)
        if feat["exception"]:
            print(f"Failed obtaining valid features for {path}. Skipping.")
            return None, None

        print("total time: ", time.time() - self.time)
        self.time = time.time()
        res_type_argmax = torch.argmax(feat["res_type"], dim=-1)
        design_seq = res_type_argmax[
            feat["design_mask"].bool() & feat["token_pad_mask"].bool()
        ]

        design_chain_id = feat["asym_id"][
            torch.where(feat["design_mask"].bool() & feat["token_pad_mask"].bool())[0][
                0
            ]
        ].item()
        design_chain_seq = res_type_argmax[design_chain_id == feat["asym_id"]]

        try:
            design_seq = "".join(
                [const.prot_token_to_letter[const.tokens[t]] for t in design_seq]
            )
            design_chain_seq = "".join(
                [const.prot_token_to_letter[const.tokens[t]] for t in design_chain_seq]
            )
        except Exception as e:
            print(
                f"[Error] converting design sequence for {path}: {e}. Skipping this file."
            )
            traceback.print_exc()
            return None, None

        metrics = {
            "id": sample_id,
            "file_name": path.name,
            "designed_sequence": design_seq,
            "designed_chain_sequence": design_chain_seq,
        }
        target_id = re.search(rf"{self.data.cfg.target_id_regex}", sample_id).group(1)

        # Get masks
        design_mask = feat["design_mask"].bool()
        design_resolved_mask = design_mask & feat["token_resolved_mask"].bool()
        target_resolved_mask = ~design_mask & feat["token_resolved_mask"].bool()

        atom_design_resolved_mask = (
            (feat["atom_to_token"].float() @ design_resolved_mask.unsqueeze(-1).float())
            .bool()
            .squeeze()
        )
        atom_target_resolved_mask = (
            (feat["atom_to_token"].float() @ target_resolved_mask.unsqueeze(-1).float())
            .bool()
            .squeeze()
        )
        atom_resolved_mask = feat["atom_resolved_mask"]
        resolved_atoms_design_mask = atom_design_resolved_mask[atom_resolved_mask]

        # Get masks for native structure
        if self.native:
            native_design_mask = feat["native_design_mask"].bool()
            native_target_resolved_mask = (
                ~native_design_mask & feat["native_token_resolved_mask"].bool()
            )
            native_atom_target_resolved_mask = (
                (
                    feat["native_atom_to_token"].float()
                    @ native_target_resolved_mask.unsqueeze(-1).float()
                )
                .bool()
                .squeeze()
            )
        start = time.time()
        # Write cif file to pdb file
        mmcif_parser = PDB.MMCIFParser()
        pdb_parser = PDB.PDBParser()
        pdb_writer = PDB.PDBIO()
        if path.suffix == ".cif":
            biopy_structure = mmcif_parser.get_structure("id", str(path))
        elif path.suffix == ".pdb":
            biopy_structure = pdb_parser.get_structure("id", str(path))
        else:
            raise ValueError("Unsupported file type")
        pdb_writer.set_structure(biopy_structure)
        pdb_buffer = io.StringIO()
        pdb_writer.save(pdb_buffer)
        pdb_buffer.seek(0)  # rewind buffer for reading

        print("parse files and convert to biopy", time.time() - start)

        # add to design_only directory for novelty and hydrophobic path computation
        if (
            self.novelty_original
            or self.novelty_refolded
            or self.novelty_per_target_original
            or self.novelty_per_target_refolded
            or self.largest_hydrophobic
            or self.run_clustering
        ):
            if not suffix is None:
                des_pdb_dir = self.des_pdb_dir / suffix
                des_pdb_dir.mkdir(exist_ok=True, parents=True)
            else:
                des_pdb_dir = self.des_pdb_dir
            des_pdb_path = des_pdb_dir / f"{feat['id']}_des.pdb"
            try:
                save_design_only_structure_to_pdb(
                    atom_design_mask=atom_design_resolved_mask,
                    structure=feat["str_gen"],
                    output_pdb_path=des_pdb_path,
                )

                area = largest_hydrophobic_patch_area(des_pdb_path)
                metrics["design_largest_hydrophobic_patch"] = area

            except Exception as e:
                print(
                    f"[Warning] Could not save design-only structure for {feat['id']}: {e}. Skipping this file."
                )
                traceback.print_exc()
                return None, None

        # Count logging
        metrics["num_prot_tokens"] = (
            (feat["mol_type"] == const.chain_type_ids["PROTEIN"]).sum().item()
        )
        metrics["num_lig_atoms"] = (
            (feat["mol_type"] == const.chain_type_ids["NONPOLYMER"]).sum().item()
        )
        metrics["num_resolved_tokens"] = feat["token_resolved_mask"].sum().item()
        metrics["num_tokens"] = feat["token_pad_mask"].sum().item()
        metrics["num_design"] = feat["design_mask"].sum().item()

        # delta sasa for original
        if self.delta_sasa_original:
            start = time.time()
            delta_sasa_orig, design_sasa_unbound, design_sasa_bound = (
                compute_delta_sasa(pdb_buffer, resolved_atoms_design_mask)
            )
            metrics["delta_sasa_original"] = delta_sasa_orig
            metrics["design_sasa_unbound_original"] = design_sasa_unbound
            metrics["design_sasa_bound_original"] = design_sasa_bound
            print("compute_delta_sasa ", time.time() - start)

        # Plip metrics for original
        start = time.time()
        try:
            if self.plip_original:
                plip_stats = get_plip(
                    pdb_buffer, resolved_atoms_design_mask, self.small_molecule_plips
                )
                metrics.update(plip_stats)
        except Exception as e:
            print(f"[Error] computing plip for {path}: {e}. Skipping this file.")
            traceback.print_exc()
            return None, None
        print("plip original ", time.time() - start)
        breakpoint()
        # Sequence metrics
        design_seq = torch.argmax(feat["res_type"], dim=-1)[design_mask]
        if self.sequence_recovery:
            native_seq = torch.argmax(feat["native_res_type"], dim=-1)[
                native_design_mask
            ]
            metrics["seq_recovery"] = (design_seq == native_seq).float().mean().item()
        for t in const.fake_atom_placements.keys():
            metrics[f"design_{t}"] = (
                (design_seq == const.token_ids[t]).float().mean().item()
            )

        # Secondary structure metrics
        # Compute secondary structure distribution. First get backbone then use pydssp to compute.
        start = time.time()
        bb_design_mask = (
            feat["atom_pad_mask"].bool()
            & atom_design_resolved_mask
            & feat["backbone_mask"].bool()
        )
        bb_coords = feat["coords"][0][bb_design_mask]
        num_atoms = bb_coords.shape[0]
        if num_atoms % 4 != 0:
            msg = f"BB atoms {num_atoms} is not divisible by 4 for {path}"
            print(msg)
            traceback.print_exc()
            return None, None

        bb = bb_coords.reshape(-1, 4, 3)
        ca_coords = bb[:, 1, :]
        if len(bb) > 5:
            try:
                dssp = (
                    torch.zeros(bb.shape[0], dtype=torch.long)
                    if torch.sum(bb_design_mask).item() == 0
                    else pydssp.assign(bb, out_type="index")
                )
                # Secondary structure conditioning metric
                if self.ss_condition:
                    ss_conditioned = feat["ss_type"][design_mask]
                    dssp_adjusted = dssp + 1
                    ss_metrics = compute_ss_metrics(dssp_adjusted, ss_conditioned)
                    metrics.update(ss_metrics)
                metrics["loop"] = (dssp == 0).float().mean().item()
                metrics["helix"] = (dssp == 1).float().mean().item()
                metrics["sheet"] = (dssp == 2).float().mean().item()
            except:
                traceback.print_exc()
                print(f"DSSP failed for {path}.")
                return None, None
        else:
            metrics["loop"] = float("nan")
            metrics["helix"] = float("nan")
            metrics["sheet"] = float("nan")
        print("dssp original ", time.time() - start)

        # Compute RMSD between native (input) and generated conditioning structures.
        # conditioning structure does not have fake atoms, just parse the coordinates and compute rmsd.
        metrics["native_rmsd"] = 0.0
        metrics["native_rmsd_bb"] = 0.0
        if self.native:
            target_coords = feat["coords"][:, atom_target_resolved_mask]
            native_target_coords = feat["native_coords"][
                :, native_atom_target_resolved_mask
            ]
            target_rmsd = compute_rmsd(native_target_coords, target_coords)

            bb_target_coords = feat["coords"][
                :, atom_target_resolved_mask & feat["backbone_mask"].bool()
            ]
            bb_native_target_coords = feat["native_coords"][
                :,
                native_atom_target_resolved_mask & feat["native_backbone_mask"].bool(),
            ]
            bb_target_rmsd = compute_rmsd(bb_native_target_coords, bb_target_coords)

            if self.all_bb_rmsd:
                bb_coords = feat["coords"][:, feat["backbone_mask"].bool()]
                bb_native_coords = feat["native_coords"][
                    :, feat["native_backbone_mask"].bool()
                ]
                bb_rmsd = compute_rmsd(bb_native_coords, bb_coords)
                metrics["native_rmsd_all_bb"] = bb_rmsd.item()

            metrics["native_rmsd"] = target_rmsd.item()
            metrics["native_rmsd_bb"] = bb_target_rmsd.item()

        # Check binding site adherence. For each binding site token, find closest design token
        # token_distances = torch.cdist(feat[""])
        token_distances = torch.cdist(feat["center_coords"], feat["center_coords"])
        binding_site_mask = feat["binding_type"] == 1
        bindsite_design_distances = token_distances[binding_site_mask][
            :, feat["design_mask"]
        ]
        min_bindsite_design_distances = bindsite_design_distances.min(axis=1).values
        for threshold in self.bindsite_adherence_thresholds:
            metrics[f"bindsite_under_{threshold}rmsd"] = (
                (min_bindsite_design_distances < threshold).float().mean().item()
            )
        # Count free Cysteines
        cysteine_mask = (
            torch.argmax(feat["res_type"], dim=-1)
            == const.token_ids["CYS"] & feat["design_mask"]
        )
        cysteine_sulfur_indices = (
            torch.argmax(feat["token_to_rep_atom"].int(), dim=-1)[cysteine_mask]
            + const.ref_atoms["CYS"].index("SG")
            - const.ref_atoms["CYS"].index("CA")
        )
        cysteine_coords = feat["coords"][0][cysteine_sulfur_indices]
        free_cysteines = 0
        dist = torch.cdist(cysteine_coords, cysteine_coords)
        for i in range(dist.shape[0]):
            if dist[i, torch.argsort(dist[i])[1]]>4.0:
                free_cysteines += 1
        metrics["free_cysteines"] = free_cysteines

        # Quality of Cysteine-Cysteine bonds
        bonds = feat["structure_bonds"]
        sulfur_mask = (
            torch.argmax(feat["ref_element"], dim=-1)
            == const.element_to_atomic_num["S"]
        )
        dist = []
        disulfide_bonds = []
        for bond in bonds:
            if (
                bond[6] == const.bond_type_ids["COVALENT"]
                and sulfur_mask[bond[4]]
                and sulfur_mask[bond[5]]
            ):
                disulfide_bonds.append(bond)
        for ds_bond in disulfide_bonds:
            dist.append(
                torch.cdist(
                    feat["coords"][0][ds_bond[4]].unsqueeze(0),
                    feat["coords"][0][ds_bond[5]].unsqueeze(0),
                )
            )
        if len(dist) > 0:
            min_dist = torch.cat(dist).min()
            max_dist = torch.cat(dist).max()
            metrics["disulfide_bond_len_qual"] = [max_dist.item(), min_dist.item()]

        # Folding metrics
        ca_coords_refolded = None
        metrics["native_rmsd_refolded"] = 0.0
        metrics["native_rmsd_bb_refolded"] = 0.0
        if self.predict_task is not None or self.use_prefolded_dir:
            start = time.time()

            folded_path = self.design_dir / const.folding_dirname / f"{feat['id']}.npz"
            if not folded_path.exists():
                print(f"Folded path does not exist. Skipping: {folded_path}")
                return None, None

            folded = np.load(
                self.design_dir / const.folding_dirname / f"{feat['id']}.npz"
            )
            print("load npz ", time.time() - start)

            if (
                not len(folded["res_type"].squeeze()) == len(feat["res_type"])
                or not (folded["res_type"].squeeze() == feat["res_type"].numpy()).all()
            ):
                msg = f"Skipping {path}. Sequences folded['res_type'] and feat['res_type'] were not the same. There must be some inconsistency between the folded output directory and the design_dir. Maybe two processes operating on the same design_dir were launched? Maybe you are using an incorrect prefolded_dir?"
                print(msg)
                return None, None

            start = time.time()
            folding_metrics, folded_coords = get_folding_metrics(
                feat,
                folded,
                diffusion_samples=self.predict_task.predict_args["diffusion_samples"]
                if self.predict_task is not None
                else 1,
                compute_lddts=self.compute_lddts,
            )
            print("folding metrics ", time.time() - start)
            metrics.update(folding_metrics)

            if self.backbone_folding_metrics:
                start = time.time()
                feat_bb = copy.deepcopy(feat)
                feat_bb["atom_resolved_mask"] = feat_bb["atom_resolved_mask"].to(
                    bool
                ) & feat_bb["backbone_mask"].to(bool)
                folding_metrics_bb, folded_coords_bb = get_folding_metrics(
                    feat_bb,
                    folded,
                    diffusion_samples=self.predict_task.predict_args[
                        "diffusion_samples"
                    ]
                    if self.predict_task is not None
                    else 1,
                    compute_lddts=self.compute_lddts,
                    store_confidence=False,  # Not store because same as non-bb confidence metrics
                )
                print("backbone folding metrics ", time.time() - start)
                folding_metrics_bb = {
                    f"bb_{k}": v for k, v in folding_metrics_bb.items()
                }
                metrics.update(folding_metrics_bb)

            # write to refolded cif directory
            feat_out = {}
            for k in feat.keys():
                if k == "coords":
                    feat_out[k] = torch.from_numpy(folded_coords)
                else:
                    feat_out[k] = feat[k]

            refold_atom_target_resolved_mask = (
                (
                    feat_out["atom_to_token"].float()
                    @ target_resolved_mask.unsqueeze(-1).float()
                )
                .bool()
                .squeeze()
            )
            refold_target_coords = feat_out["coords"][
                refold_atom_target_resolved_mask, :
            ][None, ...]

            if self.native:
                refold_target_rmsd = compute_rmsd(
                    native_target_coords,
                    refold_target_coords,
                )

                bb_refold_target_coords = feat_out["coords"][
                    refold_atom_target_resolved_mask & feat_out["backbone_mask"].bool()
                ][None, ...]
                bb_refold_target_rmsd = compute_rmsd(
                    bb_native_target_coords,
                    bb_refold_target_coords,
                )

                metrics["native_rmsd_refolded"] = refold_target_rmsd.item()
                metrics["native_rmsd_bb_refolded"] = bb_refold_target_rmsd.item()

            if self.novelty_refolded or self.novelty_per_target_refolded:
                des_refold_pdb_path = (
                    self.des_refold_pdb_dir / f"{feat['id']}_des_refold.pdb"
                )
                structure, _, _ = Structure.from_feat(feat_out)

                try:
                    save_design_only_structure_to_pdb(
                        atom_design_mask=atom_design_resolved_mask,
                        structure=structure,
                        output_pdb_path=des_refold_pdb_path,
                    )
                except Exception as e:
                    print(
                        f"[Warning] Could not save design-only structure for {feat['id']}: {e}. Skipping this file."
                    )
                    traceback.print_exc()
                    return None, None

            if self.delta_sasa_refolded or self.plip_refolded:
                structure, _, _ = Structure.from_feat(feat_out)
                structure.atoms["bfactor"] = atom_design_resolved_mask[
                    feat_out["atom_pad_mask"].bool()
                ].float()
                cif_text = to_mmcif(structure)
                open(self.refold_cif_dir / f"{feat['id']}.cif", "w").write(cif_text)
                cif_io = io.StringIO(cif_text)
                structure_refold = mmcif_parser.get_structure("RandomID", cif_io)

                pdb_writer.set_structure(structure_refold)
                pdb_buffer_refold = io.StringIO()
                pdb_writer.save(pdb_buffer_refold)
                pdb_buffer_refold.seek(0)

            # delta sasa for refolded
            if self.delta_sasa_refolded:
                delta_sasa_refolded, design_sasa_unbound, design_sasa_bound = (
                    compute_delta_sasa(pdb_buffer_refold, resolved_atoms_design_mask)
                )
                metrics["delta_sasa_refolded"] = delta_sasa_refolded
                metrics["design_sasa_unbound_refolded"] = design_sasa_unbound
                metrics["design_sasa_bound_refolded"] = design_sasa_bound

            start = time.time()
            # plip metrics for refolded structure
            if self.plip_refolded:
                try:
                    plip_stats = get_plip(
                        pdb_buffer_refold,
                        resolved_atoms_design_mask,
                        self.small_molecule_plips,
                    )
                    refolded_stats = {f"{k}_refolded": v for k, v in plip_stats.items()}
                    metrics.update(refolded_stats)
                except Exception as e:
                    print(
                        f"[Error] computing plip refolded for {path}: {e}. Skipping this file."
                    )
                    traceback.print_exc()
                    return None, None
            print("plip refolded ", time.time() - start)
            breakpoint()
            bb_out = feat_out["coords"][bb_design_mask].reshape(-1, 4, 3)
            ca_coords_refolded = bb_out[:, 1, :].cpu()

        # Affinity metrics
        if self.affinity_task is not None or self.use_prepred_affinitydir:
            start = time.time()

            affinity_path = (
                self.design_dir / const.affinity_dirname / f"{feat['id']}.npz"
            )
            if not affinity_path.exists():
                print(f"Affinity path does not exist. Skipping: {affinity_path}")
                return None, None

            affinity = np.load(
                self.design_dir / const.affinity_dirname / f"{feat['id']}.npz"
            )

            for key in const.eval_keys_affinity:
                if key in affinity:
                    metrics[key] = affinity[key].item()

            if "affinity_probability_binary1" in metrics:
                metrics["affinity_probability_binary1>50"] = (
                    metrics["affinity_probability_binary1"] > 0.5
                )
                metrics["affinity_probability_binary1>75"] = (
                    metrics["affinity_probability_binary1"] > 0.75
                )

        # Anchor metrics
        if self.anchors_on:
            well_anchor_dist = 0.0
            for i in range(feat["anchor_element"].shape[0]):
                anchor_coords_sample = feat["anchor_coords"][i]
                anchor_charge = feat["anchor_charge"][i]
                anchor_element = feat["anchor_element"][i]
                same_element_mask = torch.argmax(
                    feat["ref_element"], dim=1
                ) == torch.argmax(anchor_element, dim=-1)
                same_charge_mask = feat["ref_charge"] == anchor_charge
                same_mask = same_element_mask & same_charge_mask
                same_coords = feat["coords"][0][same_mask]
                min_dist = torch.cdist(
                    same_coords, anchor_coords_sample.unsqueeze(0)
                ).min()
                well_anchor_dist += min_dist
            well_anchor_dist /= feat["anchor_element"].shape[0]
            metrics["well_anchored"] = well_anchor_dist.item()

        data = {
            "target_id": target_id,
            "sample_id": sample_id,
            "design_seq": design_seq.cpu(),
            "ca_coords": ca_coords.cpu(),
            "ca_coords_refolded": ca_coords_refolded,
        }
        return metrics, data

    def compute_metrics_from_path(
        self, metadata_path, generated_path, native_path, suffix=None
    ):
        feat = self.data.predict_set.getitem_from_paths(
            metadata_path, generated_path, native_path
        )
        metrics = self.compute_metrics_from_feat(feat, suffix=suffix)
        (self.design_dir / const.folding_dirname / f"{feat['id']}.npz").unlink(
            missing_ok=True
        )
        return metrics

    def compute_metrics(self, idx, suffix=None):
        feat = self.data.predict_set[idx]
        return self.compute_metrics_from_feat(feat, suffix=suffix)

    def compute_diversity(self, all_data, all_metrics):
        avg_metrics = {}
        metrics_data = {}
        folding_metrics = self.predict_task is not None or self.use_prefolded_dir

        # Aggregate alpha carbon positions for diversity eval
        ca_gen = defaultdict(list)
        input_metrics = defaultdict(list)
        ca_refold = defaultdict(list)
        sequences = defaultdict(list)
        for i, data in enumerate(all_data):
            ca_gen[data["target_id"]].append(data["ca_coords"])
            ca_refold[data["target_id"]].append(data["ca_coords_refolded"])
            input_metrics[data["target_id"]].append(all_metrics[i])

            seq = data["design_seq"]
            try:
                seq = "".join(
                    [const.prot_token_to_letter[const.tokens[t]] for t in seq]
                )
                sequences[data["target_id"]].append(seq)
            except KeyError as e:
                print(
                    f"[Error] KeyError '{e.args[0]}' for target_id: {data['target_id']}, sample_id: {data['sample_id']}"
                )
        print(
            f"Number of targets: {len(ca_gen)}. Number of designs: {len(all_metrics)}."
        )

        # vendi score (diversity)
        seqs_filtered = [seq[0] for seq in sequences.values()]
        seq_scores = vendi_sequences(seqs_filtered, self.diversity_subset)
        for k, v in seq_scores.items():
            avg_metrics[k] = round(float(v), 5)

        if self.diversity_original:
            ca_filtered = [ca[0] for ca in ca_gen.values() if len(ca[0]) >= 3]
            metrics_filtered = [
                m[0]
                for ca, m in zip(ca_gen.values(), input_metrics.values())
                if len(ca[0]) >= 3
            ]
            scores = vendi_scores(
                ca_filtered,
                metrics_filtered,
                folding_metrics,
                self.diversity_subset,
                self.compute_lddts,
            )
            for k, v in scores.items():
                avg_metrics[k + "_original"] = round(float(v), 5)

        if self.diversity_per_target_original:
            vendi_per_target = []
            for target_id, ca_list in ca_gen.items():
                seq_list = sequences[target_id]
                ca_filtered = [e for e in ca_list if len(e) >= 3]
                metrics_filtered = [
                    m
                    for ca, m in zip(ca_list, input_metrics[target_id])
                    if len(ca[0]) >= 3
                ]
                count = len(ca_filtered)
                scores = vendi_scores(
                    ca_filtered,
                    all_metrics=metrics_filtered,
                    folding_metrics=folding_metrics,
                    diversity_subset=self.diversity_subset,
                    compute_lddts=self.compute_lddts,
                )
                seq_scores = vendi_sequences(seq_list, self.diversity_subset)
                scores.update(seq_scores)
                scores.update(
                    {
                        "target_id": target_id,
                        "num_filtered_ca": count,
                    }
                )
                vendi_per_target.append(scores)
            df_vendi = pd.DataFrame(vendi_per_target)
            vendi_csv_path = Path(self.design_dir) / f"vendi_per_target_{self.name}.csv"
            df_vendi.to_csv(vendi_csv_path, index=False, float_format="%.5f")

            for k in vendi_per_target[0].keys():
                if isinstance(vendi_per_target[0][k], numbers.Number):
                    vendis = [e[k] for e in vendi_per_target if not np.isnan(e[k])]
                    avg_metrics[k + "_mean_per_target"] = float(np.mean(vendis))
                    avg_metrics[k + "_median_per_target"] = float(np.median(vendis))

                    metrics_data[k] = vendis

        if self.diversity_refolded and (
            self.predict_task is not None or self.use_prefolded_dir
        ):
            sample0 = [ca[0] for ca in ca_refold.values() if ca[0].shape[0] >= 3]
            metrics_filtered = [
                m[0]
                for ca, m in zip(ca_refold.values(), input_metrics.values())
                if len(ca[0]) >= 3
            ]
            scores = vendi_scores(
                sample0,
                metrics_filtered,
                folding_metrics,
                self.diversity_subset,
                self.compute_lddts,
                backbone_folding_metrics=self.backbone_folding_metrics,
            )

            for k, v in scores.items():
                avg_metrics[k + "_refolded"] = round(float(v), 5)

        return avg_metrics, metrics_data

    def compute_novelty(self, suffix=None):
        avg_metrics = {}
        metrics_data = {}

        des_pdb_dir = Path(self.des_pdb_dir)
        design_dir = Path(self.design_dir)
        des_refold_pdb_dir = Path(self.des_refold_pdb_dir)
        if not suffix is None:
            des_pdb_dir = des_pdb_dir / suffix
            design_dir = design_dir / suffix
            des_refold_pdb_dir = des_refold_pdb_dir / suffix
            design_dir.mkdir(exist_ok=True, parents=True)

        # novelty original
        if self.novelty_original or self.novelty_per_target_original:
            novelty_original_df = compute_novelty_foldseek(
                indir=des_pdb_dir,
                outdir=design_dir,
                reference_db=self.foldseek_db,
                files=[str(p) for p in des_pdb_dir.glob("*.pdb")],
                foldseek_binary=self.foldseek_binary,
            )

        if self.novelty_original:
            avg_metrics["novelty_original"] = round(
                float(novelty_original_df["novelty"].mean()), 5
            )

        if self.novelty_per_target_original:
            novelty_original_df["target_id"] = novelty_original_df["query"].apply(
                lambda x: "_".join(x.split("_")[3:5])
            )
            nov_df = (
                novelty_original_df.groupby("target_id")["novelty"].mean().reset_index()
            )
            nov_csv = Path(design_dir) / f"novelty_per_target_original_{self.name}.csv"
            nov_df.to_csv(nov_csv, index=False, float_format="%.5f")
            avg_metrics["mean_novelty_per_target_original"] = (
                nov_df["novelty"].mean().round(5)
            )
            avg_metrics["median_novelty_per_target_original"] = (
                nov_df["novelty"].median().round(5)
            )
            metrics_data["nov_df"] = nov_df

        # Novelty refolded
        if (self.novelty_refolded or self.novelty_per_target_refolded) and (
            self.predict_task is not None or self.use_prefolded_dir
        ):
            novelty_refolded_df = compute_novelty_foldseek(
                indir=des_refold_pdb_dir,
                outdir=Path(design_dir),
                reference_db=self.foldseek_db,
                files=[str(p) for p in des_refold_pdb_dir.glob("*.pdb")],
                foldseek_binary=self.foldseek_binary,
            )

        if self.novelty_refolded and (
            self.predict_task is not None or self.use_prefolded_dir
        ):
            avg_metrics["novelty_refolded"] = round(
                float(novelty_refolded_df["novelty"].mean()), 5
            )

        if self.novelty_per_target_refolded and (
            self.predict_task is not None or self.use_prefolded_dir
        ):
            novelty_refolded_df["target_id"] = novelty_refolded_df["query"].apply(
                lambda x: "_".join(x.split("_")[3:5])
            )
            nov_df_refold = (
                novelty_refolded_df.groupby("target_id")["novelty"].mean().reset_index()
            )
            nov_csv = Path(design_dir) / f"novelty_per_target_refolded_{self.name}.csv"
            nov_df_refold.to_csv(nov_csv, index=False, float_format="%.5f")
            avg_metrics["mean_novelty_per_target_refolded"] = (
                nov_df_refold["novelty"].mean().round(5)
            )
            avg_metrics["median_novelty_per_target_refolded"] = round(
                nov_df_refold["novelty"].median(), 5
            )
            metrics_data["nov_df_refold"] = nov_df_refold
        return avg_metrics, metrics_data

    def make_histograms(self, all_metrics):
        df = pd.DataFrame(all_metrics)

        # Make aggregate histograms
        histograms = {}
        cols = [
            "delta_sasa_refolded",
            "rmsd",
            "iptm",
            "ptm",
            "rmsd",
            "design_ptm",
            "min_interaction_pae",
            "helix",
            "sheet",
            "loop",
            "plip_pistacking",
            "plip_saltbridge",
            "plip_pication",
            "plip_hydrophobic",
            "plip_hbonds",
            "design_sasa_bound_original",
            "design_sasa_unbound_original",
            "delta_sasa_original",
            "num_design",
            "precision_loop",
            "recall_loop",
            "precision_helix",
            "recall_helix",
            "precision_sheet",
            "recall_sheet",
            "accuracy_overall",
        ]
        for col in cols:
            if col in df.columns:
                histograms["hist" + col] = make_histogram(df, col)

        # make per target histograms
        df["target_id"] = df["id"].apply(lambda x: "_".join(x.split("_")[3:5]))
        per_target_df = df.groupby("target_id").mean(numeric_only=True).reset_index()
        cols += ["rmsd<2.5", "designability_rmsd_2"]
        if self.compute_lddts:
            cols += [
                "designability_lddt_90",
                "designability_lddt_85",
                "designability_lddt_80",
                "designability_lddt_75",
                "designability_lddt_70",
                "designability_lddt_65",
                "designability_lddt_60",
            ]
        for col in cols:
            if col in df.columns:
                # Per target histograms
                histograms["per_target" + col] = make_histogram(per_target_df, col)
        return df, histograms

    def run_foldseek_clustering(self, df: pd.DataFrame, suffix=None) -> pd.DataFrame:
        des_pdb_dir = self.des_pdb_dir / suffix if suffix else self.des_pdb_dir
        design_dir = Path(self.design_dir) / suffix if suffix else Path(self.design_dir)

        cluster_output_dir = design_dir / "foldseek_cluster"
        cluster_output_dir.mkdir(parents=True, exist_ok=True)

        cluster_prefix = cluster_output_dir / "cluster"
        tmp_dir = cluster_output_dir / "tmp"

        min_num_design = int(df["num_design"].min())
        cmd = [
            self.foldseek_binary,
            "easy-cluster",
            str(des_pdb_dir),
            str(cluster_prefix),
            str(tmp_dir),
            "--alignment-type",
            "1",
            "--cov-mode",
            "0",
            "--min-seq-id",
            "0",
            "--tmscore-threshold",
            "0.5",
        ]
        if min_num_design < 20:
            msg = f"[FoldSeek] Using --kmer-per-seq {2} due to short designs."
            print(msg)
            cmd += ["--kmer-per-seq", str(2)]

        try:
            subprocess.run(cmd, check=True)

            df_cluster = pd.read_csv(
                str(cluster_prefix) + "_cluster.tsv",
                sep="\t",
                header=None,
                names=["file", "clusters_05_tmscore"],
            )
            df_cluster["file"] = df_cluster["file"].apply(lambda x: Path(x).stem)

            df = df.merge(df_cluster, left_on="id", right_on="file", how="left").drop(
                columns=["file"]
            )
        except Exception as e:
            msg = f"Structure clustering was unsuccessful. No cluster labels are added to the dataframe / csv file output."
            print(msg)
        return df

    def run_foldseek_sequence_clustering(
        self, df: pd.DataFrame, suffix=None
    ) -> pd.DataFrame:
        des_pdb_dir = self.des_pdb_dir / suffix if suffix else self.des_pdb_dir
        design_dir = Path(self.design_dir) / suffix if suffix else Path(self.design_dir)

        cluster_output_dir = design_dir / "foldseek_seq_cluster"
        cluster_output_dir.mkdir(parents=True, exist_ok=True)

        cluster_prefix = cluster_output_dir / "seqcluster"
        tmp_dir = cluster_output_dir / "tmp"

        min_num_design = int(df["num_design"].min())
        cmd = [
            self.foldseek_binary,
            "easy-cluster",
            str(des_pdb_dir),
            str(cluster_prefix),
            str(tmp_dir),
            "--alignment-type",
            "2",  # sequence-based clustering
            "--cov-mode",
            "0",
            "--min-seq-id",
            "0.7",
        ]
        if min_num_design < 20:
            print(f"[FoldSeek] Using --kmer-per-seq 2 due to short designs.")
            cmd += ["--kmer-per-seq", "2"]
        try:
            subprocess.run(cmd, check=True)

            df_cluster = pd.read_csv(
                str(cluster_prefix) + "_cluster.tsv",
                sep="\t",
                header=None,
                names=["file", "cluster_07_seqidentity"],
            )
            df_cluster["file"] = df_cluster["file"].apply(lambda x: Path(x).stem)

            df = df.merge(df_cluster, left_on="id", right_on="file", how="left").drop(
                columns=["file"]
            )
        except Exception as e:
            msg = f"Sequence clustering was unsuccessful. No cluster labels are added to the dataframe / csv file output."
            print(msg)
        return df

    @torch.no_grad()
    def run(self, config=None) -> tuple[Dict, Dict]:
        # Run affinity GPU evals
        if self.affinity_task is not None and not self.use_prepred_affinitydir:
            self.affinity_task.run()

        # Run folding GPU evals
        if self.predict_task is not None and not self.use_prefolded_dir:
            self.predict_task.run()

        # Run other evals
        if not torch.distributed.is_initialized() or torch.distributed.get_rank() == 0:
            return self.run_cpu_evals()

    def run_cpu_evals(self) -> tuple[Dict, Dict]:
        # Compute per instance metrics and gather predicted coordinates
        all_metrics = []
        all_data = []
        failures = 0
        # The rdkit thing is necessary to make multiprocessing with the rdkit molecules work.
        rdkit.Chem.SetDefaultPickleProperties(rdkit.Chem.PropertyPickleOptions.AllProps)
        num_processes = min(self.num_processes, multiprocessing.cpu_count())
        if num_processes == 1:
            for idx in tqdm(range(len(self.data.predict_set))):
                metrics, data = self.compute_metrics(idx)
                if metrics is not None:
                    all_metrics.append(metrics)
                    all_data.append(data)
                else:
                    failures += 1
        else:
            with multiprocessing.Pool(num_processes) as pool:  # noqa: SIM117
                with tqdm(total=len(self.data.predict_set)) as pbar:
                    for metrics, data in pool.imap_unordered(
                        self.compute_metrics, list(range(len(self.data.predict_set)))
                    ):
                        if metrics is not None:
                            all_metrics.append(metrics)
                            all_data.append(data)
                        else:
                            failures += 1
        print(f"Compute metrics failures {failures}. Successes {len(all_metrics)}")

        if len(all_metrics) == 0:
            raise ValueError("No metrics computed")

        # Write individual metrics to disc.
        df = pd.DataFrame(all_metrics)
        if self.run_clustering:
            df = self.run_foldseek_clustering(df)
            df = self.run_foldseek_sequence_clustering(df)

        csv_path = Path(self.design_dir) / f"aggregate_metrics_{self.name}.csv"
        df.to_csv(csv_path, float_format="%.5f", index=False)

        # Store ca coords and seq in a separate csv
        data_rows = []
        for data in all_data:
            data_rows.append(
                {
                    "id": data["sample_id"],
                    "target_id": data["target_id"],
                    "sequence": "".join(
                        [
                            const.prot_token_to_letter[const.tokens[t]]
                            for t in data["design_seq"]
                        ]
                    ),
                    "ca_coords": json.dumps(data["ca_coords"].numpy().tolist()),
                }
            )

        ca_seq_df = pd.DataFrame(data_rows)
        ca_seq_df.to_pickle(
            Path(self.design_dir) / "ca_coords_sequences.pkl.gz", compression="gzip"
        )  # or "bz2", "xz", None

        # Compute per target metrics
        df["target_id"] = df["id"].apply(lambda x: "_".join(x.split("_")[3:5]))
        per_target_df = df.groupby("target_id").mean(numeric_only=True).reset_index()
        csv_path = Path(self.design_dir) / f"per_target_metrics_{self.name}.csv"
        per_target_df.to_csv(csv_path, float_format="%.5f", index=False)

        avg_metrics = df.mean(numeric_only=True).round(5).to_dict()
        avg_metrics["num_targets"] = len(all_metrics)
        if self.run_clustering:
            if "cluster_07_seqidentity" in df.columns:
                avg_metrics["num_cluster_07_seqidentity"] = len(
                    np.unique(df["cluster_07_seqidentity"].to_numpy())
                )
            if "num_clusters_05_tmscore" in df.columns:
                avg_metrics["num_clusters_05_tmscore"] = len(
                    np.unique(df["clusters_05_tmscore"].to_numpy())
                )

        print("computing diversity")
        diversity_metrics, diversity_data = self.compute_diversity(
            all_data, all_metrics
        )
        for k in diversity_metrics:
            avg_metrics[k] = diversity_metrics[k]

        print("computing novelty")
        novelty_metrics, novelty_data = self.compute_novelty()
        for k in novelty_metrics:
            avg_metrics[k] = novelty_metrics[k]

        _, histograms = self.make_histograms(all_metrics)

        # Log to Wandb
        if self.wandb is not None and not self.debug:
            print("\nOverall average metrics:", avg_metrics)

            # Make residue distribution plot
            native_stats = np.load("data/native_statistics.npz")
            design_freqs = np.array(
                [avg_metrics[f"design_{k}"] for k in const.fake_atom_placements.keys()]
            )
            x = np.arange(len(const.fake_atom_placements.keys()))
            width = 0.15
            fig_res, ax = plt.subplots(figsize=(12, 6))
            ax.bar(x - width / 2, design_freqs, width, label="Design frequency")
            ax.bar(
                x + width / 2, native_stats["res_dist"], width, label="Data frequency"
            )
            ax.set_xlabel("Res Type")
            ax.set_ylabel("Probability")
            ax.set_title("Res Type distributions")
            ax.set_xticks(x)
            ax.set_xticklabels(const.fake_atom_placements.keys())
            ax.legend()
            ax.grid(True, which="both", axis="y", linestyle="--", linewidth=0.5)
            plt.tight_layout()
            fig_res.savefig(Path(self.design_dir) / "res_type_distribution.png")

            # Make secondary structure distribution plot
            ss_dist = np.array(
                [avg_metrics["loop"], avg_metrics["helix"], avg_metrics["sheet"]]
            )
            x = np.arange(3)
            width = 0.15
            fig_ss, ax = plt.subplots(figsize=(12, 6))
            ax.bar(x - width / 2, ss_dist, width, label="Designed")
            ax.bar(x + width / 2, native_stats["ss_dist"], width, label="Native data")
            ax.set_xlabel("Secondary Structure type")
            ax.set_ylabel("Frequency")
            ax.set_title("Secondary Structure distributions")
            ax.set_xticks(x)
            ax.set_xticklabels(["loop", "helix", "sheet"])
            ax.legend()
            ax.grid(True, which="both", axis="y", linestyle="--", linewidth=0.5)
            plt.tight_layout()
            fig_ss.savefig(
                Path(self.design_dir) / "secondary_structure_distribution.png"
            )

            wandb.init(name=self.name, **self.wandb)
            wandb.log(avg_metrics)
            wandb.log({"res_dist": wandb.Image(fig_res)})
            wandb.log({"ss_dist": wandb.Image(fig_ss)})

            # Log histograms

            for name, fig in histograms.items():
                wandb.log({f"{name}_hist": wandb.Image(fig)})

            # plot per target vendiscore histogram
            if self.diversity_per_target_original:
                fig, ax = plt.subplots(figsize=(6, 4))
                ax.hist(
                    diversity_data["vendi_tm_fixed"], bins=50, color="blue", alpha=0.7
                )
                ax.set_title("Vendi Score Per Target Distribution")
                ax.set_xlabel("Vendi Score")
                ax.set_ylabel("Count")
                plt.tight_layout()
                wandb.log({"vendi_per_target": wandb.Image(fig)})
                plt.close(fig)

            if self.novelty_per_target_original:
                fig, ax = plt.subplots(figsize=(6, 4))
                ax.hist(
                    novelty_data["nov_df"]["novelty"],
                    bins=50,
                    color="blue",
                    alpha=0.7,
                )
                ax.set_title("Novelty Per Target Original Distribution")
                ax.set_xlabel("Novelty")
                ax.set_ylabel("Count")
                plt.tight_layout()
                wandb.log({"novelty_per_target_original_hist": wandb.Image(fig)})
                plt.close(fig)

            if self.novelty_per_target_refolded and (
                self.predict_task is not None or self.use_prefolded_dir
            ):
                fig, ax = plt.subplots(figsize=(6, 4))
                ax.hist(
                    novelty_data["nov_df_refold"]["novelty"],
                    bins=50,
                    color="blue",
                    alpha=0.7,
                )
                ax.set_title("Novelty Per Target Refolded Distribution")
                ax.set_xlabel("Novelty")
                ax.set_ylabel("Count")
                plt.tight_layout()
                wandb.log({"novelty_per_target_refolded_hist": wandb.Image(fig)})
                plt.close(fig)

        return avg_metrics, histograms
