import torch
from torch.nn import Module
from torch.nn.functional import one_hot
from foldeverything.data import const
import matplotlib.pyplot as plt


class BoltzMasker(Module):
    """Masking module for feats before passing to model forward."""

    def __init__(
        self,
        mask: bool = False,
        mask_backbone: bool = False,
        mask_disto: bool = False,
        correct_bond_masking: bool = False,
    ) -> None:
        """Initialize the masker.

        Parameters
        ----------
        mask : bool
            Whether or not to mask the input features.
        """
        super().__init__()
        self.mask = mask
        self.mask_backbone = mask_backbone
        self.mask_disto = mask_disto
        self.correct_bond_masking = correct_bond_masking

    def forward(self, feats):
        """['token_index', 'residue_index', 'asym_id', 'entity_id', 'sym_id', 'mol_type',
        'res_type', 'is_standard', 'design_mask', 'binding_type', 'structure_group' 'token_bonds', 'type_bonds',
         'token_pad_mask', 'token_resolved_mask', 'token_disto_mask', 'token_pair_mask',
          'contact_conditioning', 'contact_threshold', 'method_feature', 'temp_feature',
           'ph_feature', 'modified', 'ccd', 'cyclic', 'center_coords', 'token_distance_mask',
            'target_msa_mask', 'ref_pos', 'atom_resolved_mask',
             'ref_atom_name_chars', 'ref_element', 'ref_charge', 'ref_chirality', 'atom_backbone_feat',
              'ref_space_uid', 'coords', 'atom_pad_mask', 'atom_to_token', 'token_to_rep_atom', 'r_set_to_rep_atom',
               'disto_target', 'disto_coords_ensemble', 'bfactor', 'plddt', 'masked_ref_atom_name_chars',
                'backbone_mask', 'fake_atom_mask', 'token_to_bb4_atoms', 'msa', 'msa_paired', 'deletion_value', 'has_deletion',
                 'deletion_mean', 'profile', 'msa_mask', 'has_structure', 'has_affinity', 'ensemble_ref_idxs', 'id', 'feature_residue_index', 'feature_asym_id'
                 'token_to_res']"""
        if self.mask:
            new = {}
            new["id"] = feats["id"]
            new["structure_bonds"] = feats["structure_bonds"]
            skip_keys = [
                "id",
                "all_coords",
                "all_resolved_mask",
                "crop_to_all_atom_map",
                "chain_symmetries",
                "amino_acids_symmetries",
                "ligand_symmetries",
                "record",
            ]

            clone = {
                k: v.clone()
                for k, v in feats.items()
                if (k not in skip_keys) and isinstance(v, torch.Tensor)
            }

            device = clone["token_index"].device
            token_pad_mask = clone["token_pad_mask"].bool()
            design_mask = clone["design_mask"].bool()
            token_mask = token_pad_mask & design_mask

            atom_pad_mask = clone["atom_pad_mask"].bool()
            atom_design_mask = (
                torch.bmm(
                    clone["atom_to_token"].float(), design_mask.float().unsqueeze(-1)
                )
                .squeeze()
                .bool()
            )
            atom_mask = atom_pad_mask & atom_design_mask
            if not self.mask_backbone:
                atom_mask = atom_mask & ~clone["backbone_mask"].bool()

            new["ensemble_ref_idxs"] = clone["ensemble_ref_idxs"]
            new["has_structure"] = clone["has_structure"]

            # token features that are copied
            new["contact_threshold"] = clone["contact_threshold"]
            new["contact_conditioning"] = clone["contact_conditioning"]
            new["design_mask"] = clone["design_mask"]
            if "inverse_fold_design_mask" in clone:
                new["inverse_fold_design_mask"] = clone["inverse_fold_design_mask"]
            new["token_index"] = clone["token_index"]
            new["residue_index"] = clone["residue_index"]
            new["is_standard"] = clone["is_standard"]
            new["token_resolved_mask"] = clone["token_resolved_mask"]
            new["asym_id"] = clone["asym_id"]
            new["entity_id"] = clone["entity_id"]
            new["sym_id"] = clone["sym_id"]
            new["mol_type"] = clone["mol_type"]
            new["token_pad_mask"] = clone["token_pad_mask"]
            new["token_disto_mask"] = clone["token_disto_mask"]
            new["msa_mask"] = clone["msa_mask"]
            if "disto_target" in clone:
                new["disto_target"] = clone["disto_target"]
            new["token_pair_mask"] = clone["token_pair_mask"]
            new["binding_type"] = clone["binding_type"]
            new["structure_group"] = clone["structure_group"]
            new["cyclic"] = clone["cyclic"]
            new["modified"] = clone["modified"]
            new["token_distance_mask"] = clone["token_distance_mask"]
            new["center_coords"] = clone["center_coords"]
            new["noisy_center_coords"] = clone["noisy_center_coords"]
            new["absolute_coords"] = clone["absolute_coords"]
            new["method_feature"] = clone["method_feature"]
            new["temp_feature"] = clone["temp_feature"]
            new["ph_feature"] = clone["ph_feature"]
            new["design_ss_mask"] = clone["design_ss_mask"]
            new["ss_type"] = clone["ss_type"]
            new["res_type_clone"] = clone["res_type_clone"]
            new["feature_residue_index"] = clone["feature_residue_index"]
            new["feature_asym_id"] = clone["feature_asym_id"]
            new["is_anchor"] = clone["is_anchor"]
            new["token_to_res"] = clone["token_to_res"]
            if self.correct_bond_masking:
                # Only mask bonds between designed NONPOLYMER tokens
                designed_nonpolymer_mask = token_mask & (
                    clone["mol_type"] == const.chain_type_ids["NONPOLYMER"]
                )
                bond_mask = (
                    designed_nonpolymer_mask[:, :, None]
                    & designed_nonpolymer_mask[:, None, :]
                )

                if clone["token_bonds"].dim() == 4:
                    bond_mask_expanded = bond_mask.unsqueeze(-1)
                    mask_val = torch.zeros_like(clone["token_bonds"])
                    new["token_bonds"] = torch.where(
                        bond_mask_expanded, mask_val, clone["token_bonds"]
                    )
                else:
                    mask_val = torch.zeros_like(clone["token_bonds"])
                    new["token_bonds"] = torch.where(
                        bond_mask, mask_val, clone["token_bonds"]
                    )

                mask_val = torch.zeros_like(clone["type_bonds"])
                new["type_bonds"] = torch.where(
                    bond_mask, mask_val, clone["type_bonds"]
                )
            else:
                new["token_bonds"] = torch.zeros_like(
                    clone["token_bonds"]
                )  # This is a mistake and needs to be fixed at some point. These should be copied not overridden (if we are not doing small molecule design)
                new["type_bonds"] = clone["type_bonds"]

            template_keys = [
                "visibility_ids",
                "query_to_template",
                "template_mask",
                "template_mask_frame",
                "template_mask_cb",
                "template_ca",
                "template_cb",
                "template_frame_t",
                "template_frame_rot",
                "template_restype",
            ]
            for k in template_keys:
                if k in clone.keys():
                    new[k] = clone[k]

            # atom features that are copied
            new["new_to_old_atomidx"] = clone["new_to_old_atomidx"]
            new["bfactor"] = clone["bfactor"]
            new["plddt"] = clone["plddt"]
            new["atom_backbone_feat"] = clone["atom_backbone_feat"]
            new["backbone_mask"] = clone["backbone_mask"]
            new["atom_resolved_mask"] = clone["atom_resolved_mask"]
            new["ref_space_uid"] = clone["ref_space_uid"]
            new["coords"] = clone["coords"]
            new["fake_atom_mask"] = clone["fake_atom_mask"]
            new["atom_pad_mask"] = clone["atom_pad_mask"]
            new["r_set_to_rep_atom"] = clone["r_set_to_rep_atom"]
            new["token_to_rep_atom"] = clone["token_to_rep_atom"]
            new["atom_to_token"] = clone["atom_to_token"]
            new["atom_pad_mask"] = clone["atom_pad_mask"]
            new["masked_ref_atom_name_chars"] = clone["masked_ref_atom_name_chars"]
            new["token_to_bb4_atoms"] = clone["token_to_bb4_atoms"]

            # apply token feature masking
            mask_val = one_hot(
                torch.ones(clone["res_type"].shape[:-1], device=device).long()
                * (const.token_ids["UNK"]),
                len(const.token_ids),
            )
            new["res_type"] = torch.where(
                token_mask[:, :, None], mask_val, clone["res_type"]
            )

            mask_val = torch.zeros_like(clone["ccd"])
            new["ccd"] = torch.where(token_mask[:, :, None], mask_val, clone["ccd"])

            mask_val = torch.ones_like(clone["msa"]) * const.token_ids["UNK"]
            new["msa"] = torch.where(token_mask[:, None, :], mask_val, clone["msa"])

            mask_val = torch.ones_like(clone["msa"]) * const.token_ids["-"]
            new["msa"][:, 1:] = torch.where(
                clone["target_msa_mask"][:, None, :].bool(),
                mask_val[:, 1:],
                new["msa"][:, 1:],
            )

            mask_val = torch.zeros_like(clone["msa_mask"][:, 1:])
            new["msa_mask"][:, 1:] = torch.where(
                clone["target_msa_mask"][:, None, :].bool(),
                mask_val,
                clone["msa_mask"][:, 1:],
            )
            # plt.imshow(new["msa_mask"].cpu().numpy()[0])
            # plt.savefig("workbench/msa_mask.png", dpi=1000)
            # plt.clf()

            mask_val = torch.zeros_like(clone["msa_paired"])
            new["msa_paired"] = torch.where(
                token_mask[:, None, :], mask_val, clone["msa_paired"]
            )
            mask_val = torch.zeros_like(clone["deletion_value"])
            new["deletion_value"] = torch.where(
                token_mask[:, None, :], mask_val, clone["deletion_value"]
            )

            # Mask disto loss for designed parts
            if self.mask_disto:
                mask_val = torch.zeros_like(clone["token_disto_mask"])
                new["token_disto_mask"] = torch.where(
                    token_mask,
                    mask_val,
                    clone["token_disto_mask"],
                )
            mask_val = torch.zeros_like(clone["has_deletion"])
            new["has_deletion"] = torch.where(
                token_mask[:, None, :], mask_val, clone["has_deletion"]
            )

            mask_val = torch.zeros_like(clone["deletion_mean"])
            new["deletion_mean"] = torch.where(
                token_mask, mask_val, clone["deletion_mean"]
            )

            mask_val = one_hot(
                torch.ones(clone["profile"].shape[:-1], device=device).long()
                * (const.token_ids["UNK"]),
                len(const.token_ids),
            ).to(clone["profile"].dtype)
            new["profile"] = torch.where(
                token_mask[:, :, None], mask_val, clone["profile"]
            )

            # apply atom feature designability mask
            mask_val = one_hot(
                torch.ones(clone["ref_element"].shape[:-1], device=device).long()
                * (const.mask_element_id),
                const.num_elements,
            )
            new["ref_element"] = torch.where(
                atom_mask[:, :, None],
                mask_val,
                clone["ref_element"],
            )

            mask_val = torch.zeros_like(clone["ref_charge"])
            new["ref_charge"] = torch.where(atom_mask, mask_val, clone["ref_charge"])

            mask_val = (
                torch.ones_like(clone["ref_chirality"]).long()
                * const.chirality_type_ids["CHI_UNSPECIFIED"]
            )
            new["ref_chirality"] = torch.where(
                atom_mask, mask_val, clone["ref_chirality"]
            )

            mask_val = clone["masked_ref_atom_name_chars"].clone()
            new["ref_atom_name_chars"] = torch.where(
                atom_mask[:, :, None, None],
                mask_val,
                clone["ref_atom_name_chars"],
            )

            # for the ref_pos, the backbone positions might be leaking information about the residue identity.
            # They might not always be the same across all residues. So we always mask them independent of mask_backbone.
            mask = atom_pad_mask & atom_design_mask
            mask_val = torch.zeros_like(clone["ref_pos"])
            new["ref_pos"] = torch.where(
                mask[:, :, None],
                mask_val,
                clone["ref_pos"],
            )
        else:
            new = feats
        return new
