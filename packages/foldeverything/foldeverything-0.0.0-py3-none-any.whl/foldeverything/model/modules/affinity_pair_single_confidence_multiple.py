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


class AffinityModulePairSingleConfidenceMultiple(nn.Module):
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
        self.token_s = token_s
        self.token_z = token_z
        self.no_trunk_feats = no_trunk_feats
        self.use_s_diffusion = use_s_diffusion
        self.max_num_atoms_per_token = 23
        self.use_gaussian = use_gaussian
        self.no_update_s = pairformer_args.get("no_update_s", False)
        if use_gaussian:
            self.gaussian_basis = GaussianSmearing(
                start=2, stop=max_dist, num_gaussians=num_dist_bins
            )
            self.dist_bin_pairwise_linear = nn.Linear(num_dist_bins, token_z)
            init.gating_init_(self.dist_bin_pairwise_linear.weight)
            init.bias_init_zero_(self.dist_bin_pairwise_linear.bias)
        else:
            boundaries = torch.linspace(2, max_dist, num_dist_bins - 1)
            self.register_buffer("boundaries", boundaries)
            self.dist_bin_pairwise_embed = nn.Embedding(num_dist_bins, token_z)
            init.gating_init_(self.dist_bin_pairwise_embed.weight)
        s_input_dim = (
            token_s + 2 * const.num_tokens + 1 + len(const.pocket_contact_info)
        )

        self.add_s_to_z_prod = add_s_to_z_prod
        if add_s_to_z_prod:
            self.s_to_z_prod_in1 = LinearNoBias(s_input_dim, token_z)
            self.s_to_z_prod_in2 = LinearNoBias(s_input_dim, token_z)
            self.s_to_z_prod_out = LinearNoBias(token_z, token_z)
            init.gating_init_(self.s_to_z_prod_out.weight)

        self.s_norm = nn.LayerNorm(token_s + s_input_dim)
        self.s_linear = LinearNoBias(token_s + s_input_dim, token_s)
        self.z_norm = nn.LayerNorm(token_z)
        self.z_linear = LinearNoBias(token_z, token_z)
        self.s_norm_conf = nn.LayerNorm(token_s)
        self.s_linear_conf = LinearNoBias(token_s, token_s)
        self.z_norm_conf = nn.LayerNorm(token_z)
        self.z_linear_conf = LinearNoBias(token_z, token_z)

        self.add_s_input_to_s = add_s_input_to_s

        self.add_z_input_to_z = add_z_input_to_z
        if add_z_input_to_z:
            self.rel_pos = RelativePositionEncoder(token_z)
            self.token_bonds = nn.Linear(
                1 if maximum_bond_distance == 0 else maximum_bond_distance + 2,
                token_z,
                bias=False,
            )
            self.token_bonds_type = nn.Embedding(len(const.bond_types) + 1, token_z)
        self.pairwise_conditioner = PairwiseConditioning(
            token_z=token_z,
            dim_token_rel_pos_feats=token_z,
            num_transitions=2,
        )

        self.use_s_chem_features = use_s_chem_features
        if use_s_chem_features:
            self.emb_3_aromatic = nn.Embedding(2, token_s)
            self.emb_5_aromatic = nn.Embedding(2, token_s)
            self.emb_6_aromatic = nn.Embedding(2, token_s)
            self.emb_7_aromatic = nn.Embedding(2, token_s)
            self.emb_8_aromatic = nn.Embedding(2, token_s)
            self.emb_num_aromatic_rings = nn.Embedding(5, token_s)
            self.emb_degree = nn.Embedding(7, token_s)
            self.emb_imp_valence = nn.Embedding(7, token_s)
            self.emb_exp_valence = nn.Embedding(7, token_s)
            self.emb_conn_hs = nn.Embedding(4, token_s)
            self.emb_hybrid = nn.Embedding(9, token_s)
        self.emb_res_type = LinearNoBias(const.num_tokens, token_s)
        self.emb_ligand_mask = LinearNoBias(2, token_s)
        pairformer_class = MiniformerModule if use_miniformer else PairformerModule
        self.pairformer_stack = pairformer_class(
            token_s,
            token_z,
            samples_axial_attention=samples_axial_attention,
            **pairformer_args,
        )

        self.single_transitions_a = nn.ModuleList([])
        self.single_transitions_a.append(
            Transition(
                dim=token_s, hidden=4 * token_s, out_dim=transformer_args["token_s"]
            )
        )
        self.single_transitions_a.append(
            Transition(
                dim=transformer_args["token_s"],
                hidden=4 * transformer_args["token_s"],
                out_dim=transformer_args["token_s"],
            )
        )

        self.single_transitions_s = nn.ModuleList([])
        self.single_transitions_s.append(
            Transition(
                dim=token_s, hidden=4 * token_s, out_dim=transformer_args["token_s"]
            )
        )
        self.single_transitions_s.append(
            Transition(
                dim=transformer_args["token_s"],
                hidden=4 * transformer_args["token_s"],
                out_dim=transformer_args["token_s"],
            )
        )

        self.pair_transition_z = Transition(
            dim=token_z, hidden=4 * token_z, out_dim=transformer_args["token_z"]
        )

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
        if affinity_prediction:
            self.affinity_heads = AffinityHeads(
                transformer_args["token_s"],
                **affinity_args,
            )

    def forward(
        self,
        s_inputs,  # Float['b n ts']
        s,  # Float['b n ts']
        z,  # Float['b n n tz']
        s_conf,
        z_conf,
        x_pred,  # Float['bm m 3']
        feats,
        pred_distogram_logits,
        multiplicity=1,
        s_diffusion=None,
        run_sequentially=False,
    ):
        if len(x_pred.shape) == 4:
            B, mult, N, _ = x_pred.shape
            x_pred = x_pred.reshape(B * multiplicity, N, -1)
        else:
            BM, N, _ = x_pred.shape
            B = BM // multiplicity

        s = self.s_linear(self.s_norm(torch.cat([s, s_inputs], dim=-1)))
        if self.use_s_chem_features:
            s = s + self.emb_3_aromatic(feats["is_3_aromatic"])
            s = s + self.emb_5_aromatic(feats["is_5_aromatic"])
            s = s + self.emb_6_aromatic(feats["is_6_aromatic"])
            s = s + self.emb_7_aromatic(feats["is_7_aromatic"])
            s = s + self.emb_8_aromatic(feats["is_8_aromatic"])
            s = s + self.emb_num_aromatic_rings(feats["num_aromatic_rings"])
            s = s + self.emb_degree(feats["degree"])
            s = s + self.emb_imp_valence(feats["imp_valence"])
            s = s + self.emb_exp_valence(feats["exp_valence"])
            s = s + self.emb_conn_hs(feats["conn_hs"])
            s = s + self.emb_hybrid(feats["hybrid"])

        s = s + self.emb_res_type(feats["res_type"].float())
        s = s + self.emb_ligand_mask(
            one_hot(feats["ligand_affinity_mask"].long(), num_classes=2).float()
        )

        z = self.z_linear(self.z_norm(z))
        if self.add_z_input_to_z:
            relative_position_encoding = self.rel_pos(feats)
            z = z + relative_position_encoding
            z = z + self.token_bonds(feats["token_bonds"].float())
            z = z + self.token_bonds_type(feats["type_bonds"].long())

        if self.add_s_to_z_prod:
            z = z + self.s_to_z_prod_out(
                self.s_to_z_prod_in1(s_inputs)[:, :, None, :]
                * self.s_to_z_prod_in2(s_inputs)[:, None, :, :]
            )
        z = z.repeat_interleave(multiplicity, 0)
        s = s.repeat_interleave(multiplicity, 0)
        token_to_rep_atom = feats["token_to_rep_atom"].repeat_interleave(
            multiplicity, 0
        )
        x_pred_repr = torch.bmm(token_to_rep_atom.float(), x_pred)

        s = s + self.s_linear_conf(self.s_norm_conf(s_conf))
        z = z + self.z_linear_conf(self.z_norm_conf(z_conf))

        d = torch.cdist(x_pred_repr, x_pred_repr)
        if self.use_gaussian:
            distogram = self.dist_bin_pairwise_linear(self.gaussian_basis(d))
        else:
            distogram = self.dist_bin_pairwise_embed(
                (d.unsqueeze(-1) > self.boundaries).sum(dim=-1).long()
            )
        z = z + self.pairwise_conditioner(z_trunk=z, token_rel_pos_feats=distogram)
        mask = feats["token_pad_mask"].repeat_interleave(multiplicity, 0)
        pair_mask = mask[:, :, None] * mask[:, None, :]

        s, z = self.pairformer_stack(
            s,
            z,
            mask=mask,
            pair_mask=pair_mask,
            multiplicity=1,
        )

        s = s.reshape(B, multiplicity, *s.shape[1:])
        z = z.reshape(B, multiplicity, *z.shape[1:])
        s = torch.mean(s, dim=1)
        z = torch.mean(z, dim=1)

        for i, transition in enumerate(self.single_transitions_a):
            if i == 0:  # noqa: SIM108, SIM108, SIM108, SIM108, SIM108
                a = transition(s)
            else:
                a = a + transition(a)

        for i, transition in enumerate(self.single_transitions_s):
            if i == 0:  # noqa: SIM108, SIM108, SIM108, SIM108, SIM108
                s = transition(s)
            else:
                s = s + transition(s)

        z = self.pair_transition_z(z)

        s = self.diffusion_transformer(
            s, a, z, mask=feats["token_pad_mask"], multiplicity=1
        )

        out_dict = {}

        # affinity heads
        if self.affinity_prediction:
            # TODO: change d
            out_dict.update(
                self.affinity_heads(
                    s=s, d=d[::multiplicity], feats=feats, multiplicity=1
                )
            )
        return out_dict


class AffinityHeads(nn.Module):
    def __init__(
        self,
        token_s,
        aggregation_heads,
        interface_cutoff=10,
        multiplicity_averaging=False,
        predict_affinity_value=False,
        predict_affinity_binary=False,
        conditioning_activity_type=False,
        num_activity_types=2,
    ):
        super().__init__()
        self.aggregation_heads = aggregation_heads
        input_size = token_s * len([a for a in aggregation_heads if a[-1] == "s"])
        self.interface_cutoff = interface_cutoff
        self.multiplicity_averaging = multiplicity_averaging
        self.predict_affinity_value = predict_affinity_value
        self.predict_affinity_binary = predict_affinity_binary
        self.conditioning_activity_type = conditioning_activity_type
        if self.conditioning_activity_type:
            self.activity_type_embed = nn.Embedding(num_activity_types, input_size)
            input_size += 1
        if predict_affinity_value:
            self.to_affinity_pred_value = nn.Linear(input_size, 1)
        if predict_affinity_binary:
            self.to_affinity_pred_score = LinearNoBias(input_size, 1)
            self.to_affinity_logits_binary = nn.Linear(1, 1)
            with torch.no_grad():
                self.to_affinity_logits_binary.weight.fill_(1.0)
                self.to_affinity_logits_binary.bias.fill_(0.0)
        self.affinity_out_mlp = nn.Sequential(
            nn.Linear(input_size, input_size),
            nn.ReLU(),
            nn.Linear(input_size, input_size),
            nn.ReLU(),
        )

    def forward(
        self,
        s,
        d,
        feats,
        multiplicity=1,
    ):
        if self.multiplicity_averaging and multiplicity > 1:
            B, N, DS = s.shape
            s = s.view(B // multiplicity, multiplicity, N, DS).mean(dim=1)
            effective_multiplicity = 1
        else:
            effective_multiplicity = multiplicity

        # NOTE: ligand_affinity_mask is a ranodm asym_id mask if no ligand (for confidence)
        lig_mask = (
            feats["ligand_affinity_mask"]
            .repeat_interleave(effective_multiplicity, 0)
            .unsqueeze(-1)
        )
        mask = (
            feats["token_pad_mask"]
            .repeat_interleave(effective_multiplicity, 0)
            .unsqueeze(-1)
        )

        lig_mask = lig_mask * mask
        rec_mask = (1 - lig_mask) * mask

        pair_mask = (
            mask[:, :, None]
            * mask[:, None, :]
            * (1 - torch.eye(mask.shape[1], device=mask.device))
            .unsqueeze(0)
            .unsqueeze(-1)
        )
        lig_pair_mask = (
            lig_mask[:, :, None]
            * lig_mask[:, None, :]
            * (1 - torch.eye(mask.shape[1], device=mask.device))
            .unsqueeze(0)
            .unsqueeze(-1)
        )
        rec_pair_mask = (
            rec_mask[:, :, None]
            * rec_mask[:, None, :]
            * (1 - torch.eye(mask.shape[1], device=mask.device))
            .unsqueeze(0)
            .unsqueeze(-1)
        )
        cross_pair_mask = pair_mask - lig_pair_mask - rec_pair_mask

        if self.multiplicity_averaging and multiplicity > 1:
            inter_pair_mask = (d.unsqueeze(-1) < self.interface_cutoff).view(
                B // multiplicity, multiplicity, N, N, 1
            ).float().mean(dim=1) * cross_pair_mask
        else:
            inter_pair_mask = (
                d.unsqueeze(-1) < self.interface_cutoff
            ) * cross_pair_mask
        inter_mask = torch.max(inter_pair_mask, dim=1).values

        outputs = []

        if "lig_s" in self.aggregation_heads:
            outputs.append(
                torch.sum(s * lig_mask, dim=1) / (torch.sum(lig_mask, dim=1) + 1e-7)
            )

        if "lig_sum_s" in self.aggregation_heads:
            outputs.append(torch.sum(s * lig_mask, dim=1) / 50)

        if "rec_s" in self.aggregation_heads:
            outputs.append(
                torch.sum(s * rec_mask, dim=1) / (torch.sum(rec_mask, dim=1) + 1e-7)
            )

        if "lig_inter_s" in self.aggregation_heads:
            outputs.append(
                torch.sum(s * inter_mask * lig_mask, dim=1)
                / (torch.sum(inter_mask * lig_mask, dim=1) + 1e-7)
            )

        if "rec_inter_s" in self.aggregation_heads:
            outputs.append(
                torch.sum(s * inter_mask * rec_mask, dim=1)
                / (torch.sum(inter_mask * rec_mask, dim=1) + 1e-7)
            )

        g = torch.cat(outputs, dim=-1)

        if self.conditioning_activity_type:
            activity_type = (
                feats["activity_type"]
                .reshape(-1)
                .repeat_interleave(effective_multiplicity, 0)
            )
            activity_type_emb = self.activity_type_embed(activity_type)
            g = torch.cat([g * activity_type_emb, activity_type.unsqueeze(-1)], dim=-1)

        g = self.affinity_out_mlp(g)

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
