import itertools
import pickle
import string
from pathlib import Path
import random
from typing import Dict, Iterator

import numpy as np
import torch
from rdkit.Chem import RWMol, Atom, Conformer
from rdkit.Chem import Mol, AllChem, rdDetermineBonds
from tqdm import tqdm
import json

from foldeverything.data import const
from foldeverything.data.pad import pad_dim
from foldeverything.model.loss.confidence import lddt_dist
from foldeverything.utils.iterator import product
from foldeverything.data.data import elem_from_name
# For distance-based bond order inference
from foldeverything.data.bond_analyze import get_bond_order


def load_molecules(moldir: str, molecules: list[str]) -> dict[str, Mol]:
    """Load the given input data.

    Parameters
    ----------
    moldir : str
        The path to the molecules directory.
    molecules : list[str]
        The molecules to load.

    Returns
    -------
    dict[str, Mol]
        The loaded molecules.
    """
    loaded_mols = {}
    for molecule in molecules:
        path = Path(moldir) / f"{molecule}.pkl"
        with path.open("rb") as f:
            loaded_mols[molecule] = pickle.load(f)  # noqa: S301
    return loaded_mols


def load_canonicals(moldir: str) -> dict[str, Mol]:
    """Load the given input data.

    Parameters
    ----------
    moldir : str
        The molecules to load.

    Returns
    -------
    dict[str, Mol]
        The loaded molecules.

    """
    return load_molecules(moldir, const.canonical_tokens)


def load_all_molecules(moldir: str) -> dict[str, Mol]:
    """Load the given input data.

    Parameters
    ----------
    moldir : str
        The path to the molecules directory.
    molecules : list[str]
        The molecules to load.

    Returns
    -------
    dict[str, Mol]
        The loaded molecules.

    """
    loaded_mols = {}
    files = list(Path(moldir).glob("*.pkl"))
    for path in tqdm(files, total=len(files), desc="Loading molecules", leave=False):
        mol_name = path.stem
        with path.open("rb") as f:
            loaded_mols[mol_name] = pickle.load(f)  # noqa: S301
    return loaded_mols


def get_symmetries(mols: dict[str, Mol]) -> Dict:  # noqa: PLR0912
    """Create a dictionary for the ligand symmetries.

    Parameters
    ----------
    path : str
        The path to the ligand symmetries.

    Returns
    -------
    Dict
        The ligand symmetries.

    """
    symmetries = {}
    for key, mol in mols.items():
        try:
            sym = pickle.loads(bytes.fromhex(mol.GetProp("symmetries")))  # noqa: S301

            if mol.HasProp("pb_edge_index"):
                edge_index = pickle.loads(
                    bytes.fromhex(mol.GetProp("pb_edge_index"))
                ).astype(np.int64)  # noqa: S301
                lower_bounds = pickle.loads(
                    bytes.fromhex(mol.GetProp("pb_lower_bounds"))
                )  # noqa: S301
                upper_bounds = pickle.loads(
                    bytes.fromhex(mol.GetProp("pb_upper_bounds"))
                )  # noqa: S301
                bond_mask = pickle.loads(bytes.fromhex(mol.GetProp("pb_bond_mask")))  # noqa: S301
                angle_mask = pickle.loads(bytes.fromhex(mol.GetProp("pb_angle_mask")))  # noqa: S301
            else:
                edge_index = np.empty((2, 0), dtype=np.int64)
                lower_bounds = np.array([], dtype=np.float32)
                upper_bounds = np.array([], dtype=np.float32)
                bond_mask = np.array([], dtype=np.float32)
                angle_mask = np.array([], dtype=np.float32)

            if mol.HasProp("chiral_atom_index"):
                chiral_atom_index = pickle.loads(
                    bytes.fromhex(mol.GetProp("chiral_atom_index"))
                ).astype(np.int64)
                chiral_check_mask = pickle.loads(
                    bytes.fromhex(mol.GetProp("chiral_check_mask"))
                ).astype(np.int64)
                chiral_atom_orientations = pickle.loads(
                    bytes.fromhex(mol.GetProp("chiral_atom_orientations"))
                )
            else:
                chiral_atom_index = np.empty((4, 0), dtype=np.int64)
                chiral_check_mask = np.array([], dtype=bool)
                chiral_atom_orientations = np.array([], dtype=bool)

            if mol.HasProp("stereo_bond_index"):
                stereo_bond_index = pickle.loads(
                    bytes.fromhex(mol.GetProp("stereo_bond_index"))
                ).astype(np.int64)
                stereo_check_mask = pickle.loads(
                    bytes.fromhex(mol.GetProp("stereo_check_mask"))
                ).astype(np.int64)
                stereo_bond_orientations = pickle.loads(
                    bytes.fromhex(mol.GetProp("stereo_bond_orientations"))
                )
            else:
                stereo_bond_index = np.empty((4, 0), dtype=np.int64)
                stereo_check_mask = np.array([], dtype=bool)
                stereo_bond_orientations = np.array([], dtype=bool)

            if mol.HasProp("aromatic_5_ring_index"):
                aromatic_5_ring_index = pickle.loads(
                    bytes.fromhex(mol.GetProp("aromatic_5_ring_index"))
                ).astype(np.int64)
            else:
                aromatic_5_ring_index = np.empty((5, 0), dtype=np.int64)
            if mol.HasProp("aromatic_6_ring_index"):
                aromatic_6_ring_index = pickle.loads(
                    bytes.fromhex(mol.GetProp("aromatic_6_ring_index"))
                ).astype(np.int64)
            else:
                aromatic_6_ring_index = np.empty((6, 0), dtype=np.int64)
            if mol.HasProp("planar_double_bond_index"):
                planar_double_bond_index = pickle.loads(
                    bytes.fromhex(mol.GetProp("planar_double_bond_index"))
                ).astype(np.int64)
            else:
                planar_double_bond_index = np.empty((6, 0), dtype=np.int64)

            atom_names = [atom.GetProp("name") for atom in mol.GetAtoms()]
            symmetries[key] = (
                sym,
                atom_names,
                edge_index,
                lower_bounds,
                upper_bounds,
                bond_mask,
                angle_mask,
                chiral_atom_index,
                chiral_check_mask,
                chiral_atom_orientations,
                stereo_bond_index,
                stereo_check_mask,
                stereo_bond_orientations,
                aromatic_5_ring_index,
                aromatic_6_ring_index,
                planar_double_bond_index,
            )
        except Exception as e:  # noqa: BLE001, PERF203, S110
            pass

    return symmetries


def compute_symmetry_idx_dictionary(data):
    # Compute the symmetry index dictionary
    total_count = 0
    all_coords = []
    for i, chain in enumerate(data.chains):
        chain.start_idx = total_count
        for j, token in enumerate(chain.tokens):
            token.start_idx = total_count - chain.start_idx
            all_coords.extend(
                [[atom.coords.x, atom.coords.y, atom.coords.z] for atom in token.atoms]
            )
            total_count += len(token.atoms)
    return all_coords


def get_current_idx_list(data):
    idx = []
    for chain in data.chains:
        if chain.in_crop:
            for token in chain.tokens:
                if token.in_crop:
                    idx.extend(
                        [
                            chain.start_idx + token.start_idx + i
                            for i in range(len(token.atoms))
                        ]
                    )
    return idx


def all_different_after_swap(l):
    final = [s[-1] for s in l]
    return len(final) == len(set(final))


def minimum_lddt_symmetry_coords(
    coords: torch.Tensor,
    feats: dict,
    index_batch: int,
):
    all_coords = feats["all_coords"][index_batch].unsqueeze(0).to(coords)
    all_resolved_mask = (
        feats["all_resolved_mask"][index_batch].to(coords).to(torch.bool)
    )
    crop_to_all_atom_map = (
        feats["crop_to_all_atom_map"][index_batch].to(coords).to(torch.long)
    )
    chain_symmetries = feats["chain_swaps"][index_batch]
    amino_acids_symmetries = feats["amino_acids_symmetries"][index_batch]
    ligand_symmetries = feats["ligand_symmetries"][index_batch]

    dmat_predicted = torch.cdist(
        coords[:, : len(crop_to_all_atom_map)], coords[:, : len(crop_to_all_atom_map)]
    )

    # Check best symmetry on chain swap
    best_true_coords = all_coords[:, crop_to_all_atom_map].clone()
    best_true_resolved_mask = all_resolved_mask[crop_to_all_atom_map].clone()
    best_lddt = -1.0
    for c in chain_symmetries:
        true_all_coords = all_coords.clone()
        true_all_resolved_mask = all_resolved_mask.clone()
        for start1, end1, start2, end2, chainidx1, chainidx2 in c:
            true_all_coords[:, start1:end1] = all_coords[:, start2:end2]
            true_all_resolved_mask[start1:end1] = all_resolved_mask[start2:end2]

        true_coords = true_all_coords[:, crop_to_all_atom_map]
        true_resolved_mask = true_all_resolved_mask[crop_to_all_atom_map]
        dmat_true = torch.cdist(true_coords, true_coords)
        pair_mask = (
            true_resolved_mask[:, None]
            * true_resolved_mask[None, :]
            * (1 - torch.eye(len(true_resolved_mask))).to(true_resolved_mask)
        )

        lddt = lddt_dist(
            dmat_predicted, dmat_true, pair_mask, cutoff=15.0, per_atom=False
        )[0]
        lddt = lddt.item()

        if lddt > best_lddt and torch.sum(true_resolved_mask) > 3:
            best_lddt = lddt
            best_true_coords = true_coords
            best_true_resolved_mask = true_resolved_mask

    # atom symmetries (nucleic acid and protein residues), resolved greedily without recomputing alignment
    true_coords = best_true_coords.clone()
    true_resolved_mask = best_true_resolved_mask.clone()
    for symmetric_amino_or_lig in amino_acids_symmetries + ligand_symmetries:
        best_lddt_improvement = 0.0

        indices = set()
        for c in symmetric_amino_or_lig:
            for i, j in c:
                indices.add(i)
        indices = sorted(list(indices))
        indices = torch.from_numpy(np.asarray(indices)).to(true_coords.device).long()
        pred_coords_subset = coords[:, : len(crop_to_all_atom_map)][:, indices]
        sub_dmat_pred = torch.cdist(
            coords[:, : len(crop_to_all_atom_map)], pred_coords_subset
        )

        for c in symmetric_amino_or_lig:
            # starting from greedy best, try to swap the atoms
            new_true_coords = true_coords.clone()
            new_true_resolved_mask = true_resolved_mask.clone()
            for i, j in c:
                new_true_coords[:, i] = true_coords[:, j]
                new_true_resolved_mask[i] = true_resolved_mask[j]

            true_coords_subset = true_coords[:, indices]
            new_true_coords_subset = new_true_coords[:, indices]

            sub_dmat_true = torch.cdist(true_coords, true_coords_subset)
            sub_dmat_new_true = torch.cdist(new_true_coords, new_true_coords_subset)

            sub_true_pair_lddt = (
                true_resolved_mask[:, None] * true_resolved_mask[None, indices]
            )
            sub_true_pair_lddt[indices] = (
                sub_true_pair_lddt[indices]
                * (1 - torch.eye(len(indices))).to(sub_true_pair_lddt).bool()
            )

            sub_new_true_pair_lddt = (
                new_true_resolved_mask[:, None] * new_true_resolved_mask[None, indices]
            )
            sub_new_true_pair_lddt[indices] = (
                sub_new_true_pair_lddt[indices]
                * (1 - torch.eye(len(indices))).to(sub_true_pair_lddt).bool()
            )

            lddt, total = lddt_dist(
                sub_dmat_pred,
                sub_dmat_true,
                sub_true_pair_lddt,
                cutoff=15.0,
                per_atom=False,
            )
            new_lddt, new_total = lddt_dist(
                sub_dmat_pred,
                sub_dmat_new_true,
                sub_new_true_pair_lddt,
                cutoff=15.0,
                per_atom=False,
            )

            lddt_improvement = new_lddt - lddt

            if lddt_improvement > best_lddt_improvement:
                best_true_coords = new_true_coords
                best_true_resolved_mask = new_true_resolved_mask
                best_lddt_improvement = lddt_improvement

        # greedily update best coordinates after each amino acid
        true_coords = best_true_coords.clone()
        true_resolved_mask = best_true_resolved_mask.clone()

    # Recomputing alignment
    true_coords = pad_dim(true_coords, 1, coords.shape[1] - true_coords.shape[1])
    true_resolved_mask = pad_dim(
        true_resolved_mask,
        0,
        coords.shape[1] - true_resolved_mask.shape[0],
    )

    return true_coords, true_resolved_mask.unsqueeze(0)


def compute_single_distogram_loss(pred, target, mask):
    # Compute the distogram loss
    errors = -1 * torch.sum(
        target * torch.nn.functional.log_softmax(pred, dim=-1),
        dim=-1,
    )
    denom = 1e-5 + torch.sum(mask, dim=(-1, -2))
    mean = errors * mask
    mean = torch.sum(mean, dim=-1)
    mean = mean / denom[..., None]
    batch_loss = torch.sum(mean, dim=-1)
    global_loss = torch.mean(batch_loss)
    return global_loss


def minimum_lddt_symmetry_dist(
    pred_distogram: torch.Tensor,
    feats: dict,
    index_batch: int,
):
    # Note: for now only ligand symmetries are resolved

    disto_target = feats["disto_target"][index_batch]
    mask = feats["token_disto_mask"][index_batch]
    mask = mask[None, :] * mask[:, None]
    mask = mask * (1 - torch.eye(mask.shape[1])).to(disto_target)

    coords = feats["coords"][index_batch]

    ligand_symmetries = feats["ligand_symmetries"][index_batch]
    atom_to_token_map = feats["atom_to_token"][index_batch].argmax(dim=-1)

    # atom symmetries, resolved greedily without recomputing alignment
    for symmetric_amino_or_lig in ligand_symmetries:
        best_c, best_disto, best_loss_improvement = None, None, 0.0
        for c in symmetric_amino_or_lig:
            # starting from greedy best, try to swap the atoms
            new_disto_target = disto_target.clone()
            indices = []

            # fix the distogram by replacing first the columns then the rows
            disto_temp = new_disto_target.clone()
            for i, j in c:
                new_disto_target[:, atom_to_token_map[i]] = disto_temp[
                    :, atom_to_token_map[j]
                ]
                indices.append(atom_to_token_map[i].item())
            disto_temp = new_disto_target.clone()
            for i, j in c:
                new_disto_target[atom_to_token_map[i], :] = disto_temp[
                    atom_to_token_map[j], :
                ]

            indices = (
                torch.from_numpy(np.asarray(indices)).to(disto_target.device).long()
            )

            pred_distogram_subset = pred_distogram[:, indices]
            disto_target_subset = disto_target[:, indices]
            new_disto_target_subset = new_disto_target[:, indices]
            mask_subset = mask[:, indices]

            loss = compute_single_distogram_loss(
                pred_distogram_subset, disto_target_subset, mask_subset
            )
            new_loss = compute_single_distogram_loss(
                pred_distogram_subset, new_disto_target_subset, mask_subset
            )
            loss_improvement = (loss - new_loss) * len(indices)

            if loss_improvement > best_loss_improvement:
                best_c = c
                best_disto = new_disto_target
                best_loss_improvement = loss_improvement

        # greedily update best coordinates after each ligand
        if best_loss_improvement > 0:
            disto_target = best_disto.clone()
            old_coords = coords.clone()
            for i, j in best_c:
                coords[:, i] = old_coords[:, j]

    # update features to be used in diffusion and in distogram loss
    feats["disto_target"][index_batch] = disto_target
    feats["coords"][index_batch] = coords
    return


def compute_all_coords_mask(structure):
    # Compute all coords, crop mask and add start_idx to structure
    total_count = 0
    all_coords = []
    all_coords_crop_mask = []
    all_resolved_mask = []
    for i, chain in enumerate(structure.chains):
        chain.start_idx = total_count
        for j, token in enumerate(chain.tokens):
            token.start_idx = total_count - chain.start_idx
            all_coords.extend(
                [[atom.coords.x, atom.coords.y, atom.coords.z] for atom in token.atoms]
            )
            all_coords_crop_mask.extend(
                [token.in_crop for _ in range(len(token.atoms))]
            )
            all_resolved_mask.extend(
                [token.is_present for _ in range(len(token.atoms))]
            )
            total_count += len(token.atoms)
    if len(all_coords_crop_mask) != len(all_resolved_mask):
        pass
    return all_coords, all_coords_crop_mask, all_resolved_mask


def get_chain_symmetries(
    cropped, backbone_only, atom14, atom14_geometric, atom37, max_n_symmetries=100
):
    # get all coordinates and resolved mask
    structure = cropped.structure
    all_coords = []
    all_resolved_mask = []
    original_atom_idx = []
    chain_atom_idx = []
    chain_atom_num = []
    chain_in_crop = []
    chain_asym_id = []
    new_atom_idx = 0

    for chain in structure.chains:
        atom_idx, atom_num = (
            chain["atom_idx"],  # Global index of first atom in the chain
            chain["atom_num"],  # Number of atoms in the chain
        )

        # compute coordinates and resolved mask
        resolved_mask = structure.atoms["is_present"][
            atom_idx : atom_idx + atom_num
        ]  # Whether each atom in the chain is actually resolved

        # ensemble_atom_starts = [structure.ensemble[idx]["atom_coord_idx"] for idx in cropped.ensemble_ref_idxs]
        # coords = np.array(
        #    [structure.coords[ensemble_atom_start + atom_idx: ensemble_atom_start + atom_idx + atom_num]["coords"] for
        #     ensemble_atom_start in ensemble_atom_starts])

        coords = structure.atoms["coords"][atom_idx : atom_idx + atom_num]

        in_crop = False
        for token in cropped.tokens:
            if token["asym_id"] == chain["asym_id"]:
                in_crop = True
                break

        all_coords.append(coords)
        all_resolved_mask.append(resolved_mask)
        original_atom_idx.append(atom_idx)
        chain_atom_idx.append(new_atom_idx)
        chain_atom_num.append(atom_num)
        chain_in_crop.append(in_crop)
        chain_asym_id.append(chain["asym_id"])

        new_atom_idx += atom_num

    all_coords = np.concatenate(all_coords, axis=0)
    # Compute backmapping from token to all coords
    crop_to_all_atom_map = []
    for token in cropped.tokens:
        chain_idx = chain_asym_id.index(token["asym_id"])
        start = (
            chain_atom_idx[chain_idx] - original_atom_idx[chain_idx] + token["atom_idx"]
        )

        # add logic for backbone_only and atom14
        if bool(token["is_standard"]) and bool(token["design_mask"]) and backbone_only:
            if token["mol_type"] == const.chain_type_ids["PROTEIN"]:
                atom_num = min(4, token["atom_num"])
            elif token["mol_type"] == const.chain_type_ids["DNA"]:
                atom_num = min(11, token["atom_num"])
            elif token["mol_type"] == const.chain_type_ids["RNA"]:
                atom_num = min(12, token["atom_num"])
        elif (
            bool(token["is_standard"])
            and bool(token["design_mask"])
            and (atom14 or atom37)
        ):
            if token["mol_type"] == const.chain_type_ids["PROTEIN"]:
                atom_num = 14 if atom14 else 37
            elif token["mol_type"] == const.chain_type_ids["DNA"]:
                atom_num = 22
            elif token["mol_type"] == const.chain_type_ids["RNA"]:
                atom_num = 23
        else:
            atom_num = token["atom_num"]

        res_type = const.tokens[token["res_type"]]

        # special handling for atom14: real atoms map back with offset, fake atoms map back to the center rep atom
        if (
            bool(token["is_standard"])
            and bool(token["design_mask"])
            and (atom14 or atom37)
        ):
            if atom14_geometric:
                local_array = np.arange(start, start + atom_num)
                placements = np.array(const.fake_atom_placements[res_type])

                oxygen_offset = const.ref_atoms[res_type].index("O")
                nitrogen_offset = const.ref_atoms[res_type].index("N")

                local_array[placements == "O"] = start + oxygen_offset
                local_array[placements == "N"] = start + nitrogen_offset
            elif atom37:
                ca_offset = const.ref_atoms[res_type].index("CA")
                local_array = np.array(
                    [
                        start + const.ref_atoms[res_type].index(name)
                        if name in const.ref_atoms[res_type]
                        else start + ca_offset
                        for name in const.atom_types
                    ]
                )
            else:
                real_range = np.arange(start, start + token["atom_num"])
                # need to add in offset for the rep atom
                rep_atom_offset = token["center_idx"] - token["atom_idx"]
                fake_range = np.array(
                    [start + rep_atom_offset] * (atom_num - token["atom_num"])
                )
                local_array = np.concatenate([real_range, fake_range])
        # for backbone_only and without backbone_only or atom14
        else:
            local_array = np.arange(start, start + atom_num)
        crop_to_all_atom_map.append(local_array)

    crop_to_all_atom_map = np.concatenate(crop_to_all_atom_map, axis=0)

    # Compute the connections edge index for covalent bonds
    all_atom_to_crop_map = np.zeros(all_coords.shape[0], dtype=np.int64)
    all_atom_to_crop_map[crop_to_all_atom_map.astype(np.int64)] = np.arange(
        crop_to_all_atom_map.shape[0]
    )
    connections_edge_index = []
    for connection in structure.bonds:
        if (connection["chain_1"] == connection["chain_2"]) and (
            connection["res_1"] == connection["res_2"]
        ):
            continue
        connections_edge_index.append([connection["atom_1"], connection["atom_2"]])
    if len(connections_edge_index) > 0:
        connections_edge_index = np.array(connections_edge_index, dtype=np.int64).T
        connections_edge_index = all_atom_to_crop_map[connections_edge_index]
    else:
        connections_edge_index = np.empty((2, 0))

    # Compute the symmetries between chains
    symmetries = []
    swaps = []
    for i, chain in enumerate(structure.chains):
        start = chain_atom_idx[i]
        end = start + chain_atom_num[i]

        if chain_in_crop[i]:
            possible_swaps = []
            for j, chain2 in enumerate(structure.chains):
                start2 = chain_atom_idx[j]
                end2 = start2 + chain_atom_num[j]
                if (
                    chain["entity_id"] == chain2["entity_id"]
                    and end - start == end2 - start2
                ):
                    possible_swaps.append((start, end, start2, end2, i, j))
            swaps.append(possible_swaps)

        found = False
        for symmetry_idx, symmetry in enumerate(symmetries):
            j = symmetry[0][0]
            chain2 = structure.chains[j]
            start2 = chain_atom_idx[j]
            end2 = start2 + chain_atom_num[j]
            if (
                chain["entity_id"] == chain2["entity_id"]
                and end - start == end2 - start2
            ):
                symmetries[symmetry_idx].append(
                    (i, start, end, chain_in_crop[i], chain["mol_type"])
                )
                found = True
        if not found:
            symmetries.append([(i, start, end, chain_in_crop[i], chain["mol_type"])])

    combinations = itertools.product(*swaps)
    # to avoid combinatorial explosion, bound the number of combinations even considered
    combinations = list(itertools.islice(combinations, max_n_symmetries * 10))
    # filter for all chains getting a different assignment
    combinations = [c for c in combinations if all_different_after_swap(c)]

    if len(combinations) > max_n_symmetries:
        combinations = random.sample(combinations, max_n_symmetries)

    if len(combinations) == 0:
        combinations.append([])

    for i in range(len(symmetries) - 1, -1, -1):
        if not any(chain[3] for chain in symmetries[i]):
            symmetries.pop(i)

    features = {}
    features["all_coords"] = torch.Tensor(all_coords)  # axis=1 with ensemble

    features["all_resolved_mask"] = torch.Tensor(
        np.concatenate(all_resolved_mask, axis=0)
    )
    features["crop_to_all_atom_map"] = torch.Tensor(crop_to_all_atom_map)
    features["chain_symmetries"] = symmetries
    features["connections_edge_index"] = torch.tensor(connections_edge_index)
    features["chain_swaps"] = combinations

    return features


def get_amino_acids_symmetries(cropped, backbone_only, atom14, atom37):
    # Compute standard amino-acids symmetries
    swaps = []
    start_index_crop = 0
    for token in cropped.tokens:
        symmetries = const.ref_symmetries.get(const.tokens[token["res_type"]], [])

        # add atom_num logic for backbone_only and atom14
        if bool(token["is_standard"]) and bool(token["design_mask"]) and backbone_only:
            if token["mol_type"] == const.chain_type_ids["PROTEIN"]:
                atom_num = min(4, token["atom_num"])
            elif token["mol_type"] == const.chain_type_ids["DNA"]:
                atom_num = min(11, token["atom_num"])
            elif token["mol_type"] == const.chain_type_ids["RNA"]:
                atom_num = min(12, token["atom_num"])
        elif (
            bool(token["is_standard"])
            and bool(token["design_mask"])
            and (atom14 or atom37)
        ):
            if token["mol_type"] == const.chain_type_ids["PROTEIN"]:
                atom_num = 14 if atom14 else 37
            elif token["mol_type"] == const.chain_type_ids["DNA"]:
                atom_num = 22
            elif token["mol_type"] == const.chain_type_ids["RNA"]:
                atom_num = 23
        else:
            atom_num = token["atom_num"]

        if len(symmetries) > 0:
            residue_swaps = []
            for sym in symmetries:
                sym_new_idx = [
                    (i + start_index_crop, j + start_index_crop) for i, j in sym
                ]
                residue_swaps.append(sym_new_idx)
            swaps.append(residue_swaps)
        # start_index_crop += token["atom_num"]
        start_index_crop += atom_num

    features = {"amino_acids_symmetries": swaps}
    return features


def slice_valid_index(index, ccd_to_valid_id_array, args=None):
    index = ccd_to_valid_id_array[index]
    valid_index_mask = (~np.isnan(index)).all(axis=0)
    index = index[:, valid_index_mask]
    if args is None:
        return index
    args = (arg[valid_index_mask] for arg in args)
    return index, args


def get_ligand_symmetries(cropped, symmetries, return_physical_metrics=False):
    # Compute ligand and non-standard amino-acids symmetries
    return_physical_metrics = True

    structure = cropped.structure

    added_molecules = {}
    index_mols = []
    atom_count = 0

    crop_coords_list = []
    crop_names_list = []
    # for token in cropped.tokens:
    #     residue_idx = token["res_idx"] + structure.chains[token["asym_id"]]["res_idx"]
    #     atom_start = structure.residues[residue_idx]["atom_idx"]
    #     atom_end = atom_start + structure.residues[residue_idx]["atom_num"]
    #     atom_coords = structure.atoms[atom_start:atom_end]["coords"]
    #     crop_coords_list.extend(atom_coords)
    #     crop_names_list.extend(structure.atoms[atom_start:atom_end]["name"])
    for token in cropped.tokens:
        # check if molecule is already added by identifying it through asym_id and res_idx
        atom_count += token["atom_num"]
        mol_id = (token["asym_id"], token["res_idx"])
        if mol_id in added_molecules:
            added_molecules[mol_id] += token["atom_num"]
            #print(f"Molecule {mol_id} already added")
            continue
        added_molecules[mol_id] = token["atom_num"]

        # get the molecule type and indices
        residue_idx = token["res_idx"] + structure.chains[token["asym_id"]]["res_idx"]
        mol_name = structure.residues[residue_idx]["name"]
        atom_idx = structure.residues[residue_idx]["atom_idx"]
        mol_atom_names = structure.atoms[
            atom_idx : atom_idx + structure.residues[residue_idx]["atom_num"]
        ]["name"]

        atom_coords = structure.atoms[
            atom_idx : atom_idx + structure.residues[residue_idx]["atom_num"]
        ]["coords"]

        crop_coords_list.extend(atom_coords)
        crop_names_list.extend(structure.atoms[
            atom_idx : atom_idx + structure.residues[residue_idx]["atom_num"]
        ]["name"])

        if mol_name not in const.ref_symmetries:
            index_mols.append(
                (mol_name, atom_count - token["atom_num"], mol_id, mol_atom_names)
            )
    breakpoint()

    print("atom_count", atom_count)
    print(f"index_mols: {index_mols}")

    # for each molecule, get the symmetries
    molecule_symmetries = []
    all_edge_index = []
    all_lower_bounds, all_upper_bounds = [], []
    all_bond_mask, all_angle_mask = [], []
    all_chiral_atom_index, all_chiral_check_mask, all_chiral_atom_orientations = (
        [],
        [],
        [],
    )
    all_stereo_bond_index, all_stereo_check_mask, all_stereo_bond_orientations = (
        [],
        [],
        [],
    )
    (
        all_aromatic_5_ring_index,
        all_aromatic_6_ring_index,
        all_planar_double_bond_index,
    ) = (
        [],
        [],
        [],
    )
    for mol_name, start_mol, mol_id, mol_atom_names in index_mols:

        if not mol_name in symmetries:
            continue
        else:
            swaps = []
            (
                syms_ccd,
                mol_atom_names_ccd,
                edge_index,
                lower_bounds,
                upper_bounds,
                bond_mask,
                angle_mask,
                chiral_atom_index,
                chiral_check_mask,
                chiral_atom_orientations,
                stereo_bond_index,
                stereo_check_mask,
                stereo_bond_orientations,
                aromatic_5_ring_index,
                aromatic_6_ring_index,
                planar_double_bond_index,
            ) = symmetries[mol_name]

            # Get indices of mol_atom_names_ccd that are in mol_atom_names
            ccd_to_valid_ids = {
                mol_atom_names_ccd.index(name): i
                for i, name in enumerate(mol_atom_names)
            }
            ccd_to_valid_id_array = np.array(
                [
                    float("nan") if i not in ccd_to_valid_ids else ccd_to_valid_ids[i]
                    for i in range(len(mol_atom_names_ccd))
                ]
            )
            ccd_valid_ids = set(ccd_to_valid_ids.keys())
            syms = []
            # Get syms
            for sym_ccd in syms_ccd:
                sym_dict = {}
                bool_add = True
                for i, j in enumerate(sym_ccd):
                    if i in ccd_valid_ids:
                        if j in ccd_valid_ids:
                            i_true = ccd_to_valid_ids[i]
                            j_true = ccd_to_valid_ids[j]
                            sym_dict[i_true] = j_true
                        else:
                            bool_add = False
                            break
                if bool_add:
                    syms.append([sym_dict[i] for i in range(len(ccd_valid_ids))])
            for sym in syms:
                if len(sym) != added_molecules[mol_id]:
                    raise Exception(
                        f"Symmetry length mismatch {len(sym)} {added_molecules[mol_id]}"
                    )
                # assert (
                #     len(sym) == added_molecules[mol_id]
                # ), f"Symmetry length mismatch {len(sym)} {added_molecules[mol_id]}"
                sym_new_idx = []
                for i, j in enumerate(sym):
                    if i != int(j):
                        sym_new_idx.append((i + start_mol, int(j) + start_mol))
                if len(sym_new_idx) > 0:
                    swaps.append(sym_new_idx)

            if len(swaps) > 0:
                molecule_symmetries.append(swaps)

            if return_physical_metrics:
                edge_index, (lower_bounds, upper_bounds, bond_mask, angle_mask) = (
                    slice_valid_index(
                        edge_index,
                        ccd_to_valid_id_array,
                        (lower_bounds, upper_bounds, bond_mask, angle_mask),
                    )
                )
                all_edge_index.append(edge_index + start_mol)
                all_lower_bounds.append(lower_bounds)
                all_upper_bounds.append(upper_bounds)
                all_bond_mask.append(bond_mask)
                all_angle_mask.append(angle_mask)

                chiral_atom_index, (chiral_check_mask, chiral_atom_orientations) = (
                    slice_valid_index(
                        chiral_atom_index,
                        ccd_to_valid_id_array,
                        (chiral_check_mask, chiral_atom_orientations),
                    )
                )
                all_chiral_atom_index.append(chiral_atom_index + start_mol)
                all_chiral_check_mask.append(chiral_check_mask)
                all_chiral_atom_orientations.append(chiral_atom_orientations)

                stereo_bond_index, (stereo_check_mask, stereo_bond_orientations) = (
                    slice_valid_index(
                        stereo_bond_index,
                        ccd_to_valid_id_array,
                        (stereo_check_mask, stereo_bond_orientations),
                    )
                )
                all_stereo_bond_index.append(stereo_bond_index + start_mol)
                all_stereo_check_mask.append(stereo_check_mask)
                all_stereo_bond_orientations.append(stereo_bond_orientations)

                aromatic_5_ring_index = slice_valid_index(
                    aromatic_5_ring_index, ccd_to_valid_id_array
                )
                aromatic_6_ring_index = slice_valid_index(
                    aromatic_6_ring_index, ccd_to_valid_id_array
                )
                planar_double_bond_index = slice_valid_index(
                    planar_double_bond_index, ccd_to_valid_id_array
                )
                all_aromatic_5_ring_index.append(aromatic_5_ring_index + start_mol)
                all_aromatic_6_ring_index.append(aromatic_6_ring_index + start_mol)
                all_planar_double_bond_index.append(
                    planar_double_bond_index + start_mol
                )

    if return_physical_metrics:
        if len(all_edge_index) > 0:
            all_edge_index = np.concatenate(all_edge_index, axis=1).astype(np.int64)
            all_lower_bounds = np.concatenate(all_lower_bounds, axis=0)
            all_upper_bounds = np.concatenate(all_upper_bounds, axis=0)
            all_bond_mask = np.concatenate(all_bond_mask, axis=0)
            all_angle_mask = np.concatenate(all_angle_mask, axis=0)

            # ------------------------------------------------------------------
            # Ground-truth bond lengths (Å) for each edge in `ligand_edge_index`.
            # The edge indices are in the same crop-order we incremented while
            # scanning tokens, so we can rebuild the full set of coordinates for
            # the crop in that order and do a single vectorised norm.
            # ------------------------------------------------------------------
            if all_edge_index.shape[1] > 0:
                # crop_coords_list = []
                # crop_names_list = []
                # for token in cropped.tokens:
                #     residue_idx = token["res_idx"] + structure.chains[token["asym_id"]]["res_idx"]
                #     atom_start = structure.residues[residue_idx]["atom_idx"]
                #     atom_end = atom_start + structure.residues[residue_idx]["atom_num"]
                #     atom_coords = structure.atoms[atom_start:atom_end]["coords"]
                #     crop_coords_list.extend(atom_coords)
                #     crop_names_list.extend(structure.atoms[atom_start:atom_end]["name"])


                crop_coords = np.asarray(crop_coords_list, dtype=np.float32)
                crop_names  = np.asarray(crop_names_list, dtype='<U4')

                edge_lengths = np.linalg.norm(
                    crop_coords[all_edge_index[0]] - crop_coords[all_edge_index[1]], axis=1
                )
            else:
                edge_lengths = np.array([], dtype=np.float32)

            # ------------------------------------------------------------------
            # Compute bond order ground-truth (0,1,2,3,4)
            # Strategy: (1) RDKit DetermineBonds; (2) fallback to distance table.
            # ------------------------------------------------------------------
            if all_edge_index.shape[1] > 0:
                from rdkit.Chem import PeriodicTable
                # pt = Chem.GetPeriodicTable()
                ligand_atom_ids = np.unique(all_edge_index)
                ligand_coords = crop_coords[ligand_atom_ids]       # (Nlig, 3)
                ligand_names  = crop_names [ligand_atom_ids]

                # def element_of(name: str) -> str:
                #     letters = ''.join(c for c in name if c.isalpha())
                #     return letters.capitalize() if letters.capitalize() in element_to_atomic_num else letters[0].upper()

                # Build list of symbols and coords in crop order
                atomic_nums = [const.element_to_atomic_num[elem_from_name(n, mol_name)]
                                for n in ligand_names]
                atom_symbols = [elem_from_name(n, mol_name) for n in crop_names]
                #atomic_nums = [const.element_to_atomic_num[element_of(n)] for n in ligand_names]

                # RDKit DetermineBonds requires atomic numbers list and coordinates array

                try:
                    rw = RWMol()
                    for z in atomic_nums:
                        rw.AddAtom(Atom(z))

                    conf = Conformer(len(atomic_nums))
                    for i, (x, y, z) in enumerate(ligand_coords):
                        conf.SetAtomPosition(i, (float(x), float(y), float(z)))
                    rw.AddConformer(conf)

                    mol_rd = rw.GetMol()
                    rdDetermineBonds.DetermineBonds(mol_rd)
                    # rd_mol = rdDetermineBonds.DetermineBonds(
                    #     atomicNums=atomic_nums, confCoords=ligand_coords
                    # )
                except Exception:
                    rd_mol = None
                bond_order = np.zeros(all_edge_index.shape[1], dtype=np.int8)
                for e, (i, j) in enumerate(all_edge_index.T):
                        sym_i, sym_j = atom_symbols[int(i)], atom_symbols[int(j)]
                        bond_order[e] = get_bond_order(sym_i, sym_j, edge_lengths[e])
                breakpoint()
                # --------------------------------------------------------------
                # RDKit-based valence/sanitization check on inferred bonds
                # --------------------------------------------------------------
            #     try:
            #         # Map crop indices -> ligand-local indices [0..Nlig-1]
            #         index_map = -np.ones((crop_coords.shape[0],), dtype=np.int64)
            #         index_map[ligand_atom_ids] = np.arange(len(ligand_atom_ids), dtype=np.int64)

            #         # Build ligand-only RDKit mol with coordinates
            #         rw = RWMol()
            #         for z in atomic_nums:
            #             rw.AddAtom(Atom(int(z)))
            #         conf = Conformer(len(atomic_nums))
            #         for idx, (x_, y_, z_) in enumerate(ligand_coords):
            #             conf.SetAtomPosition(idx, (float(x_), float(y_), float(z_)))
            #         rw.AddConformer(conf)
            #         #breakpoint()

            #         # Add inferred bonds (convert aromatic class 4 to RDKit AROMATIC)
            #         bt_map = {
            #             1: Chem.BondType.SINGLE,
            #             2: Chem.BondType.DOUBLE,
            #             3: Chem.BondType.TRIPLE,
            #             4: Chem.BondType.AROMATIC,
            #         }
            #         for e, (i, j) in enumerate(all_edge_index.T):
            #             t = int(bond_order[e])
            #             if t <= 0:
            #                 continue
            #             li = int(index_map[int(i)])
            #             lj = int(index_map[int(j)])
            #             if li < 0 or lj < 0:
            #                 continue
            #             rw.AddBond(li, lj, bt_map.get(t, Chem.BondType.SINGLE))
            #             if t == 4:
            #                 # mark atoms/bond aromatic to aid sanitization
            #                 rw.GetAtomWithIdx(li).SetIsAromatic(True)
            #                 rw.GetAtomWithIdx(lj).SetIsAromatic(True)
            #                 rw.GetBondBetweenAtoms(li, lj).SetIsAromatic(True)
            #         #breakpoint()
            #         mol_check = rw.GetMol()
            #         ligand_valence_ok = True
            #         ligand_valence_problems = []
            #         #breakpoint()
            #         try:
            #             Chem.SanitizeMol(mol_check, sanitizeOps=Chem.SanitizeFlags.SANITIZE_ALL)
            #         except Exception as e:
            #             ligand_valence_ok = False
            #             ligand_valence_problems.append(f"SanitizeMol: {type(e).__name__}: {e}")

            #         for p in Chem.DetectChemistryProblems(mol_check):
            #             ligand_valence_ok = False
            #             ligand_valence_problems.append(p.Message())

            #     except Exception as _e_val:
            #         # If RDKit validation fails unexpectedly, leave flags unset
            #         ligand_valence_ok = False
            #         ligand_valence_problems = [f"valence-check error: {_e_val}"]
            #     print(ligand_valence_problems)
            # else:
            #     bond_order = np.array([], dtype=np.int8)

            #breakpoint()
            all_chiral_atom_index = np.concatenate(all_chiral_atom_index, axis=1)
            all_chiral_check_mask = np.concatenate(all_chiral_check_mask, axis=0)
            all_chiral_atom_orientations = np.concatenate(
                all_chiral_atom_orientations, axis=0
            )

            all_stereo_bond_index = np.concatenate(all_stereo_bond_index, axis=1)
            all_stereo_check_mask = np.concatenate(all_stereo_check_mask, axis=0)
            all_stereo_bond_orientations = np.concatenate(
                all_stereo_bond_orientations, axis=0
            )

            all_aromatic_5_ring_index = np.concatenate(
                all_aromatic_5_ring_index, axis=1
            )
            all_aromatic_6_ring_index = np.concatenate(
                all_aromatic_6_ring_index, axis=1
            )
            all_planar_double_bond_index = np.empty(
                (6, 0), dtype=np.int64
            )  # TODO remove np.concatenate(all_planar_double_bond_index, axis=1)
        else:
            all_edge_index = np.empty((2, 0), dtype=np.int64)
            all_lower_bounds = np.array([], dtype=np.float32)
            all_upper_bounds = np.array([], dtype=np.float32)
            all_bond_mask = np.array([], dtype=bool)
            all_angle_mask = np.array([], dtype=bool)

            all_chiral_atom_index = np.empty((4, 0), dtype=np.int64)
            all_chiral_check_mask = np.array([], dtype=bool)
            all_chiral_atom_orientations = np.array([], dtype=bool)
            all_stereo_bond_index = np.empty((4, 0), dtype=np.int64)
            all_stereo_check_mask = np.array([], dtype=bool)
            all_stereo_bond_orientations = np.array([], dtype=bool)

            all_aromatic_5_ring_index = np.empty((5, 0), dtype=np.int64)
            all_aromatic_6_ring_index = np.empty((6, 0), dtype=np.int64)
            all_planar_double_bond_index = np.empty((6, 0), dtype=np.int64)

        features = {
            "ligand_symmetries": molecule_symmetries,
            "ligand_edge_index": torch.tensor(all_edge_index).long(),
            "ligand_edge_lower_bounds": torch.tensor(all_lower_bounds),
            "ligand_edge_upper_bounds": torch.tensor(all_upper_bounds),
            "ligand_edge_bond_mask": torch.tensor(all_bond_mask),
            "ligand_edge_angle_mask": torch.tensor(all_angle_mask),
            "ligand_edge_lengths": torch.tensor(edge_lengths),
            "ligand_chiral_atom_index": torch.tensor(all_chiral_atom_index).long(),
            "ligand_chiral_check_mask": torch.tensor(all_chiral_check_mask),
            "ligand_chiral_atom_orientations": torch.tensor(
                all_chiral_atom_orientations
            ),
            "ligand_stereo_bond_index": torch.tensor(all_stereo_bond_index).long(),
            "ligand_stereo_check_mask": torch.tensor(all_stereo_check_mask),
            "ligand_stereo_bond_orientations": torch.tensor(
                all_stereo_bond_orientations
            ),
            "ligand_aromatic_5_ring_index": torch.tensor(
                all_aromatic_5_ring_index
            ).long(),
            "ligand_aromatic_6_ring_index": torch.tensor(
                all_aromatic_6_ring_index
            ).long(),
            "ligand_planar_double_bond_index": torch.tensor(
                all_planar_double_bond_index
            ).long(),
        }
    else:
        features = {
            "ligand_symmetries": molecule_symmetries,
        }
    breakpoint()
    return features


def generate_alphanumeric_strings(length: int = 5) -> Iterator[str]:
    """Generate all possible alphanumeric strings of length.

    Parameters
    ----------
    max_length : int, optional
        Maximum length of strings to generate, by default 5

    Yields
    ------
    str
        Alphanumeric string

    """
    chars = string.ascii_lowercase + string.digits
    for chars_tuple in product(chars, repeat=length):
        yield "".join(chars_tuple)


def mol_from_smile(smiles_list: list[str]) -> list[Mol]:
    """Load the smiles.

    Parameters
    ----------
    smiles : str
        Path to the smiles file.

    Returns
    -------
    List[Mol]

    """

    # Generate names
    names = generate_alphanumeric_strings(length=5)

    mols_processed = []
    failed = 0
    for smile in tqdm(smiles_list):
        try:
            mol = AllChem.MolFromSmiles(smile)
            mol = AllChem.AddHs(mol)
            mol.SetProp("MOL_NAME", "RANDO")
            mol.SetProp("SMILES", smile)
            canonical_order = AllChem.CanonicalRankAtoms(mol)
            for atom, can_idx in zip(mol.GetAtoms(), canonical_order):
                atom.SetProp("name", atom.GetSymbol().upper() + str(can_idx + 1))
            mols_processed.append(mol)
        except Exception as e:  # noqa: PERF203, BLE001
            failed += 1
    print(f"Failed to process {failed} molecules.")
    return mols_processed


def compute_3d(mol: Mol, num_conformers: int = 10) -> bool:
    """Generate 3D coordinates using EKTDG method.

    Taken from `pdbeccdutils.core.component.Component`.

    Parameters
    ----------
    mol: Mol
        The RDKit molecule to process
    num_conformers: int, optional
        Number of conformers to generate, defaults to 10

    Returns
    -------
    bool
        Whether computation was successful.

    """
    try:
        # Generate multiple conformers
        params = AllChem.ETKDGv3()
        params.numThreads = 0
        params.timeout = 60
        conf_ids = AllChem.EmbedMultipleConfs(
            mol, numConfs=num_conformers, params=params
        )

        if len(conf_ids) < num_conformers:
            params.useRandomCoords = True
            conf_ids = AllChem.EmbedMultipleConfs(
                mol, numConfs=num_conformers, params=params
            )

        if len(conf_ids) < 1:
            return False

        # Optimize each conformer
        conf_ids_final = []
        for conf_id in conf_ids:
            try:
                AllChem.UFFOptimizeMolecule(mol, confId=conf_id, maxIters=1000)
            except:  # noqa: E722
                # Remove failed conformer
                mol.RemoveConformer(conf_id)
                continue
            conf_ids_final.append(conf_id)

        if len(conf_ids_final) < 1:
            return False

    except:  # noqa: E722
        # Handle force field or sanitization issues
        return False

    return True


def get_moldir_atomic_numbers(moldir: str) -> list[int]:
    counter = set()
    mols = load_all_molecules(moldir)
    z_set = set()
    for mol in mols.values():
        z_set.update(a.GetAtomicNum() for a in mol.GetAtoms())
    z_set.discard(0)
    whitelist = sorted(z_set)
    return whitelist
