import pickle

import torch
import torch.nn.functional as F
from torch import nn
from torch.nn.functional import pad
import torch.nn.functional as F
from typing import Any, Dict, Optional, List

import foldeverything.model.layers.initialize as init
from foldeverything.data import const
from foldeverything.data.const import chain_type_ids
from foldeverything.model.layers.confidence_utils import (
    GaussianSmearing,
    compute_aggregated_metric,
    compute_aggregated_pde_ablation,
    compute_aggregated_plddt_ablation,
    compute_ptms,
    tm_function,
)
from foldeverything.model.layers.miniformer import MiniformerModule
from foldeverything.model.layers.pairformer import PairformerModule
from foldeverything.model.layers.relative import (
    compute_relative_distribution_perfect_correlation,
)
from foldeverything.model.modules.encoders import RelativePositionEncoder
from foldeverything.model.modules.trunk import (
    InputEmbedder,
    MSAModule,
    ContactConditioning,
)
from foldeverything.model.modules.utils import LinearNoBias


class ConfidenceModule(nn.Module):
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
        bond_type_feature=False,
        confidence_regression=False,
        confidence_args: dict = None,
        compute_pae: bool = False,
        imitate_trunk=False,
        full_embedder_args: dict = None,
        msa_args: dict = None,
        compile_pairformer=False,
        fix_sym_check=False,
        cyclic_pos_enc=False,
        return_latent_feats=False,
        conditioning_cutoff_min=None,
        conditioning_cutoff_max=None,
    ):
        super().__init__()
        self.no_trunk_feats = no_trunk_feats
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
        self.token_level_confidence = token_level_confidence

        self.use_s_diffusion = use_s_diffusion
        if use_s_diffusion:
            self.s_diffusion_norm = nn.LayerNorm(2 * token_s)
            self.s_diffusion_to_s = LinearNoBias(2 * token_s, token_s)
            init.gating_init_(self.s_diffusion_to_s.weight)

        self.s_to_z = LinearNoBias(token_s, token_z)
        self.s_to_z_transpose = LinearNoBias(token_s, token_z)
        init.gating_init_(self.s_to_z.weight)
        init.gating_init_(self.s_to_z_transpose.weight)

        self.add_s_to_z_prod = add_s_to_z_prod
        if add_s_to_z_prod:
            self.s_to_z_prod_in1 = LinearNoBias(token_s, token_z)
            self.s_to_z_prod_in2 = LinearNoBias(token_s, token_z)
            self.s_to_z_prod_out = LinearNoBias(token_z, token_z)
            init.gating_init_(self.s_to_z_prod_out.weight)

        self.imitate_trunk = imitate_trunk
        if self.imitate_trunk:
            self.s_init = nn.Linear(token_s, token_s, bias=False)
            self.z_init_1 = nn.Linear(token_s, token_z, bias=False)
            self.z_init_2 = nn.Linear(token_s, token_z, bias=False)

            # Input embeddings
            self.input_embedder = InputEmbedder(**full_embedder_args)
            self.rel_pos = RelativePositionEncoder(
                token_z, fix_sym_check=fix_sym_check, cyclic_pos_enc=cyclic_pos_enc
            )

            self.token_bonds = nn.Linear(
                1 if maximum_bond_distance == 0 else maximum_bond_distance + 2,
                token_z,
                bias=False,
            )
            self.bond_type_feature = bond_type_feature
            if bond_type_feature:
                self.token_bonds_type = nn.Embedding(len(const.bond_types) + 1, token_z)

            self.contact_conditioning = ContactConditioning(
                token_z=token_z,
                cutoff_min=conditioning_cutoff_min,
                cutoff_max=conditioning_cutoff_max,
            )

            # Normalization layers
            self.s_norm = nn.LayerNorm(token_s)
            self.z_norm = nn.LayerNorm(token_z)

            # Recycling projections
            self.s_recycle = nn.Linear(token_s, token_s, bias=False)
            self.z_recycle = nn.Linear(token_z, token_z, bias=False)
            init.gating_init_(self.s_recycle.weight)
            init.gating_init_(self.z_recycle.weight)

            # Pairwise stack
            self.msa_module = MSAModule(
                token_z=token_z,
                token_s=token_s,
                **msa_args,
            )
            pairformer_class = MiniformerModule if use_miniformer else PairformerModule
            self.pairformer_module = pairformer_class(
                token_s,
                token_z,
                **pairformer_args,
            )
            if compile_pairformer:
                # Big models hit the default cache limit (8)
                self.is_pairformer_compiled = True
                torch._dynamo.config.cache_size_limit = 512
                torch._dynamo.config.accumulated_cache_size_limit = 512
                self.pairformer_module = torch.compile(
                    self.pairformer_module,
                    dynamic=False,
                    fullgraph=False,
                )

            self.final_s_norm = nn.LayerNorm(token_s)
            self.final_z_norm = nn.LayerNorm(token_z)
        else:
            self.s_inputs_norm = nn.LayerNorm(token_s)
            if not self.no_update_s:
                self.s_norm = nn.LayerNorm(token_s)
            self.z_norm = nn.LayerNorm(token_z)

            self.add_s_input_to_s = add_s_input_to_s
            if add_s_input_to_s:
                self.s_input_to_s = LinearNoBias(token_s, token_s)
                init.gating_init_(self.s_input_to_s.weight)

            self.add_z_input_to_z = add_z_input_to_z
            if add_z_input_to_z:
                self.rel_pos = RelativePositionEncoder(
                    token_z, fix_sym_check=fix_sym_check, cyclic_pos_enc=cyclic_pos_enc
                )
                self.token_bonds = nn.Linear(
                    1 if maximum_bond_distance == 0 else maximum_bond_distance + 2,
                    token_z,
                    bias=False,
                )
                self.bond_type_feature = bond_type_feature
                if bond_type_feature:
                    self.token_bonds_type = nn.Embedding(
                        len(const.bond_types) + 1, token_z
                    )

                self.contact_conditioning = ContactConditioning(
                    token_z=token_z,
                    cutoff_min=conditioning_cutoff_min,
                    cutoff_max=conditioning_cutoff_max,
                )

            pairformer_class = MiniformerModule if use_miniformer else PairformerModule
            self.pairformer_stack = pairformer_class(
                token_s,
                token_z,
                **pairformer_args,
            )
        self.return_latent_feats = return_latent_feats

        self.confidence_heads = ConfidenceHeads(
            token_s,
            token_z,
            token_level_confidence=token_level_confidence,
            compute_pae=compute_pae,
            **confidence_args,
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
        if run_sequentially and multiplicity > 1:
            assert z.shape[0] == 1, "Not supported with batch size > 1"
            out_dicts = []
            for sample_idx in range(multiplicity):
                out_dicts.append(  # noqa: PERF401
                    self.forward(
                        s_inputs,
                        s,
                        z,
                        x_pred[sample_idx : sample_idx + 1],
                        feats,
                        pred_distogram_logits,
                        multiplicity=1,
                        s_diffusion=(
                            s_diffusion[sample_idx : sample_idx + 1]
                            if s_diffusion is not None
                            else None
                        ),
                        run_sequentially=False,
                    )
                )

            out_dict = {}
            for key in out_dicts[0]:
                if key != "pair_chains_iptm":
                    out_dict[key] = torch.cat([out[key] for out in out_dicts], dim=0)
                else:
                    pair_chains_iptm = {}
                    for chain_idx1 in out_dicts[0][key]:
                        chains_iptm = {}
                        for chain_idx2 in out_dicts[0][key][chain_idx1]:
                            chains_iptm[chain_idx2] = torch.cat(
                                [out[key][chain_idx1][chain_idx2] for out in out_dicts],
                                dim=0,
                            )
                        pair_chains_iptm[chain_idx1] = chains_iptm
                    out_dict[key] = pair_chains_iptm
            return out_dict

        if self.imitate_trunk:
            s_inputs = self.input_embedder(feats)

            # Initialize the sequence and pairwise embeddings
            s_init = self.s_init(s_inputs)
            z_init = (
                self.z_init_1(s_inputs)[:, :, None]
                + self.z_init_2(s_inputs)[:, None, :]
            )
            relative_position_encoding = self.rel_pos(feats)
            z_init = z_init + relative_position_encoding
            z_init = z_init + self.token_bonds(feats["token_bonds"].float())
            if self.bond_type_feature:
                z_init = z_init + self.token_bonds_type(feats["type_bonds"].long())
            z_init = z_init + self.contact_conditioning(feats)

            # Apply recycling
            s = s_init + self.s_recycle(self.s_norm(s))
            z = z_init + self.z_recycle(self.z_norm(z))

        else:
            s_inputs = self.s_inputs_norm(s_inputs)
            if not self.no_update_s:
                s = self.s_norm(s)

            if self.add_s_input_to_s:
                s = s + self.s_input_to_s(s_inputs)

            z = self.z_norm(z)

            if self.add_z_input_to_z:
                relative_position_encoding = self.rel_pos(feats)
                z = z + relative_position_encoding
                z = z + self.token_bonds(feats["token_bonds"].float())
                if self.bond_type_feature:
                    z = z + self.token_bonds_type(feats["type_bonds"].long())
                z = z + self.contact_conditioning(feats)

        s = s.repeat_interleave(multiplicity, 0)

        if self.use_s_diffusion:
            assert s_diffusion is not None
            s_diffusion = self.s_diffusion_norm(s_diffusion)
            s = s + self.s_diffusion_to_s(s_diffusion)

        z = (
            z
            + self.s_to_z(s_inputs)[:, :, None, :]
            + self.s_to_z_transpose(s_inputs)[:, None, :, :]
        )
        if self.add_s_to_z_prod:
            z = z + self.s_to_z_prod_out(
                self.s_to_z_prod_in1(s_inputs)[:, :, None, :]
                * self.s_to_z_prod_in2(s_inputs)[:, None, :, :]
            )

        z = z.repeat_interleave(multiplicity, 0)
        s_inputs = s_inputs.repeat_interleave(multiplicity, 0)

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
        if self.use_gaussian:
            distogram = self.dist_bin_pairwise_linear(self.gaussian_basis(d))
        else:
            distogram = (d.unsqueeze(-1) > self.boundaries).sum(dim=-1).long()
            distogram = self.dist_bin_pairwise_embed(distogram)
        z = z + distogram

        mask = feats["token_pad_mask"].repeat_interleave(multiplicity, 0)
        pair_mask = mask[:, :, None] * mask[:, None, :]

        if self.imitate_trunk:
            z = z + self.msa_module(z, s_inputs, feats)

            s, z = self.pairformer_module(s, z, mask=mask, pair_mask=pair_mask)

            s, z = self.final_s_norm(s), self.final_z_norm(z)

        else:
            s_t, z_t = self.pairformer_stack(
                s,
                z,
                mask=mask,
                pair_mask=pair_mask,
            )

            # AF3 has residual connections, we remove them
            s = s_t
            z = z_t

        out_dict = {}

        if self.return_latent_feats:
            out_dict["s_conf"] = s
            out_dict["z_conf"] = z

        # confidence heads
        out_dict.update(
            self.confidence_heads(
                s=s,
                z=z,
                x_pred=x_pred,
                d=d,
                feats=feats,
                multiplicity=multiplicity,
                pred_distogram_logits=pred_distogram_logits,
            )
        )
        return out_dict


class ConfidenceHeads(nn.Module):
    def __init__(
        self,
        token_s,
        token_z,
        num_plddt_bins=50,
        num_pde_bins=64,
        num_pae_bins=64,
        token_level_confidence=True,
        confidence_ablation: bool = False,
        compute_pae: bool = False,
        relative_confidence: str = "off",  # "off", "learned", "perfect_correlation",
        use_separate_heads: bool = False,
    ):
        super().__init__()
        self.max_num_atoms_per_token = 23
        self.token_level_confidence = token_level_confidence
        self.confidence_ablation = confidence_ablation
        self.use_separate_heads = use_separate_heads

        self.compute_pae = compute_pae
        if self.compute_pae:
            if self.use_separate_heads:
                self.to_pae_intra_logits = LinearNoBias(token_z, num_pae_bins)
                self.to_pae_inter_logits = LinearNoBias(token_z, num_pae_bins)
            else:
                self.to_pae_logits = LinearNoBias(token_z, num_pae_bins)

        if self.use_separate_heads:
            self.to_pde_intra_logits = LinearNoBias(token_z, num_pde_bins)
            self.to_pde_inter_logits = LinearNoBias(token_z, num_pde_bins)
        else:
            self.to_pde_logits = LinearNoBias(token_z, num_pde_bins)

        self.relative_confidence = relative_confidence
        if relative_confidence == "learned":
            self.to_relative_pde_logits = LinearNoBias(
                2 * token_z, 2 * num_pde_bins - 1
            )
            self.to_relative_plddt_logits = LinearNoBias(
                2 * token_s, 2 * num_plddt_bins - 1
            )
            assert token_level_confidence, (
                "Fix the relative plddt logits for the atom level confidence"
            )
            if self.compute_pae:
                self.to_relative_pae_logits = LinearNoBias(
                    2 * token_z, 2 * num_pae_bins - 1
                )

        if self.token_level_confidence:
            self.to_plddt_logits = LinearNoBias(token_s, num_plddt_bins)
            self.to_resolved_logits = LinearNoBias(token_s, 2)
        else:
            self.to_plddt_logits = LinearNoBias(
                token_s, num_plddt_bins * self.max_num_atoms_per_token
            )
            self.to_resolved_logits = LinearNoBias(
                token_s, 2 * self.max_num_atoms_per_token
            )

    def forward(
        self,
        s,  # Float['b n ts']
        z,  # Float['b n n tz']
        x_pred,  # Float['bm m 3']
        d,
        feats,
        pred_distogram_logits,
        multiplicity=1,
    ):
        if self.use_separate_heads:
            asym_id_token = feats["asym_id"]
            is_same_chain = asym_id_token.unsqueeze(-1) == asym_id_token.unsqueeze(-2)
            is_different_chain = ~is_same_chain

        if self.compute_pae:
            if self.use_separate_heads:
                pae_intra_logits = self.to_pae_intra_logits(z)
                pae_intra_logits = pae_intra_logits * is_same_chain.float().unsqueeze(
                    -1
                )

                pae_inter_logits = self.to_pae_inter_logits(z)
                pae_inter_logits = (
                    pae_inter_logits * is_different_chain.float().unsqueeze(-1)
                )

                pae_logits = pae_inter_logits + pae_intra_logits
            else:
                pae_logits = self.to_pae_logits(z)

        if self.use_separate_heads:
            pde_intra_logits = self.to_pde_intra_logits(z + z.transpose(1, 2))
            pde_intra_logits = pde_intra_logits * is_same_chain.float().unsqueeze(-1)

            pde_inter_logits = self.to_pde_inter_logits(z + z.transpose(1, 2))
            pde_inter_logits = pde_inter_logits * is_different_chain.float().unsqueeze(
                -1
            )

            pde_logits = pde_inter_logits + pde_intra_logits
        else:
            pde_logits = self.to_pde_logits(z + z.transpose(1, 2))
        resolved_logits = self.to_resolved_logits(s)
        plddt_logits = self.to_plddt_logits(s)

        if self.relative_confidence == "learned":
            BM, N, N, Dz = z.shape
            B = BM // multiplicity
            _, _, Ds = s.shape

            s_pair = torch.cat(
                [
                    s.view(B, multiplicity, 1, N, Ds).repeat(1, 1, multiplicity, 1, 1),
                    s.view(B, 1, multiplicity, N, Ds).repeat(1, multiplicity, 1, 1, 1),
                ],
                dim=-1,
            )
            relative_plddt_logits = self.to_relative_plddt_logits(s_pair)

            z_pair = torch.cat(
                [
                    z.view(B, multiplicity, 1, N, N, Dz).repeat(
                        1, 1, multiplicity, 1, 1, 1
                    ),
                    z.view(B, 1, multiplicity, N, N, Dz).repeat(
                        1, multiplicity, 1, 1, 1, 1
                    ),
                ],
                dim=-1,
            )
            relative_pde_logits = self.to_relative_pde_logits(z_pair)
            if self.compute_pae:
                relative_pae_logits = self.to_relative_pae_logits(z_pair)

        elif self.relative_confidence == "perfect_correlation":
            BM, N, N, Dz = z.shape
            B = BM // multiplicity

            plddt_probs = F.softmax(plddt_logits, dim=-1)
            plddt_probs_1 = plddt_probs.view(B, multiplicity, 1, N, -1).repeat(
                1, 1, multiplicity, 1, 1
            )
            plddt_probs_2 = plddt_probs.view(B, 1, multiplicity, N, -1).repeat(
                1, multiplicity, 1, 1, 1
            )
            relative_plddt_probs = compute_relative_distribution_perfect_correlation(
                plddt_probs_1, plddt_probs_2
            )
            relative_plddt_logits = torch.log(relative_plddt_probs.clamp(min=1e-6))

            pde_probs = F.softmax(pde_logits, dim=-1)
            pde_probs_1 = pde_probs.view(B, multiplicity, 1, N, N, -1).repeat(
                1, 1, multiplicity, 1, 1, 1
            )
            pde_probs_2 = pde_probs.view(B, 1, multiplicity, N, N, -1).repeat(
                1, multiplicity, 1, 1, 1, 1
            )
            relative_pde_probs = compute_relative_distribution_perfect_correlation(
                pde_probs_1, pde_probs_2
            )
            relative_pde_logits = torch.log(relative_pde_probs.clamp(min=1e-6))

            if self.compute_pae:
                pae_probs = F.softmax(pae_logits, dim=-1)
                pae_probs_1 = pae_probs.view(B, multiplicity, 1, N, N, -1).repeat(
                    1, 1, multiplicity, 1, 1, 1
                )
                pae_probs_2 = pae_probs.view(B, 1, multiplicity, N, N, -1).repeat(
                    1, multiplicity, 1, 1, 1, 1
                )
                relative_pae_probs = compute_relative_distribution_perfect_correlation(
                    pae_probs_1, pae_probs_2
                )
                relative_pae_logits = torch.log(relative_pae_probs.clamp(min=1e-6))

        ligand_weight = 20
        non_interface_weight = 1
        interface_weight = 10

        token_type = feats["mol_type"]
        token_type = token_type.repeat_interleave(multiplicity, 0)
        is_ligand_token = (token_type == const.chain_type_ids["NONPOLYMER"]).float()
        is_protein_token = (token_type == const.chain_type_ids["PROTEIN"]).float()

        if self.token_level_confidence:
            plddt = compute_aggregated_metric(plddt_logits)
            token_pad_mask = feats["token_pad_mask"].repeat_interleave(multiplicity, 0)
            complex_plddt = (plddt * token_pad_mask).sum(dim=-1) / token_pad_mask.sum(
                dim=-1
            )

            is_contact = (d < 8).float()
            is_different_chain = (
                feats["asym_id"].unsqueeze(-1) != feats["asym_id"].unsqueeze(-2)
            ).float()
            is_different_chain = is_different_chain.repeat_interleave(multiplicity, 0)
            token_interface_mask = torch.max(
                is_contact * is_different_chain * (1 - is_ligand_token).unsqueeze(-1),
                dim=-1,
            ).values
            token_non_interface_mask = (1 - token_interface_mask) * (
                1 - is_ligand_token
            )
            iplddt_weight = (
                is_ligand_token * ligand_weight
                + token_interface_mask * interface_weight
                + token_non_interface_mask * non_interface_weight
            )
            complex_iplddt = (plddt * token_pad_mask * iplddt_weight).sum(
                dim=-1
            ) / torch.sum(token_pad_mask * iplddt_weight, dim=-1)

            # Compute plddt ablation
            if self.confidence_ablation:
                ablation_plddt = compute_aggregated_plddt_ablation(plddt_logits)
                aggregated_ablation_plddt = []
                for mask in [
                    is_ligand_token,
                    token_interface_mask,
                    token_non_interface_mask,
                ]:
                    aggregated_ablation_plddt.append(
                        (
                            ablation_plddt
                            * token_pad_mask.unsqueeze(-1)
                            * mask.unsqueeze(-1)
                        ).sum(dim=1)
                        / (torch.sum(token_pad_mask * mask, dim=1).unsqueeze(-1) + 1e-7)
                    )
                aggregated_ablation_plddt = torch.cat(aggregated_ablation_plddt, dim=-1)
        else:
            # token to atom conversion for resolved logits
            B, N, _ = resolved_logits.shape
            resolved_logits = resolved_logits.reshape(
                B, N, self.max_num_atoms_per_token, 2
            )

            arange_max_num_atoms = (
                torch.arange(self.max_num_atoms_per_token)
                .reshape(1, 1, -1)
                .to(resolved_logits.device)
            )
            max_num_atoms_mask = (
                feats["atom_to_token"].sum(1).unsqueeze(-1) > arange_max_num_atoms
            )
            resolved_logits = resolved_logits[:, max_num_atoms_mask.squeeze(0)]
            resolved_logits = pad(
                resolved_logits,
                (
                    0,
                    0,
                    0,
                    int(
                        feats["atom_pad_mask"].shape[1]
                        - feats["atom_pad_mask"].sum().item()
                    ),
                ),
                value=0,
            )
            plddt_logits = plddt_logits.reshape(B, N, self.max_num_atoms_per_token, -1)
            plddt_logits = plddt_logits[:, max_num_atoms_mask.squeeze(0)]
            plddt_logits = pad(
                plddt_logits,
                (
                    0,
                    0,
                    0,
                    int(
                        feats["atom_pad_mask"].shape[1]
                        - feats["atom_pad_mask"].sum().item()
                    ),
                ),
                value=0,
            )
            atom_pad_mask = feats["atom_pad_mask"].repeat_interleave(multiplicity, 0)
            plddt = compute_aggregated_metric(plddt_logits)

            complex_plddt = (plddt * atom_pad_mask).sum(dim=-1) / atom_pad_mask.sum(
                dim=-1
            )
            token_type = feats["mol_type"].float()
            atom_to_token = feats["atom_to_token"].float()
            chain_id_token = feats["asym_id"].float()
            atom_type = torch.bmm(atom_to_token, token_type.unsqueeze(-1)).squeeze(-1)
            is_ligand_atom = (atom_type == const.chain_type_ids["NONPOLYMER"]).float()
            d_atom = torch.cdist(x_pred, x_pred)
            is_contact = (d_atom < 8).float()
            chain_id_atom = torch.bmm(
                atom_to_token, chain_id_token.unsqueeze(-1)
            ).squeeze(-1)
            is_different_chain = (
                chain_id_atom.unsqueeze(-1) != chain_id_atom.unsqueeze(-2)
            ).float()

            atom_interface_mask = torch.max(
                is_contact * is_different_chain * (1 - is_ligand_atom).unsqueeze(-1),
                dim=-1,
            ).values
            atom_non_interface_mask = (1 - atom_interface_mask) * (1 - is_ligand_atom)
            iplddt_weight = (
                is_ligand_atom * ligand_weight
                + atom_interface_mask * interface_weight
                + atom_non_interface_mask * non_interface_weight
            )

            complex_iplddt = (plddt * feats["atom_pad_mask"] * iplddt_weight).sum(
                dim=-1
            ) / torch.sum(feats["atom_pad_mask"] * iplddt_weight, dim=-1)

        # Compute the gPDE and giPDE
        pde = compute_aggregated_metric(pde_logits, end=32)
        pae = compute_aggregated_metric(pae_logits, end=32)
        pred_distogram_prob = nn.functional.softmax(
            pred_distogram_logits, dim=-1
        ).repeat_interleave(multiplicity, 0)
        contacts = torch.zeros((1, 1, 1, 64), dtype=pred_distogram_prob.dtype).to(
            pred_distogram_prob.device
        )
        contacts[:, :, :, :20] = 1.0
        prob_contact = (pred_distogram_prob * contacts).sum(-1)
        token_pad_mask = feats["token_pad_mask"].repeat_interleave(multiplicity, 0)
        token_pad_pair_mask = (
            token_pad_mask.unsqueeze(-1)
            * token_pad_mask.unsqueeze(-2)
            * (
                1
                - torch.eye(
                    token_pad_mask.shape[1], device=token_pad_mask.device
                ).unsqueeze(0)
            )
        )
        # added code
        asym_id = feats["asym_id"].repeat_interleave(multiplicity, 0)
        selected_ligand_mask = is_ligand_token * (asym_id == 1).float()
        protein_pair_mask = token_pad_pair_mask * (
            is_protein_token.unsqueeze(-1) * is_protein_token.unsqueeze(-2)
        )
        protein_pair_mask_weighted = protein_pair_mask * prob_contact
        protein_pae_value_weighted = (pae * protein_pair_mask_weighted).sum(
            dim=(1, 2)
        ) / (protein_pair_mask_weighted.sum(dim=(1, 2)) + 1e-5)
        protein_pae_value_unweighted = (pae * protein_pair_mask).sum(dim=(1, 2)) / (
            protein_pair_mask.sum(dim=(1, 2)) + 1e-5
        )

        ligand_pair_mask = token_pad_pair_mask * (
            selected_ligand_mask.unsqueeze(-1) * selected_ligand_mask.unsqueeze(-2)
        )

        ligand_pair_mask_weighted = ligand_pair_mask * prob_contact
        ligand_pae_value_weighted = (pae * ligand_pair_mask_weighted).sum(
            dim=(1, 2)
        ) / (ligand_pair_mask_weighted.sum(dim=(1, 2)) + 1e-5)
        ligand_pae_value_unweighted = (pae * ligand_pair_mask).sum(dim=(1, 2)) / (
            ligand_pair_mask.sum(dim=(1, 2)) + 1e-5
        )

        interface_protein_mask = torch.max(
            (d < 8).float()
            * is_protein_token.unsqueeze(-1)
            * selected_ligand_mask.unsqueeze(-2),
            dim=-1,
        ).values
        protein_ligand_interface_pair_mask = (
            token_pad_pair_mask
            * interface_protein_mask.unsqueeze(-1)
            * selected_ligand_mask.unsqueeze(-2)
            * (d < 8).float()
        )
        protein_ligand_interface_pair_mask_weighted = (
            protein_ligand_interface_pair_mask * prob_contact
        )
        interface_pae_value_weighted = (
            pae * protein_ligand_interface_pair_mask_weighted
        ).sum(dim=(1, 2)) / (
            protein_ligand_interface_pair_mask_weighted.sum(dim=(1, 2)) + 1e-5
        )
        interface_pae_value_unweighted = (pae * protein_ligand_interface_pair_mask).sum(
            dim=(1, 2)
        ) / (protein_ligand_interface_pair_mask.sum(dim=(1, 2)) + 1e-5)
        # finish
        token_pair_mask = token_pad_pair_mask * prob_contact
        complex_pde = (pde * token_pair_mask).sum(dim=(1, 2)) / token_pair_mask.sum(
            dim=(1, 2)
        )
        asym_id = feats["asym_id"].repeat_interleave(multiplicity, 0)
        token_interface_pair_mask = token_pair_mask * (
            asym_id.unsqueeze(-1) != asym_id.unsqueeze(-2)
        )
        complex_ipde = (pde * token_interface_pair_mask).sum(dim=(1, 2)) / (
            token_interface_pair_mask.sum(dim=(1, 2)) + 1e-5
        )

        # Compute pde ablation
        if self.confidence_ablation:
            ablation_pde = compute_aggregated_pde_ablation(pde_logits)
            aggregated_ablation_pde = []
            ligand_ligand_mask = (
                token_pad_pair_mask
                * is_ligand_token.unsqueeze(-1)
                * is_ligand_token.unsqueeze(-2)
            )
            protein_protein_mask = (
                token_pad_pair_mask
                * (1 - is_ligand_token).unsqueeze(-1)
                * (1 - is_ligand_token).unsqueeze(-2)
            )
            ligand_protein_mask = token_pad_pair_mask * (
                is_ligand_token.unsqueeze(-1) * (1 - is_ligand_token).unsqueeze(-2)
                + is_ligand_token.unsqueeze(-2) * (1 - is_ligand_token).unsqueeze(-1)
            )

            for mask in [protein_protein_mask, ligand_protein_mask, ligand_ligand_mask]:
                aggregated_ablation_pde.append(
                    (ablation_pde * mask.unsqueeze(-1)).sum(dim=(1, 2))
                    / (torch.sum(mask, dim=(1, 2)).unsqueeze(-1) + 1e-7)
                )
            aggregated_ablation_pde = torch.cat(aggregated_ablation_pde, dim=-1)

        # Compute design metric PDE
        is_design_token = feats["design_mask"].float()
        is_target_token = 1 - feats["design_mask"].float()
        target_design_inter_mask = token_pad_pair_mask * (
            is_design_token[:, :, None] * is_target_token[:, None, :]
            + is_target_token[:, :, None] * is_design_token[:, None, :]
        )
        interaction_pae = (pae * target_design_inter_mask).sum(dim=(1, 2)) / (
            target_design_inter_mask.sum(dim=(1, 2)) + 1e-5
        )
        min_interaction_pae = torch.min(pae + (1 - target_design_inter_mask) * 100000)[
            None
        ]

        out_dict = dict(
            pde_logits=pde_logits,
            plddt_logits=plddt_logits,
            resolved_logits=resolved_logits,
            pde=pde,
            plddt=plddt,
            complex_plddt=complex_plddt,
            complex_iplddt=complex_iplddt,
            complex_pde=complex_pde,
            complex_ipde=complex_ipde,
            interaction_pae=interaction_pae,
            min_interaction_pae=min_interaction_pae,
        )

        # weighted
        out_dict["protein_pae_value_weighted"] = protein_pae_value_weighted
        out_dict["ligand_pae_value_weighted"] = ligand_pae_value_weighted
        out_dict["interface_pae_value_weighted"] = interface_pae_value_weighted
        # unweighted
        out_dict["protein_pae_value_unweighted"] = protein_pae_value_unweighted
        out_dict["ligand_pae_value_unweighted"] = ligand_pae_value_unweighted
        out_dict["interface_pae_value_unweighted"] = interface_pae_value_unweighted

        if self.compute_pae:
            out_dict["pae_logits"] = pae_logits
            out_dict["pae"] = compute_aggregated_metric(pae_logits, end=32)

            try:
                (
                    ptm,
                    iptm,
                    ligand_iptm,
                    protein_iptm,
                    pair_chains_iptm,
                    design_iptm,
                    target_ptm,
                    design_ptm,
                ) = compute_ptms(pae_logits, x_pred, feats, multiplicity)
                out_dict["ptm"] = ptm
                out_dict["iptm"] = iptm
                out_dict["ligand_iptm"] = ligand_iptm
                out_dict["protein_iptm"] = protein_iptm
                out_dict["pair_chains_iptm"] = pair_chains_iptm
                out_dict["design_iptm"] = design_iptm
                out_dict["target_ptm"] = target_ptm
                out_dict["design_ptm"] = design_ptm
            except Exception as e:
                print(f"Error in compute_ptms: {e}")
                out_dict["ptm"] = torch.zeros_like(complex_plddt)
                out_dict["iptm"] = torch.zeros_like(complex_plddt)
                out_dict["ligand_iptm"] = torch.zeros_like(complex_plddt)
                out_dict["protein_iptm"] = torch.zeros_like(complex_plddt)
                out_dict["pair_chains_iptm"] = torch.zeros_like(complex_plddt)
                out_dict["design_iptm"] = torch.zeros_like(complex_plddt)
                out_dict["target_ptm"] = torch.zeros_like(complex_plddt)
                out_dict["design_ptm"] = torch.zeros_like(complex_plddt)

        if (
            self.relative_confidence == "learned"
            or self.relative_confidence == "perfect_correlation"
        ):
            out_dict["relative_pde_logits"] = relative_pde_logits
            out_dict["relative_plddt_logits"] = relative_plddt_logits
            if self.compute_pae:
                out_dict["relative_pae_logits"] = relative_pae_logits

        if self.confidence_ablation:
            out_dict["ablation_confidence"] = torch.cat(
                [aggregated_ablation_plddt, aggregated_ablation_pde], dim=-1
            )
        return out_dict
