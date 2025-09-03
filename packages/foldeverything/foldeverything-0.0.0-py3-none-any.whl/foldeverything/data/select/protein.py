from dataclasses import replace
from typing import List, Optional, Set

import numpy as np
from scipy.spatial.distance import cdist

from foldeverything.data import const
from foldeverything.data.select.selector import Selector
from foldeverything.data.crop.multimer import pick_chain_token, MultimerCropper
from foldeverything.data.data import Tokenized


def get_min_distances(
    tokens1: Tokenized,
    tokens2: Tokenized,
    random: np.random.RandomState,
    noise_std: float = 1,
    axis: int = 1,
):
    tokens2_centers = tokens2["center_coords"].copy()
    tokens2_centers[~tokens2["resolved_mask"]] = np.nan
    tokens1_centers = tokens1["center_coords"].copy()
    tokens1_centers[~tokens1["resolved_mask"]] = np.nan
    distances = cdist(tokens1_centers, tokens2_centers)
    distances[np.isnan(distances)] = np.inf
    min_distances = np.min(distances, axis=axis)
    noisy_distances = min_distances + random.randn(*min_distances.shape) * noise_std
    return noisy_distances


def select_n_protein_no_lig(
    tokens: Tokenized,
    prot_chains: Tokenized,
    num_design_chains: int,
    random: np.random.RandomState,
    noise_std: float,
    redesign_prob: float,
):
    num_prot_chains = len(prot_chains)
    idx = random.choice(range(num_prot_chains))
    query_tokens = prot_chains[idx]
    candidate_chains = prot_chains[:idx] + prot_chains[idx + 1 :]
    candidate_tokens = np.concatenate(candidate_chains)
    noisy_distances = get_min_distances(
        candidate_tokens, query_tokens, random, noise_std
    )
    candidate_chain_ids = np.unique(candidate_tokens["asym_id"])

    # take the minimum across all residues in the candidate chains
    dist_gathered = []
    for asym_id in candidate_chain_ids:
        dist_gathered.append(
            np.min(noisy_distances[candidate_tokens["asym_id"] == asym_id])
        )

    # take closest chains to query chain as design chains together with query chain
    dist_gathered = np.array(dist_gathered)
    indices = np.argsort(dist_gathered)
    include_asym_ids = candidate_chain_ids[indices[: num_design_chains - 1]]
    design_chains = [c for c in candidate_chains if c["asym_id"][0] in include_asym_ids]
    design_chains = design_chains + [query_tokens]
    design_tokens = np.concatenate(design_chains)

    if random.rand(1) < redesign_prob:
        # design all design chains, predict the rest
        tokens["design_mask"][design_tokens["token_idx"]] = True
        denovo = True
    else:
        # redesign all design chain interfaces, predict the rest
        num_redesign_res = random.choice(len(design_tokens) // 4) + 1
        design_asym_ids = np.unique(design_tokens["asym_id"])
        target_chains = [
            c for c in prot_chains if c["asym_id"][0] not in design_asym_ids
        ]
        target_tokens = np.concatenate(target_chains)
        distances = get_min_distances(design_tokens, target_tokens, random, noise_std)
        indices2 = np.argsort(distances)
        redesign_tokens = design_tokens[indices2[:num_redesign_res]]
        tokens["design_mask"][redesign_tokens["token_idx"]] = True
        denovo = False
    return tokens, denovo


class ProteinSelector(Selector):
    """Select design tokens from protein chains."""

    def __init__(
        self,
        neighborhood_sizes: List[int] = [10],
        distance_noise_std: float = 1,
        redesign_prob: float = 0.5,
        target_cutoff1: float = 8,
        target_cutoff2: float = 12,
        run_selection: bool = True,
        select_all: bool = False,
    ) -> None:
        """Initialize the selector.

        Parameters
        ----------
        neighborhood_sizes : List[int]
            Modulates the type of selection to be performed.
            TODO: write doc

        """
        self.neighborhood_sizes = neighborhood_sizes
        self.cropper = MultimerCropper(neighborhood_sizes)
        self.distance_noise_std = distance_noise_std
        self.redesign_prob = redesign_prob
        self.target_cutoff1 = target_cutoff1
        self.target_cutoff2 = target_cutoff2
        self.run_selection = run_selection
        self.select_all = select_all

    def select(  # noqa: PLR0915
        self,
        data: Tokenized,
        random: np.random.RandomState,
        chain_id: Optional[int] = None,
        interface_id: Optional[int] = None,
    ) -> Tokenized:
        """Select protein residues to be designed.

        Parameters
        ----------
        data : Tokenized
            The tokenized data.
        random : np.random.RandomState
            The random state for reproducibility.

        Returns
        -------
        Tokenized
            The cropped data.

        """
        if not self.run_selection:
            return data, "predict"

        # Check inputs
        if chain_id is not None and interface_id is not None:
            msg = "Only one of chain_id or interface_id can be provided."
            raise ValueError(msg)

        # Randomly select a neighborhood size
        neighborhood_size = random.choice(self.neighborhood_sizes)

        # Get token data
        tokens = data.tokens.copy()
        prot_mask = tokens["mol_type"] == const.chain_type_ids["PROTEIN"]
        standard_mask = tokens["is_standard"] == 1

        # Atomized protein tokens are always predicted and never designed
        # However, we never use them as design targets
        atomized_prot_tokens = tokens[prot_mask & ~standard_mask]
        prot_tokens = tokens[prot_mask & standard_mask]
        nonprot_tokens = tokens[~prot_mask]

        # Get chains
        prot_chain_ids = np.unique(prot_tokens["asym_id"])
        prot_chains = [
            prot_tokens[prot_tokens["asym_id"] == asym] for asym in prot_chain_ids
        ]
        num_prot_chains = len(prot_chains)
        nonprot_chain_ids = np.unique(nonprot_tokens["asym_id"])
        nonprot_chains = [
            nonprot_tokens[nonprot_tokens["asym_id"] == asym]
            for asym in nonprot_chain_ids
        ]
        num_nonprot_chains = len(nonprot_chains)

        if self.select_all:
            tokens["design_mask"][prot_mask & standard_mask] = True
            design_task = "design_mask"
        elif num_prot_chains == 0:
            # predict everything, design nothing
            design_task = "prots0_other>0_predict"
        elif num_prot_chains == 1 and num_nonprot_chains == 0:
            # scaffolding
            num_design_res = random.choice(range(1, len(tokens) // 2))
            # TODO: this selects a random residue as query res. Instead select a surface residue as query.
            query = pick_chain_token(
                tokens[tokens["resolved_mask"]], prot_chain_ids[0], random
            )
            design_indices = self.cropper.select_cropped_indices(
                token_data=tokens,
                valid_tokens=tokens[tokens["resolved_mask"]],
                query=query,
                neighborhood_size=neighborhood_size,
                max_atoms=num_design_res * 10,
                max_tokens=num_design_res,
            )
            if len(design_indices) > 0:
                tokens["design_mask"][design_indices] = True
            design_task = "prots1_other0"
        elif num_prot_chains == 1 and num_nonprot_chains > 0:
            if random.rand(1) < self.redesign_prob:
                # design protein, predict everything else
                tokens["design_mask"][prot_mask & standard_mask] = True
                design_task = "prots1_otherN_denovo"
            else:
                # redesign protein interface, predict everything else
                num_redesign_res = random.choice(range(len(prot_tokens) // 4)) + 1
                idx = random.choice(range(num_nonprot_chains))
                target_chain = nonprot_chains[idx]
                noisy_distances = get_min_distances(
                    prot_tokens, target_chain, random, self.distance_noise_std
                )
                indices = np.argsort(noisy_distances)
                design_tokens = prot_tokens[indices[:num_redesign_res]]
                tokens["design_mask"][design_tokens["token_idx"]] = True
                design_task = "prots1_other>0_redesign"
        elif num_prot_chains > 1 and num_nonprot_chains == 0:
            num_design_chains = random.choice(range(num_prot_chains))
            if num_design_chains == 0:
                # predict everything, design nothing
                design_task = f"prots>1_other0_predict"
            else:
                tokens, denovo = select_n_protein_no_lig(
                    tokens,
                    prot_chains,
                    num_design_chains,
                    random,
                    self.distance_noise_std,
                    self.redesign_prob,
                )
                design_task = f"prots>1_other0_{'denovo' if denovo else 'redesign'}"
        elif num_prot_chains > 1 and num_nonprot_chains > 0:
            num_design_chains = random.choice(range(num_prot_chains - 1)) + 1
            distances = get_min_distances(
                nonprot_tokens, prot_tokens, random, noise_std=0
            )
            target_candidate_tokens = nonprot_tokens[distances < self.target_cutoff1]
            if len(target_candidate_tokens) == 0:
                target_candidate_tokens = nonprot_tokens[
                    distances < self.target_cutoff2
                ]

            if len(target_candidate_tokens) == 0:
                # proceed as in the many proteins and no ligands case
                tokens, denovo = select_n_protein_no_lig(
                    tokens,
                    prot_chains,
                    num_design_chains,
                    random,
                    self.distance_noise_std,
                    self.redesign_prob,
                )
                design_task = f"prots>1_other>0_{'denovo' if denovo else 'redesign'}"
            else:
                # select a random non_protein chain as target
                candidate_asym_ids = np.unique(target_candidate_tokens["asym_id"])
                target_asym_id = random.choice(candidate_asym_ids)
                target_tokens = tokens[tokens["asym_id"] == target_asym_id]

                # find a seed protein chain as first design chain
                distances = get_min_distances(
                    prot_tokens, target_tokens, random, noise_std=0
                )
                contact_tokens = prot_tokens[distances < self.target_cutoff2]
                seed_prot_asym_id = random.choice(np.unique(contact_tokens["asym_id"]))

                # add the rest of the design chains
                design_asym_ids = [seed_prot_asym_id]
                design_token_list = [tokens[tokens["asym_id"] == seed_prot_asym_id]]
                for _ in range(num_design_chains):
                    design_tokens = np.concatenate(design_token_list)
                    nondesign_prot_tokens = np.concatenate(
                        [
                            c
                            for c in prot_chains
                            if c["asym_id"][0] not in design_asym_ids
                        ]
                    )
                    dists_to_design = get_min_distances(
                        nondesign_prot_tokens, design_tokens, random, noise_std=0
                    )
                    dists_to_target = get_min_distances(
                        nondesign_prot_tokens, target_tokens, random, noise_std=0
                    )
                    preferred_token_mask = (dists_to_design < self.target_cutoff2) & (
                        dists_to_target > self.target_cutoff1
                    )
                    preferred_tokens = nondesign_prot_tokens[preferred_token_mask]
                    if len(preferred_tokens) > 0:
                        preferred_asym_ids = np.unique(preferred_tokens["asym_id"])
                        new_asym_id = random.choice(preferred_asym_ids)
                    else:
                        indices = np.argsort(dists_to_design)
                        closest_token = nondesign_prot_tokens[indices[0]]
                        new_asym_id = closest_token["asym_id"]
                    design_asym_ids.append(new_asym_id)
                    design_token_list.append(tokens[tokens["asym_id"] == new_asym_id])
                design_tokens = np.concatenate(design_token_list)

                if random.rand(1) < self.redesign_prob:
                    # design protein, predict everything else
                    tokens["design_mask"][design_tokens["token_idx"]] = True
                    design_task = f"prots>1_other>0_denovo"
                else:
                    # redesign all design chain interfaces, predict the rest
                    num_redesign_res = random.choice(len(design_tokens) // 4) + 1
                    distances = get_min_distances(
                        design_tokens, target_tokens, random, self.distance_noise_std
                    )
                    indices2 = np.argsort(distances)
                    redesign_tokens = design_tokens[indices2[:num_redesign_res]]
                    tokens["design_mask"][redesign_tokens["token_idx"]] = True
                    design_task = f"prots>1_other>0_redesign"
        else:
            raise NotImplementedError

        return replace(data, tokens=tokens), design_task
