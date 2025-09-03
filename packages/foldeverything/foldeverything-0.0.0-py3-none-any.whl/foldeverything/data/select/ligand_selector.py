from dataclasses import replace
from typing import Tuple
import numpy as np
import torch
from foldeverything.data import const
from foldeverything.data.select.selector import Selector
from foldeverything.data.select.protein_new import ProteinSelectorNew
from foldeverything.data.tokenize.af3 import Tokenized



class LigandSelector(Selector):

    def __init__(self) -> None:

        super().__init__()
        self.protein_selector = ProteinSelectorNew(
            design_neighborhood_sizes=[2, 4, 6, 8, 10, 12, 14, 16, 18],
            substructure_neighborhood_sizes=[2, 4, 6, 8, 10, 12, 24],
            structure_condition_prob=1.0,
            distance_noise_std=1.0,
            run_selection=True,
            specify_binding_sites=True,
            ss_condition_prob=0.1,
            select_all=False,
            chain_reindexing=False,
            anchor_prob=0.0,
        )


    def select(
        self, data: Tokenized, random: np.random.Generator
    ) -> Tuple[Tokenized, str]:

        tokens = data.tokens.copy()
        is_nonpolymer = tokens["mol_type"] == const.chain_type_ids["NONPOLYMER"]

        kept_atom_to_token = []
        kept_chain_ids = []
        kept_is_present = []

        struct_atoms = data.structure.atoms
        for token_idx, tok in enumerate(tokens):
            num_atoms = tok["atom_num"]
            start_idx = tok["atom_idx"]
            end_idx = start_idx + num_atoms
            slice_atoms = struct_atoms[start_idx:end_idx]
            kept_atom_to_token.append(np.repeat(token_idx, num_atoms))
            kept_chain_ids.append(np.repeat(tok["asym_id"], num_atoms))
            kept_is_present.append(slice_atoms["is_present"])  # bools / 0-1

        atom_to_token_tensor = torch.from_numpy(np.concatenate(kept_atom_to_token))
        atom_chain_ids = torch.from_numpy(np.concatenate(kept_chain_ids))
        n_atoms = atom_chain_ids.numel()
        same_chain_mask = (atom_chain_ids[:, None] == atom_chain_ids[None, :]).float()

        atom_mask = torch.from_numpy(np.concatenate(kept_is_present)).float()
        pair_mask = atom_mask[:, None] * atom_mask[None, :]
        same_chain_pairs = torch.sum(same_chain_mask * pair_mask, dim=-1)
        is_ion_atom = (same_chain_pairs == 1)

        is_ion_token = np.zeros(len(tokens), dtype=bool)
        for token_idx in range(len(tokens)):
            atom_mask_token = atom_to_token_tensor == token_idx
            if atom_mask_token.any():
                is_ion_token[token_idx] = torch.all(is_ion_atom[atom_mask_token]).item()

        designable_mask = is_nonpolymer & ~is_ion_token


        tokens["design_mask"][:] = 0
        tokens["design_mask"][designable_mask] = 1

        self.protein_selector.run_specification(tokens, random, struct_atoms)
        self.protein_selector.run_distance_sampling(tokens, random)



        tokens["target_msa_mask"][designable_mask] = 1
        tokenized_selected = replace(data, tokens=tokens)
        return tokenized_selected, "ligand_design"
