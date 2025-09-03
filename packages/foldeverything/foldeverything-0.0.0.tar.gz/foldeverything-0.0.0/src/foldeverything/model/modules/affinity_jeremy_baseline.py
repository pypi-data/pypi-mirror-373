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


class AffinityModuleJeremyBaseline(nn.Module):
    """Algorithm 31"""

    def __init__(
        self,
        token_s,
        token_z,
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
        use_cross_transformer: bool = False,
        compute_pae: bool = False,
        imitate_trunk=False,
        full_embedder_args: dict = None,
        msa_args: dict = None,
        compile_pairformer=False,
        samples_axial_attention=False,
        multiplicity_averaging_input=False,
        expand_to_atom_level=False,
        use_s_chem_features=False,
        embed_atom_ligand=False,
    ):
        super().__init__()
        self.no_trunk_feats = no_trunk_feats
        self.use_s_diffusion = use_s_diffusion
        self.max_num_atoms_per_token = 23
        self.use_gaussian = use_gaussian
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
        self.z_norm = nn.LayerNorm(token_z)
        self.z_linear = LinearNoBias(token_z, token_z)
        self.add_s_input_to_s = add_s_input_to_s
        self.add_z_input_to_z = add_z_input_to_z
        self.pairwise_conditioner = PairwiseConditioning(
            token_z=token_z,
            dim_token_rel_pos_feats=token_z,
            num_transitions=2,
        )
        self.use_s_chem_features = use_s_chem_features
        self.embed_atom_ligand = embed_atom_ligand
        self.pair_transition_z = nn.Sequential(
            nn.Linear(token_z, 4 * token_z),
            nn.ReLU(),
            nn.Linear(4 * token_z, 4 * token_z),
            nn.ReLU(),
            nn.Linear(4 * token_z, 4 * token_z),
            nn.ReLU(),
            nn.Linear(4 * token_z, token_z),
            nn.ReLU(),
        )

        self.multiplicity_averaging_input = multiplicity_averaging_input
        self.affinity_prediction = affinity_prediction
        if affinity_prediction:
            if use_cross_transformer:
                self.affinity_heads = AffinityHeadsTransformer(
                    token_z,
                    **affinity_args,
                )
            else:
                raise Exception

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
        effective_multiplicity = (
            1 if self.multiplicity_averaging_input else multiplicity
        )
        z = self.z_linear(self.z_norm(z))
        z = z.repeat_interleave(effective_multiplicity, 0)

        token_to_rep_atom = feats["token_to_rep_atom"]
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

        # atom_mask_ligand = torch.bmm(
        #     feats["atom_to_token"].float(),
        #     feats["ligand_affinity_mask"].unsqueeze(-1).float(),
        # ).squeeze(-1)

        # d_all_atom = (
        #     torch.cdist(x_pred, x_pred)
        #     + (
        #         1
        #         - (feats["atom_pad_mask"][:, None] * feats["atom_pad_mask"][:, :, None])
        #     )
        #     * 1000
        # )
        # group_indices = feats["atom_to_token"].argmax(-1)
        # out = torch.full(
        #     (
        #         feats["atom_to_token"].shape[0],
        #         feats["atom_to_token"].shape[-1],
        #     ),
        #     1000,
        #     device=x_pred.device,
        # )
        # out = out.scatter_reduce(
        #     1, group_indices, d_all_atom.min(-1).values, reduce="min", include_self=True
        # )
        z = z + self.pairwise_conditioner(z_trunk=z, token_rel_pos_feats=distogram)
        z = self.pair_transition_z(z)

        out_dict = {}

        # affinity heads
        if self.affinity_prediction:
            if self.multiplicity_averaging_input and multiplicity > 1:
                B, N, N = d.shape
                d = d.view(B // multiplicity, multiplicity, N, N).mean(dim=1)
            out_dict.update(
                self.affinity_heads(
                    z=z, d=d, feats=feats, multiplicity=effective_multiplicity
                )
            )
        return out_dict


class AffinityHeadsTransformer(nn.Module):
    def __init__(
        self,
        token_z,
        aggregation_heads,
        interface_cutoff=10,
        multiplicity_averaging=False,
        predict_affinity_value=False,
        predict_affinity_binary=False,
        conditioning_activity_type=False,
        num_activity_types=2,
        groups={},
        val_groups={},
    ):
        super().__init__()
        self.aggregation_heads = aggregation_heads
        self.groups = groups
        input_size = token_z * len([a for a in aggregation_heads if a[-1] == "z"])
        self.interface_cutoff = interface_cutoff
        self.multiplicity_averaging = multiplicity_averaging
        self.predict_affinity_value = predict_affinity_value
        self.predict_affinity_binary = predict_affinity_binary
        self.conditioning_activity_type = conditioning_activity_type
        if self.conditioning_activity_type:
            self.activity_type_embed = nn.Embedding(num_activity_types, input_size)
            input_size += 1
        if predict_affinity_value:
            self.to_affinity_pred_value = nn.Linear(768, 1)
        if predict_affinity_binary:
            self.to_affinity_pred_score = LinearNoBias(768, 1)
            self.to_affinity_logits_binary = nn.Linear(1, 1)
            with torch.no_grad():
                self.to_affinity_logits_binary.weight.fill_(1.0)
                self.to_affinity_logits_binary.bias.fill_(0.0)

        if predict_affinity_value:
            self.to_affinity_pred_value_group = nn.Linear(768, 1)
        if predict_affinity_binary:
            self.to_affinity_pred_score_group = LinearNoBias(768, 1)
            self.to_affinity_logits_binary_group = nn.Linear(1, 1)
            with torch.no_grad():
                self.to_affinity_logits_binary_group.weight.fill_(1.0)
                self.to_affinity_logits_binary_group.bias.fill_(0.0)

        # MLP with unput size input_size and 3 layers
        # with 2 hidden layers of size input_size and output layer of size 1
        self.affinity_out_mlp = nn.Sequential(
            nn.Linear(input_size, 4 * input_size),
            nn.ReLU(),
            nn.Linear(4 * input_size, 4 * input_size),
            nn.ReLU(),
            nn.Linear(4 * input_size, 4 * input_size),
            nn.ReLU(),
            nn.Linear(4 * input_size, 768),
            nn.ReLU(),
        )

        self.linear_affinity_true = LinearNoBias(1, 768)
        self.gaussian_basis = GaussianSmearing(start=-5, stop=3, num_gaussians=128)
        self.linear_affinity_true_gaussian = LinearNoBias(128, 768)

        self.linear_mask = LinearNoBias(1, 768)
        self.norm_pre_transformer = nn.LayerNorm(768)
        self.cross_transformer = DiffusionTransformer(
            depth=12, heads=8, dim=768, pair_bias_attn=False
        )

    def forward(
        self,
        z,
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

        outputs = []

        if "lig_rec_z" in self.aggregation_heads:
            outputs.append(
                torch.sum(z * cross_pair_mask, dim=(1, 2))
                / (torch.sum(cross_pair_mask, dim=(1, 2)) + 1e-7)
            )
        if "lig_rec_sum_z" in self.aggregation_heads:
            outputs.append(
                torch.sum(
                    torch.sum(z * cross_pair_mask, dim=1)
                    / (torch.sum(cross_pair_mask, dim=1) + 1e-7),
                    dim=1,
                )
                / 30
            )
        if "lig_rec_sum_sum_z" in self.aggregation_heads:
            outputs.append(torch.sum(z * cross_pair_mask, dim=(1, 2)) / 1000)
        if "interface_z" in self.aggregation_heads:
            outputs.append(
                torch.sum(z * inter_pair_mask, dim=(1, 2))
                / (torch.sum(inter_pair_mask, dim=(1, 2)) + 1e-7)
            )
        if "interface_sum_z" in self.aggregation_heads:
            outputs.append(
                torch.sum(
                    torch.sum(z * inter_pair_mask, dim=1)
                    / (torch.sum(inter_pair_mask, dim=1) + 1e-7),
                    dim=1,
                )
                / 30
            )
        if "interface_sum_sum_z" in self.aggregation_heads:
            outputs.append(torch.sum(z * inter_pair_mask, dim=(1, 2)) / 1000)

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

        affinity_values_true = feats["affinity"].reshape(-1, 1)
        if self.training:
            tot_groups = sum(self.groups.values()) - self.groups[0]

            affinity_values_true_masked = (
                affinity_values_true.reshape(1, -1)
                * feats["mask_known_cross_transformer"]
            ).unsqueeze(-1)
            g_input_concat = (
                g.unsqueeze(0)
                + self.linear_affinity_true(affinity_values_true_masked)
                + self.linear_mask(feats["mask_known_cross_transformer"].unsqueeze(-1))
                + self.linear_affinity_true_gaussian(
                    self.gaussian_basis(affinity_values_true.reshape(-1)).unsqueeze(0)
                    * feats["mask_known_cross_transformer"].unsqueeze(-1)
                )
            )
            g_input_concat = self.norm_pre_transformer(g_input_concat)
            g_new = self.cross_transformer(
                g_input_concat,
                g_input_concat,
                mask=feats["mask_attn_cross_transformer"],
            )

            if self.predict_affinity_value:
                affinity_pred_value_all = self.to_affinity_pred_value_group(g_new)
                affinity_pred_value = affinity_pred_value_all[
                    feats["mask_unknown_cross_transformer"].bool()
                ].reshape(-1, tot_groups)
                affinity_pred_value_0 = self.to_affinity_pred_value(g).reshape(-1, 1)
                affinity_pred_value = torch.cat(
                    [affinity_pred_value_0, affinity_pred_value], dim=1
                )

            if self.predict_affinity_binary:
                affinity_pred_score_all = self.to_affinity_pred_score_group(g_new)
                affinity_logits_binary_all = self.to_affinity_logits_binary_group(
                    affinity_pred_score_all
                )
                affinity_pred_score = affinity_pred_score_all[
                    feats["mask_unknown_cross_transformer"].bool()
                ].reshape(-1, tot_groups)
                affinity_logits_binary = affinity_logits_binary_all[
                    feats["mask_unknown_cross_transformer"].bool()
                ].reshape(-1, tot_groups)
                affinity_pred_score_0 = self.to_affinity_pred_score(g).reshape(-1, 1)
                affinity_logits_binary_0 = self.to_affinity_logits_binary(
                    affinity_pred_score_0
                ).reshape(-1, 1)
                affinity_pred_score = torch.cat(
                    [affinity_pred_score_0, affinity_pred_score], dim=1
                )
                affinity_logits_binary = torch.cat(
                    [affinity_logits_binary_0, affinity_logits_binary], dim=1
                )

            out_dict = {}
            if self.predict_affinity_value:
                out_dict["affinity_pred_value"] = affinity_pred_value
            if self.predict_affinity_binary:
                out_dict["affinity_pred_score"] = affinity_pred_score
                out_dict["affinity_logits_binary"] = affinity_logits_binary

            return out_dict
        else:
            # if "mask_known_cross_transformer" in feats:
            #     affinity_values_true_masked = (
            #         affinity_values_true.reshape(1, -1)
            #         * feats["mask_known_cross_transformer"]
            #     ).unsqueeze(-1)
            #     g_input_concat = (
            #         g.unsqueeze(0)
            #         + self.linear_affinity_true(affinity_values_true_masked)
            #         + self.linear_mask(
            #             feats["mask_known_cross_transformer"].unsqueeze(-1)
            #         )
            #         + self.linear_affinity_true_gaussian(
            #             self.gaussian_basis(affinity_values_true.reshape(-1)).unsqueeze(
            #                 0
            #             )
            #             * feats["mask_known_cross_transformer"].unsqueeze(-1)
            #         )
            #     )
            #     g_input_concat = self.norm_pre_transformer(g_input_concat)
            #     g_new = self.cross_transformer(
            #         g_input_concat,
            #         g_input_concat,
            #         mask=feats["mask_attn_cross_transformer"],
            #     )

            # affinity_pred_value_0 = self.to_affinity_pred_value(g[feats["ids_unknown_group0"]])
            # affinity_pred_score_0 = self.to_affinity_pred_score(
            #     g[feats["ids_unknown_group0"]]
            # )
            # affinity_logits_binary_0 = self.to_affinity_logits_binary(
            #     affinity_pred_score_0
            # )

            # if self.predict_affinity_value:
            #     if "mask_known_cross_transformer" in feats:
            #         affinity_pred_value_all = self.to_affinity_pred_value_group(g_new)
            #         affinity_pred_value = affinity_pred_value_all[
            #             feats["mask_unknown_cross_transformer"].bool()
            #         ]
            #     torch.cat([affinity_pred_value_0, affinity_pred_value], dim=0)[feats["i_unknown_groups"]]
            # affinity_pred_value_list = []
            # count = 0
            # for i in range(B):
            #     if i in feats["i_unknown_group0"]:
            #         affinity_pred_value_list.append(idx_B_to_pred_value[i])
            #     else:
            #         affinity_pred_value_list.append(
            #             affinity_pred_value[count : count + 1]
            #         )
            #     count += 1
            # affinity_pred_value = torch.cat(affinity_pred_value_list, dim=0)

            # if self.predict_affinity_binary:
            #     if "mask_known_cross_transformer" in feats:
            #         affinity_pred_score_all = self.to_affinity_pred_score_group(g_new)
            #         affinity_logits_binary_all = self.to_affinity_logits_binary_group(
            #             affinity_pred_score_all
            #         )
            #         affinity_pred_score = affinity_pred_score_all[
            #             mask_unknown_concat.bool()
            #         ]
            #         affinity_logits_binary = affinity_logits_binary_all[
            #             mask_unknown_concat.bool()
            #         ]

            #     affinity_pred_score_list = []
            #     affinity_pred_binary_list = []
            #     count = 0
            #     for i in range(B):
            #         if i in idx_B_to_pred_score:
            #             affinity_pred_score_list.append(idx_B_to_pred_score[i])
            #             affinity_pred_binary_list.append(idx_B_to_logits_binary[i])
            #         else:
            #             affinity_pred_score_list.append(
            #                 affinity_pred_score[count : count + 1]
            #             )
            #             affinity_pred_binary_list.append(
            #                 affinity_logits_binary[count : count + 1]
            #             )
            #         count += 1
            #     affinity_pred_score = torch.cat(affinity_pred_score_list, dim=0)
            #     affinity_logits_binary = torch.cat(affinity_pred_binary_list, dim=0)

            unique_idx_cross_transformer = feats["unique_idx_cross_transformer"]
            affinity_template_mask = feats["affinity_template_mask"]
            unique_idx_cross_transformer_unique = (
                unique_idx_cross_transformer.unique().tolist()
            )
            B = len(unique_idx_cross_transformer_unique)

            mask_attn_concat = []
            mask_unknown_concat = []
            g_input_concat = []
            idx_B_to_pred_value = {}
            idx_B_to_pred_score = {}
            idx_B_to_logits_binary = {}

            for i in range(B):
                idx_cross_transformer = unique_idx_cross_transformer_unique[i]
                mask_unique_idx_cross_transformer = (
                    unique_idx_cross_transformer == idx_cross_transformer
                ).float()

                # sample a list of K elements from the elements that are true in mask_same_aid
                mask_attn = mask_unique_idx_cross_transformer.unsqueeze(0).squeeze(-1)

                mask_known = affinity_template_mask * mask_unique_idx_cross_transformer

                mask_unknown = (
                    1 - affinity_template_mask
                ) * mask_unique_idx_cross_transformer

                affinity_values_true_masked = affinity_values_true * mask_known
                g_concat = (
                    g
                    + self.linear_affinity_true(affinity_values_true_masked)
                    + self.linear_mask(mask_known)
                    + self.linear_affinity_true_gaussian(
                        self.gaussian_basis(affinity_values_true.squeeze(-1))
                        * mask_known
                    )
                )

                group = int(mask_unique_idx_cross_transformer.sum().item())
                if group == 1:
                    idx_unknown = torch.where(mask_unknown.reshape(-1))[0].item()
                    affinity_pred_value_0 = self.to_affinity_pred_value(
                        g[idx_unknown]
                    ).unsqueeze(0)
                    affinity_pred_score_0 = self.to_affinity_pred_score(
                        g[idx_unknown]
                    ).unsqueeze(0)
                    affinity_logits_binary_0 = self.to_affinity_logits_binary(
                        affinity_pred_score_0
                    ).unsqueeze(0)
                    idx_B_to_pred_value[i] = affinity_pred_value_0
                    idx_B_to_pred_score[i] = affinity_pred_score_0
                    idx_B_to_logits_binary[i] = affinity_logits_binary_0
                    continue
                mask_attn_concat.append(mask_attn)
                mask_unknown_concat.append(mask_unknown.squeeze(-1).unsqueeze(0))
                g_input_concat.append(g_concat.unsqueeze(0))

            if len(mask_attn_concat) > 0:
                mask_attn_concat = torch.cat(mask_attn_concat, dim=0)
                mask_unknown_concat = torch.cat(mask_unknown_concat, dim=0)
                g_input_concat = torch.cat(g_input_concat, dim=0)
                g_input_concat = self.norm_pre_transformer(g_input_concat)
                g_new = self.cross_transformer(
                    g_input_concat,
                    g_input_concat,
                    mask=mask_attn_concat,
                )

            if self.predict_affinity_value:
                if len(mask_attn_concat) > 0:
                    affinity_pred_value_all = self.to_affinity_pred_value_group(g_new)
                    affinity_pred_value = affinity_pred_value_all[
                        mask_unknown_concat.bool()
                    ]
                affinity_pred_value_list = []
                count = 0
                for i in range(B):
                    if i in idx_B_to_pred_value:
                        affinity_pred_value_list.append(idx_B_to_pred_value[i])
                    else:
                        affinity_pred_value_list.append(
                            affinity_pred_value[count : count + 1]
                        )
                        count += 1
                affinity_pred_value = torch.cat(affinity_pred_value_list, dim=0)

            if self.predict_affinity_binary:
                if len(mask_attn_concat) > 0:
                    affinity_pred_score_all = self.to_affinity_pred_score_group(g_new)
                    affinity_logits_binary_all = self.to_affinity_logits_binary_group(
                        affinity_pred_score_all
                    )
                    affinity_pred_score = affinity_pred_score_all[
                        mask_unknown_concat.bool()
                    ]
                    affinity_logits_binary = affinity_logits_binary_all[
                        mask_unknown_concat.bool()
                    ]

                affinity_pred_score_list = []
                affinity_pred_binary_list = []
                count = 0
                for i in range(B):
                    if i in idx_B_to_pred_score:
                        affinity_pred_score_list.append(idx_B_to_pred_score[i])
                        affinity_pred_binary_list.append(idx_B_to_logits_binary[i])
                    else:
                        affinity_pred_score_list.append(
                            affinity_pred_score[count : count + 1]
                        )
                        affinity_pred_binary_list.append(
                            affinity_logits_binary[count : count + 1]
                        )
                        count += 1
                affinity_pred_score = torch.cat(affinity_pred_score_list, dim=0)
                affinity_logits_binary = torch.cat(affinity_pred_binary_list, dim=0)

            out_dict = {}
            if self.predict_affinity_value:
                out_dict["affinity_pred_value"] = affinity_pred_value
            if self.predict_affinity_binary:
                out_dict["affinity_pred_score"] = affinity_pred_score
                out_dict["affinity_logits_binary"] = affinity_logits_binary

            return out_dict
