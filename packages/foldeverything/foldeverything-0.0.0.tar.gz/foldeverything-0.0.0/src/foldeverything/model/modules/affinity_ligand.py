import torch
from torch import nn
from torch.nn.functional import one_hot

import foldeverything.model.layers.initialize as init
from foldeverything.data import const
from foldeverything.model.layers.confidence_utils import GaussianSmearing
from foldeverything.model.layers.miniformer import MiniformerModule
from foldeverything.model.layers.pairformer import PairformerModule
from foldeverything.model.modules.transformers import DiffusionTransformer
from foldeverything.model.modules.encoders import RelativePositionEncoder
from foldeverything.model.modules.utils import LinearNoBias
from foldeverything.model.layers.transition import Transition
from foldeverything.model.modules.encoders import PairwiseConditioning


class AffinityModuleLigand(nn.Module):
    """Algorithm 31"""

    def __init__(
        self,
        token_s,
        token_z,
        pairformer_args: dict,
        transformer_args: dict,
        no_trunk_feats=False,
        num_dist_bins=64,
        use_gaussian=False,
        token_level_confidence=True,
        use_miniformer=False,
        max_dist=22,
        add_s_to_z_prod=False,
        add_s_input_to_s=False,
        use_s_diffusion=False,
        add_z_input_to_z=False,
        maximum_bond_distance=0,
        confidence_prediction=False,
        confidence_args: dict = None,
        affinity_prediction=False,
        affinity_args: dict = None,
        compute_pae: bool = False,
        imitate_trunk=False,
        full_embedder_args: dict = None,
        msa_args: dict = None,
        compile_pairformer=False,
        samples_axial_attention=False,
        multiplicity_averaging_input=False,
        expand_to_atom_level=False,
        use_s_chem_features=False,
    ):
        super().__init__()
        self.no_trunk_feats = no_trunk_feats
        self.use_s_diffusion = use_s_diffusion
        self.max_num_atoms_per_token = 23
        self.use_gaussian = use_gaussian
        s_input_dim = (
            token_s + 2 * const.num_tokens + 1 + len(const.pocket_contact_info)
        )
        self.s_linear = LinearNoBias(token_s + s_input_dim, token_s)
        self.s_norm = nn.LayerNorm(token_s + s_input_dim)
        self.z_norm = nn.LayerNorm(token_z)
        self.z_linear = LinearNoBias(token_z, token_z)
        self.token_bonds = nn.Linear(
            1 if maximum_bond_distance == 0 else maximum_bond_distance + 2,
            token_z,
            bias=False,
        )
        self.token_bonds_type = nn.Embedding(len(const.bond_types) + 1, token_z)

        self.diffusion_transformer = DiffusionTransformer(
            depth=transformer_args["num_blocks"],
            heads=transformer_args["num_heads"],
            dim=transformer_args["token_s"],
            dim_single_cond=transformer_args["token_s"],
            dim_pairwise=transformer_args["token_z"],
            activation_checkpointing=transformer_args["activation_checkpointing"],
        )
        self.multiplicity_averaging_input = multiplicity_averaging_input
        self.affinity_prediction = affinity_prediction
        self.predict_affinity_value = affinity_args["predict_affinity_value"]
        self.predict_affinity_binary = affinity_args["predict_affinity_binary"]
        self.affinity_out_mlp = nn.Sequential(
            nn.Linear(token_s * 2, token_s),
            nn.ReLU(),
            nn.Linear(token_s, token_s),
            nn.ReLU(),
        )
        self.to_affinity_pred_value = nn.Linear(token_s, 1)
        self.to_affinity_pred_score = LinearNoBias(token_s, 1)
        self.to_affinity_logits_binary = nn.Linear(1, 1)

    def forward(
        self,
        s_inputs,  # Float['b n ts']
        s,  # Float['b n ts']
        z,  # Float['b n n tz']
        x_pred,  # Float['bm m 3']
        feats,
        pred_distogram_logits,
        multiplicity=1,
        s_diffusion=None,
        run_sequentially=False,
    ):
        lig_mask = feats["ligand_affinity_mask"]
        mask = feats["token_pad_mask"] * lig_mask
        s = self.s_linear(self.s_norm(torch.cat([s, s_inputs], dim=-1)))
        z = self.z_linear(self.z_norm(z))
        z = z + self.token_bonds(feats["token_bonds"].float())
        z = z + self.token_bonds_type(feats["type_bonds"].long())

        a = s.clone()
        s = self.diffusion_transformer(s, a, z, mask=mask, multiplicity=1)

        outputs = []
        outputs.append(
            torch.sum(s * lig_mask.unsqueeze(-1), dim=1)
            / (torch.sum(lig_mask.unsqueeze(-1), dim=1) + 1e-7)
        )
        outputs.append(torch.sum(s * lig_mask.unsqueeze(-1), dim=1))
        g = self.affinity_out_mlp(torch.cat(outputs, dim=-1))

        if self.predict_affinity_value:
            affinity_pred_value = self.to_affinity_pred_value(g)

        if self.predict_affinity_binary:
            affinity_pred_score = self.to_affinity_pred_score(g)
            affinity_logits_binary = self.to_affinity_logits_binary(affinity_pred_score)

        out_dict = {}
        if self.predict_affinity_value:
            out_dict["affinity_pred_value"] = affinity_pred_value
        if self.predict_affinity_binary:
            out_dict["affinity_pred_score"] = affinity_pred_score
            out_dict["affinity_logits_binary"] = affinity_logits_binary

        return out_dict
