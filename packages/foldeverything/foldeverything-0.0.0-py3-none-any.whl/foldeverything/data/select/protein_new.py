from dataclasses import replace, astuple
from typing import Dict, List, Optional

from matplotlib import pyplot as plt
import numpy as np
from scipy.spatial.distance import cdist

from foldeverything.data import const
from foldeverything.data.select.selector import Selector
from foldeverything.data.crop.multimer import MultimerCropper
from foldeverything.data.data import (
    Residue,
    Structure,
    Token,
    Chain,
    Coords,
    Atom,
    Tokenized,
    convert_ccd,
    TokenBond,
    Bond,
    Interface,
    Ensemble,
)
from foldeverything.data.tokenize.af3 import TokenData
from foldeverything.data.mol import load_molecules
from rdkit import Chem, rdBase
from rdkit.Chem import AllChem
from rdkit.Chem.rdchem import Conformer, Mol
from rdkit.Chem.rdchem import BondType


def min_token_distances(
    tokens1: Tokenized,
    tokens2: Tokenized,
    random: np.random.Generator,
    noise_std: float = 1,
    axis: int = 1,
):
    tokens2_centers = tokens2["center_coords"].copy()
    tokens2_centers[~tokens2["resolved_mask"]] = np.nan
    tokens1_centers = tokens1["center_coords"].copy()
    tokens1_centers[~tokens1["resolved_mask"]] = np.nan
    return min_distances(tokens1_centers, tokens2_centers, random, noise_std, axis)


def min_distances(
    coords1: np.ndarray,
    coords2: np.ndarray,
    random: np.random.Generator,
    noise_std: float = 1,
    axis: int = 1,
):
    distances = cdist(coords1, coords2)
    distances[np.isnan(distances)] = np.inf
    min_distances = np.min(distances, axis=axis)
    noisy_distances = (
        min_distances + random.normal(size=min_distances.shape) * noise_std
    )
    return noisy_distances


def next_label(label):
    """Generate the next lexicographical string in a base-26 system."""
    if not label:
        return "A"

    label = list(label)  # Convert string to list of characters
    i = len(label) - 1

    while i >= 0:
        if label[i] != "Z":  # Increment current character
            label[i] = chr(ord(label[i]) + 1)
            return "".join(label)
        label[i] = "A"  # Reset to 'A' if it was 'Z'
        i -= 1

    return "A" + "".join(label)  # Prepend 'A' if all were 'Z'


class ProteinSelectorNew(Selector):
    """Select design tokens from protein chains."""

    def __init__(
        self,
        design_neighborhood_sizes: List[int] = [10],
        substructure_neighborhood_sizes: List[int] = [10],
        distance_noise_std: float = 1,
        run_selection: bool = True,
        specify_binding_sites: bool = False,
        select_all: bool = False,
        complete_structure_mask: bool = False,
        binding_token_cutoff: float = 15,
        binding_atom_cutoff: float = 5,
        anchor_atom_cutoff: float = 5,
        anchor_prob: float = 0.0,
        anchor_bond_prob: float = 0.0,
        max_num_anchor_residues: int = 0,
        max_msa_prob: float = 0.6,
        min_msa_prob: float = 0.1,
        target_msa_sampling_length_cutoff: int = 50,
        structure_condition_prob: float = 0,
        ss_condition_prob: float = 0,
        binding_site_probs: Optional[Dict[str, float]] = None,
        structure_probs: Optional[Dict[str, float]] = None,
        chain_reindexing=False,
        moldir: str = None,
        simple_selection=False,
    ) -> None:
        """Initialize the selector.

        Parameters
        ----------
        neighborhood_sizes : List[int]
            Modulates the type of selection to be performed.
            TODO: write doc

        """
        self.design_neighborhood_sizes = design_neighborhood_sizes
        self.substructure_neighborhood_sizes = substructure_neighborhood_sizes
        self.cropper = MultimerCropper(design_neighborhood_sizes)
        self.distance_noise_std = distance_noise_std
        self.run_selection = run_selection
        self.select_all = select_all
        self.specify_binding_sites = specify_binding_sites
        self.binding_token_cutoff = binding_token_cutoff
        self.anchor_atom_cutoff = anchor_atom_cutoff
        self.binding_atom_cutoff = binding_atom_cutoff
        self.max_msa_prob = max_msa_prob
        self.min_msa_prob = min_msa_prob
        self.ss_condition_prob = ss_condition_prob
        self.target_msa_sampling_length_cutoff = target_msa_sampling_length_cutoff
        self.anchor_prob = anchor_prob
        self.anchor_bond_prob = anchor_bond_prob
        self.max_num_anchor_residues = max_num_anchor_residues
        self.selection_functions = {
            "select_none": self.select_none,
            "select_scaffold": self.select_scaffold,
            "select_motif": self.select_motif,
            "select_scaffold_binder": self.select_scaffold_binder,
            "select_motif_binder": self.select_motif_binder,
            "select_nonprot_interface": self.select_nonprot_interface,
            "select_standard_prot": self.select_standard_prot,
            "select_protein_intefaces": self.select_protein_intefaces,
            "select_protein_chains": self.select_protein_chains,
        }
        self.probabilities = (
            const.training_task_probabilities_with_reindexing
            if chain_reindexing
            else const.training_task_probabilities_with_anchors
            if anchor_prob > 0.0
            else const.training_task_probabilities_simple
            if simple_selection
            else const.training_task_probabilities
        )
        self.moldir = moldir

        if binding_site_probs is None:
            binding_site_probs = {
                "specify_binding": 0.15,
                "specify_not_binding": 0.075,
                "specify_binding_not_binding": 0.075,
                "specify_none": 0.7,
            }
        self.binding_type_tasks = [
            (prob, getattr(self, name)) for name, prob in binding_site_probs.items()
        ]

        if structure_probs is None:
            structure_probs = {
                "structure_all": 0.4,
                "structure_uniform": 0.3,
                "structure_crops": 0.3,
            }
        self.structure_tasks = [
            (prob, getattr(self, name)) for name, prob in structure_probs.items()
        ]

        self.ss_condition_tasks = [
            (0.5, self.ss_all),
            (0.5, self.ss_uniform),
        ]

        self.structure_condition_prob = structure_condition_prob
        self.complete_structure_mask = complete_structure_mask

    def select(  # noqa: PLR0915
        self,
        data: Tokenized,
        random: np.random.Generator,
    ) -> Tokenized:
        """Select protein residues to be designed.

        Parameters
        ----------
        data : Tokenized
            The tokenized data.
        random : np.random.Generator
            The random state for reproducibility.

        Returns
        -------
        Tokenized
            The cropped data.

        """
        if not self.run_selection:
            return data, "predict"

        # Get token data
        tokens = data.tokens.copy()
        prot_mask = tokens["mol_type"] == const.chain_type_ids["PROTEIN"]
        standard_mask = tokens["is_standard"].astype(bool)

        # Atomized protein tokens are always predicted and never designed
        # However, we never use them as design targets
        atomized_prot_tokens = tokens[prot_mask & ~standard_mask]
        prot_tokens = tokens[prot_mask & standard_mask]
        nonprot_tokens = tokens[~prot_mask]

        # Get chains
        prot_chain_ids = np.unique(prot_tokens["asym_id"])
        num_prot_chains = len(prot_chain_ids)
        nonprot_chain_ids = np.unique(nonprot_tokens["asym_id"])
        num_nonprot_chains = len(nonprot_chain_ids)

        # Get selection distribution
        if self.select_all:
            task = "select_all"
        elif num_prot_chains == 0:
            task = "0prot_>=0nonprot"
        elif num_prot_chains == 1 and num_nonprot_chains == 0:
            task = "1prot_0nonprot"
        elif num_prot_chains == 1 and num_nonprot_chains > 0:
            task = "1prot_>0nonprot"
        elif num_prot_chains > 1 and num_nonprot_chains == 0:
            task = ">1prot_0nonprot"
        elif num_prot_chains > 1 and num_nonprot_chains > 0:
            task = ">1prot_>0nonprot"
        else:
            raise NotImplementedError

        # Select "design_mask" feature in the tokens
        task_distribution = self.probabilities[task]
        weights, functions = zip(*task_distribution)
        selection_fn = self.selection_functions[random.choice(functions, p=weights)]
        tokens = selection_fn(tokens, random)

        # Reset token_idx and token bonds
        old_indices = tokens["token_idx"]
        old_to_new = {old: new for new, old in enumerate(old_indices)}
        token_bonds = data.bonds
        token_bonds = np.array(
            [
                (old_to_new[bond["token_1"]], old_to_new[bond["token_2"]], bond["type"])
                for bond in token_bonds
                if bond["token_1"] in old_indices and bond["token_2"] in old_indices
            ],
            dtype=TokenBond,
        )
        tokens["token_idx"] = np.arange(len(tokens))

        # Select "binding_type" conditioning feature
        self.run_specification(tokens, random, data.structure.atoms)

        # Construct the token_distance_mask for conditioning on distances
        self.run_distance_sampling(tokens, random)

        # Sample whether to keep MSAs
        self.run_target_msa_sampling(tokens, random)

        # Sample whether to give the secondary structure as input
        self.run_ss_mask_specification(tokens, random)

        if random.random() < self.anchor_prob:
            anchor_tokens, anchor_structure = self.extract_anchor_tokens(
                data.structure, tokens, random
            )
            tokenset, update_struct = self.add_anchor_tokens(
                data.structure,
                tokens,
                anchor_structure,
                anchor_tokens,
                random,
            )
            if anchor_tokens is not None:
                anchor_token_to_res = [
                    token["res_idx"] + data.structure.residues.shape[0]
                    for token in anchor_tokens
                ]
                anchor_token_to_res = np.array(anchor_token_to_res)
                token_to_res = np.concatenate([data.token_to_res, anchor_token_to_res])
            else:
                token_to_res = data.token_to_res
            tokenized_selected = replace(
                data,
                tokens=tokenset,
                bonds=token_bonds,
                structure=update_struct,
                token_to_res=token_to_res,
            )
        else:
            tokenized_selected = replace(data, tokens=tokens, bonds=token_bonds)
        return tokenized_selected, task + str(selection_fn)

    def run_ss_mask_specification(
        self, tokens: np.ndarray, random: np.random.Generator
    ):
        design_mask = tokens["design_mask"].astype(bool)
        if design_mask.sum() > 1 and random.random() < self.ss_condition_prob:
            weights, functions = zip(*self.ss_condition_tasks)
            ss_fn = random.choice(functions, p=weights)
            ss_fn(tokens, random)

    def ss_all(self, tokens, random):
        design_mask = tokens["design_mask"].astype(bool)
        tokens["design_ss_mask"][design_mask] = 1

    def ss_uniform(self, tokens, random):
        design_mask = tokens["design_mask"].astype(bool)
        num_sets = random.integers(1, len(tokens))
        split_points = sorted(
            random.choice(range(1, len(tokens)), num_sets, replace=False)
        )

        start = 0
        for end in split_points:
            if random.random() > 0.5:
                interval_mask = np.zeros_like(design_mask).astype(bool)
                interval_mask[start:end] = True
                tokens["design_ss_mask"][design_mask & interval_mask] = 1
            start = end
        if random.random() > 0.5:
            interval_mask = np.zeros_like(design_mask).astype(bool)
            interval_mask[start:end] = True
            tokens["design_ss_mask"][design_mask & interval_mask] = 1

    def run_target_msa_sampling(self, tokens: np.ndarray, random: np.random.Generator):
        design_mask = tokens["design_mask"]
        # compute length of targets
        diff = np.diff(design_mask, prepend=design_mask[0], append=design_mask[-1])
        target_msa_mask = np.zeros_like(design_mask)
        # find start of targetsd
        starts = np.concatenate(([0], np.where(diff != 0)[0]))
        lengths = np.diff(starts, append=len(design_mask))
        for i in range(len(starts)):
            seq_idx, l = starts[i], lengths[i]
            if design_mask[seq_idx] == 1:
                target_msa_mask[seq_idx : seq_idx + l] = (
                    1  # designed parts never have MSAs
                )
                continue
            if l > self.target_msa_sampling_length_cutoff:
                keep_msa_prob = self.max_msa_prob
            else:
                keep_msa_prob = (
                    (self.max_msa_prob - self.min_msa_prob)
                    * (l - 1)
                    / self.target_msa_sampling_length_cutoff
                )
            keep_msa = 1 - int(random.random() <= keep_msa_prob)
            target_msa_mask[seq_idx : seq_idx + l] = keep_msa
        tokens["target_msa_mask"] = target_msa_mask

    def run_distance_sampling(self, tokens: np.ndarray, random: np.random.Generator):
        if self.complete_structure_mask:
            tokens["structure_group"] = 1
            return

        design_mask = tokens["design_mask"].astype(bool)
        resolved_mask = tokens["resolved_mask"].astype(bool)
        target_tokens = tokens[~design_mask & resolved_mask]

        # Sample for which chains to specify the structure
        target_chain_ids = np.unique(target_tokens["asym_id"])
        if (
            len(target_chain_ids) == 0
            or random.random() > self.structure_condition_prob
        ):
            return
        num_specified = random.integers(1, len(target_chain_ids) + 1)
        specified_chains = random.choice(target_chain_ids, num_specified, replace=False)

        # For each chain for which we chose to specify the structure, select all tokens or sub-regions for which to specify the structure.
        substructure_sets = []
        for spec_chain in specified_chains:
            spec_tokens = tokens[(tokens["asym_id"] == spec_chain) & ~design_mask]
            weights, functions = zip(*self.structure_tasks)
            structure_fn = random.choice(functions, p=weights)

            substructure_sets.extend(structure_fn(spec_tokens, random))

        # Sample the number of coodinate systems (we call them groups) into which we will put the motifs. Shift by one because of 1 indexing in the groups (0 corresponds to no structure specification).
        num_groups = random.integers(1, len(substructure_sets) + 1)

        # Get group/frame assigments. Group 0 corresponds to no distance assignment. The other groups are indexed from 1. So there are always at least 2 groups here (0 and 1). If there is no structure conditioning, then there is only one group.
        for substructure_set in substructure_sets:
            group_assignment = random.choice(np.arange(num_groups)) + 1
            tokens["structure_group"][substructure_set["token_idx"]] = group_assignment

        assert tokens["structure_group"][tokens["design_mask"].astype(bool)].sum() == 0

    def structure_all(self, tokens: np.ndarray, random: np.random.Generator):
        return [tokens]

    def structure_uniform(self, tokens: np.ndarray, random: np.random.Generator):
        if len(tokens) == 1:
            return [tokens]
        num_sets = random.integers(1, min(len(tokens), 6))
        split_points = sorted(
            random.choice(range(1, len(tokens)), num_sets, replace=False)
        )

        structure_sets = []
        start = 0
        for end in split_points:
            structure_sets.append(tokens[start:end])
            start = end
        structure_sets.append(tokens[start:])
        return structure_sets

    def structure_crops(self, tokens: np.ndarray, random: np.random.Generator):
        if len(tokens) < 5:
            return [tokens]
        num_substructures = random.integers(2, 5)

        # Create the substructures by keeping track of remaining indices that are not yet included in a subsstructure. The maximum size of the next crop is always sampled between 1 and the number of remaining indices
        substructures = []
        remaining = tokens["token_idx"].copy()
        for _ in range(num_substructures):
            neighborhood_size = random.choice(self.substructure_neighborhood_sizes)

            # Make sure that there are enough indices to select
            if len(remaining) < neighborhood_size + 1:
                break
            num_crop = max(random.integers(len(remaining)), neighborhood_size + 1)

            remaining_tokens = tokens[np.isin(tokens["token_idx"], remaining)]
            query = remaining_tokens[random.integers(len(remaining_tokens))]
            crop_indices = self.cropper.select_cropped_indices(
                tokens=remaining_tokens,
                valid_tokens=remaining_tokens[remaining_tokens["resolved_mask"]],
                query=query,
                neighborhood_size=neighborhood_size,
                max_atoms=num_crop * 10,
                max_tokens=num_crop,
            )

            if len(crop_indices) == 0:
                # This can happen if there are multiple tokens with the same residue index because the max_tokens does not actually correspond to max_tokens but to maximum number of residues
                break

            substructure_tokens = remaining_tokens[crop_indices]
            substructures.append(substructure_tokens)
            remaining = remaining[~np.isin(remaining, substructure_tokens["token_idx"])]

        # Handle edge case that we broke the loop because there werer not enough indices to select from.
        if len(substructures) == 0:
            return [tokens]

        # Assert to check that there are no ovelaps in the substructures
        all_substructured = np.concatenate(substructures)
        assert len(all_substructured) == len(
            np.unique(all_substructured["token_idx"])
        ), (
            "There are overlaps in the substructures during structure conditioning selection."
        )

        return substructures

    def run_specification(
        self, tokens: np.ndarray, random: np.random.Generator, all_atoms: Atom
    ):
        """In place operation to specify the binding_type feature."""

        design_mask = tokens["design_mask"].astype(bool)
        resolved_mask = tokens["resolved_mask"].astype(bool)
        design_tokens = tokens[design_mask & resolved_mask]
        target_tokens = tokens[~design_mask & resolved_mask]

        if (
            not self.specify_binding_sites
            or len(target_tokens) == 0
            or len(design_tokens) == 0
        ):
            return

        # Find binder and target tokens within self.binding_token_cutoff of each other
        target_min_distances = min_token_distances(
            target_tokens, design_tokens, random, self.distance_noise_std
        )
        target_subset = target_tokens[target_min_distances < self.binding_token_cutoff]

        design_min_distances = min_token_distances(
            design_tokens, design_tokens, random, self.distance_noise_std
        )
        design_subset = design_tokens[design_min_distances < self.binding_token_cutoff]

        if len(target_subset) == 0 or len(design_subset) == 0:
            return

        # Get atoms of the tokens that are close to each other
        target_atoms = []
        target_atom_to_token = []
        for idx, t in enumerate(target_subset):
            atoms = all_atoms[t["atom_idx"] : t["atom_idx"] + t["atom_num"]]
            atoms = atoms[atoms["is_present"].astype(bool)]
            target_atoms.append(atoms)
            target_atom_to_token.append([idx] * len(atoms))
        target_atoms = np.concatenate(target_atoms)
        target_atom_to_token = np.concatenate(target_atom_to_token)

        design_atoms = []
        design_atom_to_token = []
        for idx, t in enumerate(design_subset):
            atoms = all_atoms[t["atom_idx"] : t["atom_idx"] + t["atom_num"]]
            atoms = atoms[atoms["is_present"].astype(bool)]
            design_atoms.append(atoms)
            design_atom_to_token.append([idx] * len(atoms))
        design_atoms = np.concatenate(design_atoms)
        design_atom_to_token = np.concatenate(design_atom_to_token)

        # Compute contacts based on atom level distances
        distances = min_distances(
            target_atoms["coords"],
            design_atoms["coords"],
            random,
            self.distance_noise_std,
        )
        target_contacts = target_subset[
            target_atom_to_token[distances < self.binding_atom_cutoff]
        ]
        contact_mask = np.isin(tokens["token_idx"], target_contacts["token_idx"])

        weights, functions = zip(*self.binding_type_tasks)
        binding_fn = random.choice(functions, p=weights)
        binding_fn(tokens, contact_mask, design_mask, random)
        assert tokens["binding_type"][tokens["design_mask"].astype(bool)].sum() == 0

    def specify_none(
        self,
        tokens: np.ndarray,
        contact_mask: np.ndarray,
        design_mask: np.ndarray,
        random: np.random.Generator,
    ):
        pass

    def specify_binding(
        self,
        tokens: np.ndarray,
        contact_mask: np.ndarray,
        design_mask: np.ndarray,
        random: np.random.Generator,
    ):
        assert (contact_mask & design_mask).sum() == 0
        if (contact_mask).sum() == 0:
            return
        elif (contact_mask).sum() == 1:
            num_specified = 1
        else:
            num_specified = random.integers(1, contact_mask.sum())

        specified_idx = random.choice(
            np.arange(len(contact_mask))[contact_mask], num_specified, replace=False
        )
        tokens["binding_type"][specified_idx] = const.binding_type_ids["BINDING"]
        assert tokens["binding_type"][tokens["design_mask"].astype(bool)].sum() == 0

    def specify_not_binding(
        self,
        tokens: np.ndarray,
        contact_mask: np.ndarray,
        design_mask: np.ndarray,
        random: np.random.Generator,
    ):
        not_binding_mask = ~contact_mask & ~design_mask
        if (not_binding_mask).sum() == 0:
            return
        elif (not_binding_mask).sum() == 1:
            num_specified = 1
        else:
            num_specified = random.integers(1, (not_binding_mask).sum())

        specified_idx = random.choice(
            np.arange(len(not_binding_mask))[not_binding_mask],
            num_specified,
            replace=False,
        )
        tokens["binding_type"][specified_idx] = const.binding_type_ids["NOT_BINDING"]
        assert tokens["binding_type"][tokens["design_mask"].astype(bool)].sum() == 0

    def specify_binding_not_binding(
        self,
        tokens: np.ndarray,
        contact_mask: np.ndarray,
        design_mask: np.ndarray,
        random: np.random.Generator,
    ):
        self.specify_binding(tokens, contact_mask, design_mask, random)
        self.specify_not_binding(tokens, contact_mask, design_mask, random)

    def select_none(
        self,
        tokens: np.ndarray,
        random: np.random.Generator,
    ):
        return tokens

    def resect_and_reindex(
        self,
        tokens: np.ndarray,
        random: np.random.Generator,
    ):
        deltas = np.concatenate(
            (tokens["asym_id"].astype(int), np.array([-1]))
        ) - np.concatenate((np.array([-1]), tokens["asym_id"].astype(int)))
        chain_breaks = np.where(deltas != 0)[0]
        deltas = np.concatenate(
            (tokens["design_mask"].astype(int), np.array([-1]))
        ) - np.concatenate((np.array([-1]), tokens["design_mask"].astype(int)))
        design_breaks = np.where(deltas != 0)[0]
        breaks = [
            int(i) for i in sorted(list(set(chain_breaks).union(set(design_breaks))))
        ]
        resection_mask = np.ones_like(tokens["design_mask"])
        for i in range(len(breaks) - 1):
            s, e = breaks[i], breaks[i + 1]
            tokens["feature_asym_id"][s:e] = i
            tokens["feature_res_idx"][s:e] = np.arange(e - s)

            # resect a random number of residues around the boundaries
            if i > 0:
                _s = max(0, s - random.integers(1, 5))
                _e = min(len(resection_mask), s + random.integers(1, 5))
                resection_mask[_s:_e] = 0
        resection_mask = np.clip(
            resection_mask + tokens["design_mask"], a_min=0, a_max=1
        )  # keep all design tokens
        cropped = np.where(resection_mask)[0]
        tokens = tokens[cropped]
        return tokens

    def select_motif(
        self,
        tokens: np.ndarray,
        random: np.random.Generator,
        fixed_crop: bool = False,
    ):
        prot_mask = tokens["mol_type"] == const.chain_type_ids["PROTEIN"]
        standard_mask = tokens["is_standard"].astype(bool)
        prot_tokens = tokens[prot_mask & standard_mask]

        neighborhood_size = random.choice(self.design_neighborhood_sizes)

        if fixed_crop:
            num_crop = min(len(prot_tokens) // 4, 20)
        else:
            num_crop = max(random.integers(len(prot_tokens)), neighborhood_size + 1)

        query = prot_tokens[random.integers(len(prot_tokens))]
        crop_indices = self.cropper.select_cropped_indices(
            tokens=prot_tokens,
            valid_tokens=prot_tokens[prot_tokens["resolved_mask"]],
            query=query,
            neighborhood_size=neighborhood_size,
            max_atoms=num_crop * 10,
            max_tokens=num_crop,
        )

        if len(crop_indices) > 0:
            design_indices = prot_tokens["token_idx"][crop_indices]
            if len(design_indices) > 0:
                tokens["design_mask"][design_indices] = True

        return tokens

    def select_motif_binder(
        self,
        tokens: np.ndarray,
        random: np.random.Generator,
        fixed_crop: bool = False,
    ):
        tokens = self.select_motif(tokens, random, fixed_crop)
        return self.resect_and_reindex(tokens, random)

    def select_scaffold(
        self,
        tokens: np.ndarray,
        random: np.random.Generator,
        fixed_crop: bool = False,
    ):
        prot_mask = tokens["mol_type"] == const.chain_type_ids["PROTEIN"]
        standard_mask = tokens["is_standard"].astype(bool)
        prot_tokens = tokens[prot_mask & standard_mask]

        neighborhood_size = random.choice(self.design_neighborhood_sizes)
        if fixed_crop:
            num_crop = min(len(prot_tokens) // 4, 20)
        else:
            num_crop = max(random.integers(len(prot_tokens)), neighborhood_size + 1)

        query = prot_tokens[random.integers(len(prot_tokens))]
        crop_indices = self.cropper.select_cropped_indices(
            tokens=prot_tokens,
            valid_tokens=prot_tokens[prot_tokens["resolved_mask"]],
            query=query,
            neighborhood_size=neighborhood_size,
            max_atoms=num_crop * 10,
            max_tokens=num_crop,
        )

        prot_tok_mask = np.ones(len(prot_tokens))
        prot_tok_mask[crop_indices] = 0

        design_indices = prot_tokens["token_idx"][prot_tok_mask.astype(bool)]

        if len(design_indices) > 0:
            tokens["design_mask"][design_indices] = True
        return tokens

    def select_scaffold_binder(
        self,
        tokens: np.ndarray,
        random: np.random.Generator,
        fixed_crop: bool = False,
    ):
        tokens = self.select_scaffold(tokens, random, fixed_crop)
        return self.resect_and_reindex(tokens, random)

    def select_standard_prot(self, tokens, random):
        prot_mask = tokens["mol_type"] == const.chain_type_ids["PROTEIN"]
        standard_mask = tokens["is_standard"].astype(bool)
        tokens["design_mask"][prot_mask & standard_mask] = True
        return tokens

    def select_nonprot_interface(self, tokens, random):
        prot_mask = tokens["mol_type"] == const.chain_type_ids["PROTEIN"]
        standard_mask = tokens["is_standard"].astype(bool)
        prot_tokens = tokens[prot_mask & standard_mask]
        nonprot_tokens = tokens[~prot_mask]

        # Get target tokens from a random number of target chains
        nonprot_chain_ids = np.unique(nonprot_tokens["asym_id"])
        num_target_chains = random.choice(np.arange(1, len(nonprot_chain_ids) + 1))
        select_ids = random.choice(nonprot_chain_ids, num_target_chains, replace=False)
        target_chains = [tokens[tokens["asym_id"] == id] for id in select_ids]
        target_tokens = np.concatenate(target_chains)

        # Get closest redesign tokens
        noisy_distances = min_token_distances(
            prot_tokens, target_tokens, random, self.distance_noise_std
        )
        indices = np.argsort(noisy_distances)
        num_selected = random.choice(np.arange(1, len(prot_tokens) + 1))
        selected_tokens = prot_tokens[indices[:num_selected]]
        tokens["design_mask"][selected_tokens["token_idx"]] = True
        return tokens

    def select_protein_chains(self, tokens, random):
        prot_mask = tokens["mol_type"] == const.chain_type_ids["PROTEIN"]
        standard_mask = tokens["is_standard"].astype(bool)
        prot_tokens = tokens[prot_mask & standard_mask]

        prot_tokens["mol_type"]
        prot_chain_ids = np.unique(prot_tokens["asym_id"])
        assert len(prot_chain_ids) > 1
        num_selections = random.choice(np.arange(1, len(prot_chain_ids)))
        select_ids = random.choice(prot_chain_ids, num_selections, replace=False)

        for id in select_ids:
            tokens["design_mask"][(id == tokens["asym_id"]) & standard_mask] = True
        return tokens

    def select_protein_intefaces(self, tokens, random):
        prot_mask = tokens["mol_type"] == const.chain_type_ids["PROTEIN"]
        standard_mask = tokens["is_standard"].astype(bool)
        prot_tokens = tokens[prot_mask & standard_mask]

        # Select chains
        prot_chain_ids = np.unique(prot_tokens["asym_id"])
        assert len(prot_chain_ids) > 1
        num_selections = random.choice(np.arange(1, len(prot_chain_ids)))
        select_ids = random.choice(prot_chain_ids, num_selections, replace=False)
        redesign_tokens = tokens[np.isin(tokens["asym_id"], select_ids) & standard_mask]
        target_tokens = tokens[~np.isin(tokens["asym_id"], select_ids)]

        # Get indices of closest redesign tokens to the target tokens
        noisy_distances = min_token_distances(
            redesign_tokens, target_tokens, random, self.distance_noise_std
        )
        indices = np.argsort(noisy_distances)
        num_selected = random.choice(np.arange(1, len(redesign_tokens) + 1))
        selected_tokens = redesign_tokens[indices[:num_selected]]
        tokens["design_mask"][selected_tokens["token_idx"]] = True
        return tokens

    def add_anchor_tokens(
        self,
        add_to_struct: Structure,
        add_to_tokens: np.ndarray,
        anchor_structure: Structure,
        anchor_tokens: np.ndarray,
        random: np.random.Generator,
    ):
        if anchor_tokens is None:
            return add_to_tokens, add_to_struct
        token_num = len(add_to_tokens)
        asym_num = len(add_to_struct.chains["asym_id"])
        entity_num = len(np.unique(add_to_struct.chains["entity_id"]))
        atom_num = len(add_to_struct.atoms)
        anchor_structure.chains[0]["name"] = next_label(chr(64 + asym_num))
        structure_new = Structure.concatenate(add_to_struct, anchor_structure)
        for token in anchor_tokens:
            token["token_idx"] += token_num
            token["atom_idx"] += atom_num
            token["asym_id"] += asym_num
            token["entity_id"] += entity_num
            token["center_idx"] += atom_num
            token["disto_idx"] += atom_num
            token["feature_asym_id"] += asym_num

        tokens_new = np.concatenate(
            (add_to_tokens, np.array(anchor_tokens, dtype=add_to_tokens.dtype))
        )

        return tokens_new, structure_new

    def extract_anchor_tokens(
        self,
        struct: Structure,
        tokens: np.ndarray,
        random: np.random.Generator,
    ):
        num_residues = random.integers(1, self.max_num_anchor_residues)
        all_atoms = struct.atoms.copy()

        design_mask = tokens["design_mask"].astype(bool)
        resolved_mask = tokens["resolved_mask"].astype(bool)
        design_tokens = tokens[design_mask & resolved_mask]
        target_tokens = tokens[~design_mask & resolved_mask]

        if len(target_tokens) == 0 or len(design_tokens) == 0:
            return None, None

        # Get structure group with respect to which the token is specified
        structure_groups = np.unique(tokens["structure_group"].copy())
        if len(structure_groups) == 1:
            return None, None
        non_zero_groups = structure_groups[structure_groups != 0]
        structure_group = random.choice(non_zero_groups)

        # Find binder and target tokens within self.anchor_atom_cutoff of each other
        target_min_distances = min_token_distances(
            target_tokens, design_tokens, random, self.distance_noise_std
        )
        target_subset = target_tokens[target_min_distances < self.anchor_atom_cutoff]
        if len(target_tokens) == 0:
            return None, None
        design_min_distances = min_token_distances(
            design_tokens, target_tokens, random, self.distance_noise_std
        )
        design_subset = design_tokens[design_min_distances < self.anchor_atom_cutoff]
        design_subset = design_tokens[
            np.argsort(design_min_distances)[:num_residues]
        ]  # choose the closest num_residues tokens to the target tokens
        if len(target_subset) == 0 or len(design_subset) == 0:
            return None, None

        # Get atoms to delete indices and add fake tokens
        target_atoms = []
        for idx, t in enumerate(target_subset):
            atoms = all_atoms[t["atom_idx"] : t["atom_idx"] + t["atom_num"]]
            atoms = atoms[atoms["is_present"].astype(bool)]
            target_atoms.append(atoms)
        target_atoms = np.concatenate(target_atoms)
        if len(target_atoms) == 0:
            return None, None

        anchor_atom_idx = 0
        anchor_residue_idx = 0
        anchor_atoms = []
        anchor_tokens = []
        anchor_res = []
        anchor_coords = []
        for token in design_subset:
            num_atoms_within_residues = min(max(np.random.poisson(lam=2.8), 1), 3)
            atoms = all_atoms[token["atom_idx"] : token["atom_idx"] + token["atom_num"]]
            atoms = atoms[
                np.argsort(
                    min_distances(
                        atoms["coords"],
                        target_atoms["coords"],
                        random,
                        self.distance_noise_std,
                    )
                )[:num_atoms_within_residues]
            ]
            parent_atoms = atoms[atoms["is_present"].astype(bool)]
            anchor_res_atom_num = 0
            anchor_bonds = []
            if self.anchor_bond_prob > 0 and token["res_name"] not in  ["UNK",""]:
                mol = load_molecules(self.moldir, [token["res_name"]])[token["res_name"]]
                atom_name_to_ref = {a.GetProp("name"): a for a in mol.GetAtoms()}

                for idx1 in range(len(parent_atoms)):
                    for idx2 in range(idx1 + 1, len(parent_atoms)):
                        bond = mol.GetBondBetweenAtoms(
                            atom_name_to_ref[parent_atoms[idx1]["name"]].GetIdx(),
                            atom_name_to_ref[parent_atoms[idx2]["name"]].GetIdx(),
                        )
                        if (
                            bond is not None
                            and parent_atoms[idx1]["name"] != "CA"
                            and parent_atoms[idx2]["name"] != "CA"
                        ):
                            anchor_bonds.append(
                                (
                                    0,
                                    0,
                                    anchor_residue_idx,
                                    anchor_residue_idx,
                                    idx1 + len(anchor_atoms),
                                    idx2 + len(anchor_atoms),
                                    1
                                    if bond.GetBondType() == BondType.SINGLE
                                    else 2
                                    if bond.GetBondType() == BondType.DOUBLE
                                    else 3
                                    if bond.GetBondType() == BondType.TRIPLE
                                    else 4
                                    if bond.GetBondType() == BondType.AROMATIC
                                    else 0,
                                )
                            )

            for atom in parent_atoms:
                if atom["name"] == "CA":
                    continue
                token_data = TokenData(
                    token_idx=anchor_atom_idx,
                    atom_idx=anchor_atom_idx,
                    atom_num=1,
                    res_idx=anchor_residue_idx,
                    res_type=const.token_ids[const.unk_token["PROTEIN"]],
                    res_name=token["res_name"],
                    sym_id=0,
                    asym_id=0,
                    entity_id=0,
                    mol_type=const.chain_type_ids["NONPOLYMER"],
                    center_idx=anchor_atom_idx,
                    disto_idx=anchor_atom_idx,
                    center_coords=atom["coords"],
                    disto_coords=atom["coords"],
                    resolved_mask=True,
                    disto_mask=True,
                    modified=False,
                    frame_rot=np.eye(3).flatten(),
                    frame_t=np.zeros(3),
                    frame_mask=False,
                    min_dist_ligand=0,
                    cyclic_period=0,
                    is_standard=False,
                    design=False,
                    binding_type=const.binding_type_ids["UNSPECIFIED"],
                    structure_group=structure_group,
                    ccd=convert_ccd(token["res_name"]),
                    target_msa_mask=0,
                    design_ss_mask=0,
                    feature_asym_id=0,
                    feature_res_idx=anchor_residue_idx,
                    is_anchor=1,
                    anchor_parent_idx=1,
                )
                anchor_tokens.append(astuple(token_data))
                anchor_coords.append(atom["coords"])
                anchor_atoms.append(atom)
                anchor_res_atom_num += 1

                anchor_atom_idx += 1
            tokens[token["token_idx"]]["anchor_parent_idx"] = 1
            anchor_res.append(
                (
                    const.unk_token["PROTEIN"],
                    const.token_ids[const.unk_token["PROTEIN"]],
                    anchor_residue_idx,
                    anchor_res_atom_num,
                    len(parent_atoms),
                    0,
                    0,
                    False,
                    True,
                )
            )

            anchor_residue_idx += 1

        if len(anchor_tokens) == 0:
            return None, None

        anchor_chain = np.array(
            [
                (
                    next_label(chr(64 + 0)),
                    const.chain_type_ids["NONPOLYMER"],
                    0,
                    0,
                    0,
                    0,
                    len(anchor_atoms),
                    0,
                    len(anchor_res),
                    0,
                )
            ],
            dtype=Chain,
        )
        anchor_tokens = np.array(anchor_tokens, dtype=tokens.dtype)
        anchor_mask = np.array([True])

        anchor_coords = np.array(
            [(coord,) for coord in anchor_coords], dtype=struct.coords.dtype
        )

        anchor_atoms = np.array(anchor_atoms, dtype=Atom)
        anchor_residues = np.array(anchor_res, dtype=struct.residues.dtype)
        anchor_ensemble = np.array([(0, len(anchor_atoms))], dtype=Ensemble)
        anchor_structure = Structure(
            atoms=anchor_atoms,
            bonds=np.array(anchor_bonds, dtype=Bond)
            if random.random() < self.anchor_bond_prob
            else np.array([], dtype=Bond),
            residues=anchor_residues,
            chains=np.array(anchor_chain, dtype=Chain),
            interfaces=np.array([], dtype=Interface),
            mask=anchor_mask,
            coords=anchor_coords,
            ensemble=anchor_ensemble,
        )

        return anchor_tokens, anchor_structure
