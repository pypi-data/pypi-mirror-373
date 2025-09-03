import torch
from torch import nn

import foldeverything.model.layers.initialize as init
from foldeverything.data import const
from foldeverything.model.layers.confidence_utils import GaussianSmearing
from foldeverything.model.modules.transformers import DiffusionTransformer
from foldeverything.model.modules.encoders import RelativePositionEncoder
from foldeverything.model.modules.utils import LinearNoBias
from foldeverything.model.layers.transition import Transition
from foldeverything.model.modules.encoders import PairwiseConditioning


class AffinityModuleSingleAtom(nn.Module):
    """Algorithm 31"""

    def __init__(
        self,
        token_s,
        token_z,
        pairformer_args: dict,
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
        self.no_update_s = pairformer_args.get("no_update_s", False)
        if use_gaussian:
            self.gaussian_basis = GaussianSmearing(
                start=2, stop=max_dist, num_gaussians=num_dist_bins
            )
            self.dist_bin_pairwise_linear = nn.Linear(
                num_dist_bins, pairformer_args["token_z"]
            )
            init.gating_init_(self.dist_bin_pairwise_linear.weight)
            init.bias_init_zero_(self.dist_bin_pairwise_linear.bias)
        else:
            boundaries = torch.linspace(2, max_dist, num_dist_bins - 1)
            self.register_buffer("boundaries", boundaries)
            self.dist_bin_pairwise_embed = nn.Embedding(
                num_dist_bins, pairformer_args["token_z"]
            )
            init.gating_init_(self.dist_bin_pairwise_embed.weight)
        s_input_dim = (
            token_s + 2 * const.num_tokens + 1 + len(const.pocket_contact_info)
        )

        self.add_s_to_z_prod = add_s_to_z_prod
        if add_s_to_z_prod:
            self.s_to_z_prod_in1 = LinearNoBias(s_input_dim, token_z)
            self.s_to_z_prod_in2 = LinearNoBias(s_input_dim, token_z)
            self.s_to_z_prod_out = LinearNoBias(token_z, pairformer_args["token_z"])
            init.gating_init_(self.s_to_z_prod_out.weight)

        self.s_norm = nn.LayerNorm(token_s + s_input_dim)
        self.s_linear = LinearNoBias(token_s + s_input_dim, pairformer_args["token_s"])
        self.z_norm = nn.LayerNorm(token_z)
        self.z_linear = LinearNoBias(token_z, pairformer_args["token_z"])

        self.add_s_input_to_s = add_s_input_to_s

        self.add_z_input_to_z = add_z_input_to_z
        if add_z_input_to_z:
            self.rel_pos = RelativePositionEncoder(pairformer_args["token_z"])
            self.token_bonds = nn.Linear(
                1 if maximum_bond_distance == 0 else maximum_bond_distance + 2,
                pairformer_args["token_z"],
                bias=False,
            )
            self.token_bonds_type = nn.Embedding(
                len(const.bond_types) + 1, pairformer_args["token_z"]
            )

        single_transitions = nn.ModuleList([])
        for _ in range(2):
            transition = Transition(
                dim=pairformer_args["token_s"], hidden=4 * pairformer_args["token_s"]
            )
            single_transitions.append(transition)
        self.single_transitions = single_transitions

        self.linear_affinity_feats = nn.Linear(385, pairformer_args["token_s"])
        self.emb_atomized_mask = nn.Embedding(2, pairformer_args["token_s"])
        self.use_s_chem_features = use_s_chem_features
        if use_s_chem_features:
            self.emb_3_aromatic = nn.Embedding(2, pairformer_args["token_s"])
            self.emb_5_aromatic = nn.Embedding(2, pairformer_args["token_s"])
            self.emb_6_aromatic = nn.Embedding(2, pairformer_args["token_s"])
            self.emb_7_aromatic = nn.Embedding(2, pairformer_args["token_s"])
            self.emb_8_aromatic = nn.Embedding(2, pairformer_args["token_s"])
            self.emb_num_aromatic_rings = nn.Embedding(5, pairformer_args["token_s"])
            self.emb_degree = nn.Embedding(7, pairformer_args["token_s"])
            self.emb_imp_valence = nn.Embedding(7, pairformer_args["token_s"])
            self.emb_exp_valence = nn.Embedding(7, pairformer_args["token_s"])
            self.emb_conn_hs = nn.Embedding(4, pairformer_args["token_s"])
            # self.emb_rad_e = nn.Embedding(8, pairformer_args["token_s"])
            self.emb_hybrid = nn.Embedding(9, pairformer_args["token_s"])
            self.emb_res_type = nn.Linear(const.num_tokens, pairformer_args["token_s"])

        self.diffusion_transformer = DiffusionTransformer(
            depth=pairformer_args["num_blocks"],
            heads=pairformer_args["num_heads"],
            dim=pairformer_args["token_s"],
            dim_single_cond=pairformer_args["token_s"],
            dim_pairwise=pairformer_args["token_z"],
            activation_checkpointing=pairformer_args["activation_checkpointing"],
        )
        self.multiplicity_averaging_input = multiplicity_averaging_input
        self.affinity_prediction = affinity_prediction
        if affinity_prediction:
            self.affinity_heads = AffinityHeads(
                pairformer_args["token_s"],
                **affinity_args,
            )

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
        affinity_token_to_atom = feats["affinity_token_to_atom"].float()
        affinity_token_to_token = torch.bmm(
            affinity_token_to_atom.float(), feats["atom_to_token"].float()
        )  # token, aff

        effective_multiplicity = (
            1 if self.multiplicity_averaging_input else multiplicity
        )
        s = self.s_linear(self.s_norm(torch.cat([s, s_inputs], dim=-1)))

        # switch to atom level for closest
        s = torch.einsum("bmz,bam->baz", s, affinity_token_to_token)

        # add atom information to s affinity tokens
        token_affinity_feats = torch.bmm(
            affinity_token_to_atom,
            torch.cat(
                [
                    feats["ref_charge"].unsqueeze(-1),  # 1
                    feats["ref_element"],  # 128
                    feats["ref_atom_name_chars"].reshape(
                        feats["ref_atom_name_chars"].shape[0],
                        feats["ref_atom_name_chars"].shape[1],
                        -1,
                    ),  # 4 * 64
                ],
                dim=-1,
            ).float(),
        )
        s = s + self.linear_affinity_feats(token_affinity_feats)
        s = s + self.emb_atomized_mask(feats["token_affinity_atomized_atom_mask"])
        if self.use_s_chem_features:
            s = s + self.emb_3_aromatic(feats["token_affinity_is_3_aromatic"])
            s = s + self.emb_5_aromatic(feats["token_affinity_is_5_aromatic"])
            s = s + self.emb_6_aromatic(feats["token_affinity_is_6_aromatic"])
            s = s + self.emb_7_aromatic(feats["token_affinity_is_7_aromatic"])
            s = s + self.emb_8_aromatic(feats["token_affinity_is_8_aromatic"])
            s = s + self.emb_num_aromatic_rings(
                feats["token_affinity_num_aromatic_rings"]
            )
            s = s + self.emb_degree(feats["token_affinity_degree"])
            s = s + self.emb_imp_valence(feats["token_affinity_imp_valence"])
            s = s + self.emb_exp_valence(feats["token_affinity_exp_valence"])
            s = s + self.emb_conn_hs(feats["token_affinity_conn_hs"])
            # s = s + self.emb_rad_e(feats["rad_e"])
            s = s + self.emb_hybrid(feats["token_affinity_hybrid"])
            s = s + self.emb_res_type(
                torch.bmm(affinity_token_to_token, feats["res_type"].float())
            )
            # token_affinity_residue

        for i, transition in enumerate(self.single_transitions):
            if i == 0:  # noqa: SIM108, SIM108, SIM108, SIM108, SIM108
                a = s + transition(s)
            else:
                a = a + transition(a)

        s = s.repeat_interleave(effective_multiplicity, 0)
        a = a.repeat_interleave(effective_multiplicity, 0)

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
        z = torch.einsum(
            "bmaz,bcm->bcaz",
            torch.einsum("bmnz,ban->bmaz", z, affinity_token_to_token),
            affinity_token_to_token,
        )
        z = z.repeat_interleave(effective_multiplicity, 0)

        token_to_rep_atom = affinity_token_to_atom
        token_to_rep_atom = token_to_rep_atom.repeat_interleave(multiplicity, 0)
        if len(x_pred.shape) == 4:
            B, mult, N, _ = x_pred.shape
            x_pred = x_pred.reshape(B * mult, N, -1)
        else:
            BM, N, _ = x_pred.shape
            B = BM // multiplicity
            mult = multiplicity
        x_pred_repr = torch.bmm(token_to_rep_atom.float(), x_pred)
        d = torch.cdist(x_pred_repr, x_pred_repr)
        if self.multiplicity_averaging_input and multiplicity > 1:
            distogram = []
            for i in range(B):
                x_pred_repr_chunk = x_pred_repr[i * mult : (i + 1) * mult]
                d_chunk = torch.cdist(x_pred_repr_chunk, x_pred_repr_chunk)
                if self.use_gaussian:
                    distogram.append(
                        self.dist_bin_pairwise_linear(
                            self.gaussian_basis(d_chunk)
                        ).mean(dim=0, keepdim=True)
                    )
                else:
                    distogram.append(
                        self.dist_bin_pairwise_embed(
                            (d_chunk.unsqueeze(-1) > self.boundaries).sum(dim=-1).long()
                        ).mean(dim=0, keepdim=True)
                    )
            distogram = torch.cat(distogram, dim=0)
        else:
            if self.use_gaussian:
                distogram = self.dist_bin_pairwise_linear(self.gaussian_basis(d))
            else:
                distogram = (d.unsqueeze(-1) > self.boundaries).sum(dim=-1).long()
                distogram = self.dist_bin_pairwise_embed(distogram)
            if self.multiplicity_averaging_input and multiplicity > 1:
                B, N, N, DZ = distogram.shape
                distogram = distogram.view(
                    B // multiplicity, multiplicity, N, N, DZ
                ).mean(dim=1)

        z = z + distogram

        mask = feats["affinity_token_pad_mask"].repeat_interleave(
            effective_multiplicity, 0
        )

        s = self.diffusion_transformer(
            s, a, z, mask=mask, multiplicity=effective_multiplicity
        )

        out_dict = {}

        # affinity heads
        if self.affinity_prediction:
            if self.multiplicity_averaging_input and multiplicity > 1:
                B, N, N = d.shape
                d = d.view(B // multiplicity, multiplicity, N, N).mean(dim=1)
            out_dict.update(
                self.affinity_heads(
                    s=s, d=d, feats=feats, multiplicity=effective_multiplicity
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
        affinity_token_to_atom = feats["affinity_token_to_atom"].float()
        affinity_token_to_token = torch.bmm(
            affinity_token_to_atom.float(), feats["atom_to_token"].float()
        )
        lig_mask = torch.bmm(
            affinity_token_to_token, feats["ligand_affinity_mask"].unsqueeze(-1)
        ).repeat_interleave(effective_multiplicity, 0)
        atomized_rec_mask = (
            feats["token_affinity_atomized_atom_mask"]
            .repeat_interleave(effective_multiplicity, 0)
            .float()
        ).unsqueeze(-1)
        mask = (
            feats["affinity_token_pad_mask"]
            .repeat_interleave(effective_multiplicity, 0)
            .unsqueeze(-1)
        )

        lig_mask = lig_mask * mask
        atomized_rec_mask = atomized_rec_mask * mask
        rec_mask = (1 - lig_mask - atomized_rec_mask) * mask

        outputs = []

        if "lig_s" in self.aggregation_heads:
            outputs.append(
                torch.sum(s * lig_mask, dim=1) / (torch.sum(lig_mask, dim=1) + 1e-7)
            )
        if "atomized_rec_s" in self.aggregation_heads:
            outputs.append(
                torch.sum(s * atomized_rec_mask, dim=1)
                / (torch.sum(atomized_rec_mask, dim=1) + 1e-7)
            )
        if "rec_s" in self.aggregation_heads:
            outputs.append(
                torch.sum(s * rec_mask, dim=1) / (torch.sum(rec_mask, dim=1) + 1e-7)
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
