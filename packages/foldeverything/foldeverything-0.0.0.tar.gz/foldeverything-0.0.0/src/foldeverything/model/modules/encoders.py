# started from code from https://github.com/lucidrains/alphafold3-pytorch, MIT License, Copyright (c) 2024 Phil Wang
from functools import partial
from math import pi
from typing import Optional

import torch
from einops import rearrange
from torch import nn
from torch.nn import Linear, Module, ModuleList
from torch.nn.functional import one_hot

from foldeverything.data import const
import foldeverything.model.layers.initialize as init
from foldeverything.model.layers.transition import Transition
from foldeverything.model.modules.transformers import (
    AtomTransformer,
    AllAtomTransformer,
    AnchorTransformer,
)
from foldeverything.model.modules.utils import (
    GaussianRandom3DEncodings,
    GaussianSmearing,
    LinearNoBias,
)


class FourierEmbedding(Module):
    """Algorithm 22."""

    def __init__(self, dim):
        super().__init__()
        self.proj = nn.Module()
        self.proj.register_buffer("weight", torch.randn(dim, 1))
        self.proj.register_buffer("bias", torch.randn(dim))

    def forward(
        self,
        times,  # Float[' b'],
    ):  # -> Float['b d']:
        times = rearrange(times, "b -> b 1")
        rand_proj = torch.addmm(self.proj.bias, times, self.proj.weight.t())
        return torch.cos(2 * pi * rand_proj)


class RelativePositionEncoder(Module):
    """Algorithm 3."""

    def __init__(
        self, token_z, r_max=32, s_max=2, fix_sym_check=False, cyclic_pos_enc=False
    ):
        super().__init__()
        self.r_max = r_max
        self.s_max = s_max
        self.linear_layer = LinearNoBias(4 * (r_max + 1) + 2 * (s_max + 1) + 1, token_z)
        self.fix_sym_check = fix_sym_check
        self.cyclic_pos_enc = cyclic_pos_enc

    def forward(self, feats):
        b_same_chain = torch.eq(
            feats["feature_asym_id"][:, :, None], feats["feature_asym_id"][:, None, :]
        )
        b_same_residue = torch.eq(
            feats["feature_residue_index"][:, :, None],
            feats["feature_residue_index"][:, None, :],
        )
        b_same_entity = torch.eq(
            feats["entity_id"][:, :, None], feats["entity_id"][:, None, :]
        )
        pair_is_anchor = (
            feats["is_anchor"][:, :, None] & feats["is_anchor"][:, None, :]
        ).bool()

        d_residue = (
            feats["feature_residue_index"][:, :, None]
            - feats["feature_residue_index"][:, None, :]
        )

        if self.cyclic_pos_enc and torch.any(feats["cyclic"] > 0):
            period = torch.where(
                feats["cyclic"] > 0,
                feats["cyclic"],
                torch.zeros_like(feats["cyclic"]) + 10000,
            ).unsqueeze(1)
            d_residue = (d_residue - period * torch.round(d_residue / period)).long()

        d_residue = torch.clip(
            d_residue + self.r_max,
            0,
            2 * self.r_max,
        )
        d_residue = torch.where(
            b_same_chain & ~pair_is_anchor,
            d_residue,
            torch.zeros_like(d_residue) + 2 * self.r_max + 1,
        )

        a_rel_pos = one_hot(d_residue, 2 * self.r_max + 2)

        d_token = torch.clip(
            feats["token_index"][:, :, None]
            - feats["token_index"][:, None, :]
            + self.r_max,
            0,
            2 * self.r_max,
        )
        d_token = torch.where(
            b_same_chain & b_same_residue,
            d_token,
            torch.zeros_like(d_token) + 2 * self.r_max + 1,
        )
        a_rel_token = one_hot(d_token, 2 * self.r_max + 2)

        d_chain = torch.clip(
            feats["sym_id"][:, :, None] - feats["sym_id"][:, None, :] + self.s_max,
            0,
            2 * self.s_max,
        )
        d_chain = torch.where(
            (~b_same_entity) if self.fix_sym_check else b_same_chain,
            torch.zeros_like(d_chain) + 2 * self.s_max + 1,
            d_chain,
        )
        # Note: added  | (~b_same_entity) based on observation of ProteinX manuscript
        a_rel_chain = one_hot(d_chain, 2 * self.s_max + 2)

        p = self.linear_layer(
            torch.cat(
                [
                    a_rel_pos.float(),
                    a_rel_token.float(),
                    b_same_entity.unsqueeze(-1).float(),
                    a_rel_chain.float(),
                ],
                dim=-1,
            )
        )
        return p


class SingleConditioning(Module):
    """Algorithm 21."""

    def __init__(
        self,
        sigma_data: float,
        tfmr_s: int = 768,
        token_s: int = 384,
        dim_fourier: int = 256,
        num_transitions: int = 2,
        transition_expansion_factor: int = 2,
        eps: float = 1e-20,
        disable_times: bool = False,
    ) -> None:
        super().__init__()
        self.eps = eps
        self.sigma_data = sigma_data
        self.disable_times = disable_times

        self.norm_single = nn.LayerNorm(token_s * 2)

        if tfmr_s != token_s * 2:
            self.token_s_to_tfmr_s = nn.Linear(token_s * 2, tfmr_s)
        else:
            self.token_s_to_tfmr_s = None

        self.single_embed = nn.Linear(tfmr_s, tfmr_s)
        if not self.disable_times:
            self.fourier_embed = FourierEmbedding(dim_fourier)
            self.norm_fourier = nn.LayerNorm(dim_fourier)
            self.fourier_to_single = LinearNoBias(dim_fourier, tfmr_s)

        transitions = ModuleList([])
        for _ in range(num_transitions):
            transition = Transition(
                dim=tfmr_s, hidden=transition_expansion_factor * tfmr_s
            )
            transitions.append(transition)

        self.transitions = transitions

    def forward(
        self,
        times,  # Float[' b'],
        s_trunk,  # Float['b n ts'],
        s_inputs,  # Float['b n ts'],
    ):  # -> Float['b n 2ts']:
        s = torch.cat((s_trunk, s_inputs), dim=-1)
        s = self.norm_single(s)

        if self.token_s_to_tfmr_s is not None:
            s = self.token_s_to_tfmr_s(s)

        s = self.single_embed(s)
        if not self.disable_times:
            fourier_embed = self.fourier_embed(
                times
            )  # note: sigma rescaling done in diffusion module
            normed_fourier = self.norm_fourier(fourier_embed)
            fourier_to_single = self.fourier_to_single(normed_fourier)

            s = rearrange(fourier_to_single, "b d -> b 1 d") + s

        for transition in self.transitions:
            s = transition(s) + s

        return s, normed_fourier if not self.disable_times else None


class PairwiseConditioning(Module):
    """Algorithm 21."""

    def __init__(
        self,
        token_z,
        dim_token_rel_pos_feats,
        num_transitions=2,
        transition_expansion_factor=2,
    ):
        super().__init__()

        self.dim_pairwise_init_proj = nn.Sequential(
            nn.LayerNorm(token_z + dim_token_rel_pos_feats),
            LinearNoBias(token_z + dim_token_rel_pos_feats, token_z),
        )

        transitions = ModuleList([])
        for _ in range(num_transitions):
            transition = Transition(
                dim=token_z, hidden=transition_expansion_factor * token_z
            )
            transitions.append(transition)

        self.transitions = transitions

    def forward(
        self,
        z_trunk,  # Float['b n n tz'],
        token_rel_pos_feats,  # Float['b n n 3'],
    ):  # -> Float['b n n tz']:
        z = torch.cat((z_trunk, token_rel_pos_feats), dim=-1)
        z = self.dim_pairwise_init_proj(z)

        for transition in self.transitions:
            z = transition(z) + z

        return z


class CoordinateConditioning(Module):
    def __init__(
        self,
        sigma_data: float,
        atom_s,
        token_s,
        num_heads,
        tfmr_s: int = 768,
        dim_fourier: int = 256,
        atom_feature_dim: int = 132,
        structure_prediction=True,
        disable_times: bool = False,
    ):
        super().__init__()
        self.sigma_data = sigma_data
        self.single_embed = LinearNoBias(token_s * 2, tfmr_s)

        self.disable_times = disable_times
        if not self.disable_times:
            self.fourier_embed = FourierEmbedding(dim_fourier)
            self.norm_fourier = nn.LayerNorm(dim_fourier)
            self.fourier_to_single = LinearNoBias(dim_fourier, tfmr_s)

        self.embed_atom_features = Linear(atom_feature_dim, num_heads)
        self.embed_atompair_ref_coord = LinearNoBias(3, num_heads)
        self.embed_atompair_ref_dist = LinearNoBias(1, num_heads)
        self.embed_atompair_mask = LinearNoBias(1, num_heads)

        self.structure_prediction = structure_prediction
        if structure_prediction:
            self.s_to_c_trans = nn.Sequential(
                nn.LayerNorm(tfmr_s), LinearNoBias(tfmr_s, 1)
            )
            init.final_init_(self.s_to_c_trans[1].weight)

    def forward(self, s_trunk, s_inputs, times, feats, atom_coords_noisy):
        s = torch.cat((s_trunk, s_inputs), dim=-1)
        s = self.single_embed(s)
        if not self.disable_times:
            fourier_embed = self.fourier_embed(
                times
            )  # note: sigma rescaling done in diffusion module
            normed_fourier = self.norm_fourier(fourier_embed)
            fourier_to_single = self.fourier_to_single(normed_fourier)
            s = rearrange(fourier_to_single, "b d -> b 1 d") + s

        with torch.autocast("cuda", enabled=False):
            atom_mask = feats["atom_pad_mask"].bool()
            atom_ref_pos = feats["ref_pos"]
            atom_uid = feats["ref_space_uid"]

            atom_feats = [
                atom_ref_pos,
                feats["ref_charge"].unsqueeze(-1),
                feats["ref_element"],
            ]

            atom_feats = torch.cat(atom_feats, dim=-1)
            c = self.embed_atom_features(atom_feats)
            B, N = atom_coords_noisy.shape[:2]

            s_to_c = self.s_to_c_trans(s.float())
            s_to_c = torch.bmm(
                feats["atom_to_token"].float().repeat_interleave(B, 0), s_to_c
            )
            c = c + s_to_c.to(c)

            atom_mask = atom_mask.repeat_interleave(B, 0)
            atom_uid = atom_uid.repeat_interleave(B, 0)

            d = atom_coords_noisy.view(B, N, 1, 3) - atom_coords_noisy.view(B, 1, N, 3)
            d_norm = torch.sum(d * d, dim=-1, keepdim=True)
            d_norm = 1 / (1 + d_norm)
            atom_mask_queries = atom_mask.view(B, N, 1)
            atom_mask_keys = atom_mask.view(B, 1, N)
            atom_uid_queries = atom_uid.view(B, N, 1)
            atom_uid_keys = atom_uid.view(B, 1, N)
            v = (
                (
                    atom_mask_queries
                    & atom_mask_keys
                    & (atom_uid_queries == atom_uid_keys)
                )
                .float()
                .unsqueeze(-1)
            )

            p = (
                self.embed_atompair_ref_coord(d) * v
                + self.embed_atompair_ref_dist(d_norm) * v
                + self.embed_atompair_mask(v) * v
            )
            p = p + c.view(B, 1, N, -1) + c.view(B, N, 1, -1)

            return p.sum(dim=0, keepdim=True)


class DistanceTokenBias(Module):
    def __init__(
        self,
        dim_fourier: int,
        distance_gaussian_dim: int,
        token_z: int,
        out_dim: int,
    ):
        super().__init__()
        self.fourier_downprojection = LinearNoBias(dim_fourier, 16)
        self.distance_gaussian_smearing = GaussianSmearing(
            start=0.0, stop=2.0, num_gaussians=distance_gaussian_dim
        )
        input_dim = 16 + distance_gaussian_dim + 2 + token_z
        self.distance_token_bias_trans = Transition(
            dim=input_dim, hidden=token_z, out_dim=out_dim
        )

    def forward(
        self,
        normed_fourier,
        r_noisy,
        relative_position_encoding,
        feats,
        multiplicity,
    ):
        B, N, _, _ = relative_position_encoding.shape
        fourier_downprojected = self.fourier_downprojection(normed_fourier).reshape(
            B * multiplicity, 1, 1, -1
        )

        token_to_rep_atom = feats["token_to_rep_atom"].repeat_interleave(
            multiplicity, 0
        )

        r = r_noisy

        r_repr = torch.bmm(token_to_rep_atom.float(), r)
        d = (r_repr.unsqueeze(-2) - r_repr.unsqueeze(-3)).norm(dim=-1).unsqueeze(-1)
        distance_gaussian = self.distance_gaussian_smearing(d)

        relative_position_encoding = relative_position_encoding.repeat_interleave(
            multiplicity, 0
        )

        distance_token_bias_input = torch.cat(
            (
                fourier_downprojected.repeat(1, N, N, 1),
                distance_gaussian,
                d,
                torch.zeros((B * multiplicity, N, N, 1)).to(d),
                relative_position_encoding,
            ),
            dim=-1,
        )
        distance_token_bias = self.distance_token_bias_trans(
            distance_token_bias_input
        ).permute(0, 3, 1, 2)
        return distance_token_bias


class DistanceTokenEncoder(Module):
    def __init__(
        self,
        distance_gaussian_dim: int,
        token_z: int,
        out_dim: int,
    ):
        super().__init__()
        self.distance_gaussian_smearing = GaussianSmearing(
            start=0.0, stop=2.0, num_gaussians=distance_gaussian_dim
        )
        input_dim = distance_gaussian_dim + 1 + token_z
        self.distance_token_bias_trans = Transition(
            dim=input_dim, hidden=token_z, out_dim=out_dim
        )

    def forward(
        self,
        relative_position_encoding,
        feats,
    ):
        B, N, _, _ = relative_position_encoding.shape

        token_to_bb4_atoms = feats["token_to_bb4_atoms"]
        r = feats["coords"]

        r_repr = torch.bmm(
            token_to_bb4_atoms.float().view(B, N * 4, -1), r.view(B, -1, 3)
        )
        r_repr = r_repr.reshape(B, N, 4, 3).permute(0, 2, 1, 3)
        d = (r_repr.unsqueeze(-2) - r_repr.unsqueeze(-3)).norm(dim=-1).unsqueeze(-1)
        distance_gaussian = self.distance_gaussian_smearing(d)

        relative_position_encoding = relative_position_encoding.view(
            B, 1, N, N, -1
        ).expand(-1, 4, -1, -1, -1)
        distance_token_bias_input = torch.cat(
            (
                distance_gaussian,
                d,
                relative_position_encoding,
            ),
            dim=-1,
        )
        distance_token_bias = (
            self.distance_token_bias_trans(distance_token_bias_input)
            .permute(0, 2, 3, 4, 1)
            .reshape(B, N, N, -1)
        )
        return distance_token_bias


def get_indexing_matrix(K, W, H, device):
    assert W % 2 == 0
    assert H % (W // 2) == 0

    h = H // (W // 2)
    assert h % 2 == 0

    arange = torch.arange(2 * K, device=device)
    index = ((arange.unsqueeze(0) - arange.unsqueeze(1)) + h // 2).clamp(
        min=0, max=h + 1
    )
    index = index.view(K, 2, 2 * K)[:, 0, :]
    onehot = one_hot(index, num_classes=h + 2)[..., 1:-1].transpose(1, 0)
    return onehot.reshape(2 * K, h * K).float()


def single_to_keys(single, indexing_matrix, W, H):
    B, N, D = single.shape
    K = N // W
    single = single.view(B, 2 * K, W // 2, D)
    return torch.einsum("b j i d, j k -> b k i d", single, indexing_matrix).reshape(
        B, K, H, D
    )  # j = 2K, i = W//2, k = h * K


class AtomEncoder(Module):
    def __init__(
        self,
        atom_s,
        atom_z,
        token_s,
        token_z,
        atoms_per_window_queries,
        atoms_per_window_keys,
        atom_feature_dim,
        structure_prediction=True,
        use_no_atom_char=False,
        use_atom_backbone_feat=False,
        use_residue_feats_atoms=False,
        atom_trans_bias=False,
    ):
        super().__init__()

        self.embed_atom_features = Linear(atom_feature_dim, atom_s)
        self.embed_atompair_ref_pos = LinearNoBias(3, atom_z)
        self.embed_atompair_ref_dist = LinearNoBias(1, atom_z)
        self.embed_atompair_mask = LinearNoBias(1, atom_z)
        self.atoms_per_window_queries = atoms_per_window_queries
        self.atoms_per_window_keys = atoms_per_window_keys
        self.use_no_atom_char = use_no_atom_char
        self.use_atom_backbone_feat = use_atom_backbone_feat
        self.use_residue_feats_atoms = use_residue_feats_atoms

        self.structure_prediction = structure_prediction
        if structure_prediction:
            self.s_to_c_trans = nn.Sequential(
                nn.LayerNorm(token_s), LinearNoBias(token_s, atom_s)
            )
            init.final_init_(self.s_to_c_trans[1].weight)

            self.z_to_p_trans = nn.Sequential(
                nn.LayerNorm(token_z), LinearNoBias(token_z, atom_z)
            )
            init.final_init_(self.z_to_p_trans[1].weight)

        self.c_to_p_trans_k = nn.Sequential(
            nn.ReLU(),
            LinearNoBias(atom_s, atom_z),
        )
        init.final_init_(self.c_to_p_trans_k[1].weight)

        self.c_to_p_trans_q = nn.Sequential(
            nn.ReLU(),
            LinearNoBias(atom_s, atom_z),
        )
        init.final_init_(self.c_to_p_trans_q[1].weight)

        self.p_mlp = nn.Sequential(
            nn.ReLU(),
            LinearNoBias(atom_z, atom_z),
            nn.ReLU(),
            LinearNoBias(atom_z, atom_z),
            nn.ReLU(),
            LinearNoBias(atom_z, atom_z),
        )
        init.final_init_(self.p_mlp[5].weight)

        self.atom_trans_bias = atom_trans_bias

    def forward(
        self,
        feats,
        s_trunk=None,  # Float['bm n ts'],
        z=None,  # Float['bm n n tz'],
    ):
        with torch.autocast("cuda", enabled=False):
            B, N, _ = feats["ref_pos"].shape
            atom_mask = feats["atom_pad_mask"].bool()  # Bool['b m'],

            atom_ref_pos = feats["ref_pos"]  # Float['b m 3'],
            atom_uid = feats["ref_space_uid"]  # Long['b m'],

            atom_feats = [
                atom_ref_pos,
                feats["ref_charge"].unsqueeze(-1),
                feats["ref_element"],
            ]
            if not self.use_no_atom_char:
                atom_feats.append(feats["ref_atom_name_chars"].reshape(B, N, 4 * 64))
            if self.use_atom_backbone_feat:
                atom_feats.append(feats["atom_backbone_feat"])
            if self.use_residue_feats_atoms:
                res_feats = torch.cat(
                    [
                        feats["res_type"],
                        feats["modified"].unsqueeze(-1),
                        one_hot(feats["mol_type"], num_classes=4).float(),
                    ],
                    dim=-1,
                )
                atom_to_token = feats["atom_to_token"].float()
                atom_res_feats = torch.bmm(atom_to_token, res_feats)
                atom_feats.append(atom_res_feats)

            atom_feats = torch.cat(atom_feats, dim=-1)

            c = self.embed_atom_features(atom_feats)

        # note we are already creating the windows to make it more efficient
        W, H = self.atoms_per_window_queries, self.atoms_per_window_keys
        B, N = c.shape[:2]
        K = N // W
        keys_indexing_matrix = get_indexing_matrix(K, W, H, c.device)
        to_keys = partial(
            single_to_keys, indexing_matrix=keys_indexing_matrix, W=W, H=H
        )

        atom_ref_pos_queries = atom_ref_pos.view(B, K, W, 1, 3)
        atom_ref_pos_keys = to_keys(atom_ref_pos).view(B, K, 1, H, 3)

        d = atom_ref_pos_keys - atom_ref_pos_queries  # Float['b k w h 3']
        d_norm = torch.sum(d * d, dim=-1, keepdim=True)  # Float['b k w h 1']
        d_norm = 1 / (1 + d_norm)  # AF3 feeds in the reciprocal of the distance norm

        atom_mask_queries = atom_mask.view(B, K, W, 1)
        atom_mask_keys = (
            to_keys(atom_mask.unsqueeze(-1).float()).view(B, K, 1, H).bool()
        )
        atom_uid_queries = atom_uid.view(B, K, W, 1)
        atom_uid_keys = to_keys(atom_uid.unsqueeze(-1).float()).view(B, K, 1, H).long()
        v = (
            (atom_mask_queries & atom_mask_keys & (atom_uid_queries == atom_uid_keys))
            .float()
            .unsqueeze(-1)
        )  # Bool['b k w h 1']

        p = self.embed_atompair_ref_pos(d) * v
        p = p + self.embed_atompair_ref_dist(d_norm) * v
        p = p + self.embed_atompair_mask(v) * v

        q = c

        if self.structure_prediction:
            # run only in structure model not in initial encoding
            atom_to_token = feats["atom_to_token"].float()  # Long['b m n'],

            s_to_c = self.s_to_c_trans(s_trunk.float())
            s_to_c = torch.bmm(atom_to_token, s_to_c)
            c = c + s_to_c.to(c)

            atom_to_token_queries = atom_to_token.view(B, K, W, atom_to_token.shape[-1])
            atom_to_token_keys = to_keys(atom_to_token)
            z_to_p = self.z_to_p_trans(z.float())
            z_to_p = torch.einsum(
                "bijd,bwki,bwlj->bwkld",
                z_to_p,
                atom_to_token_queries,
                atom_to_token_keys,
            )
            p = p + z_to_p.to(p)

        p = p + self.c_to_p_trans_q(c.view(B, K, W, 1, c.shape[-1]))
        p = p + self.c_to_p_trans_k(to_keys(c).view(B, K, 1, H, c.shape[-1]))
        p = p + self.p_mlp(p)

        if self.atom_trans_bias:
            allatom_ref_pos_queries = atom_ref_pos.view(B, N, 1, 3)
            allatom_ref_pos_keys = atom_ref_pos.view(B, 1, N, 3)
            allatom_d = allatom_ref_pos_keys - allatom_ref_pos_queries
            allatom_d_norm = torch.sum(allatom_d * allatom_d, dim=-1, keepdim=True)
            allatom_d_norm = 1 / (1 + allatom_d_norm)
            allatom_mask_queries = atom_mask.view(B, N, 1)
            allatom_mask_keys = atom_mask.view(B, 1, N)
            allatom_uid_queries = atom_uid.view(B, N, 1)
            allatom_uid_keys = atom_uid.view(B, 1, N)
            allatom_v = (
                (
                    allatom_mask_queries
                    & allatom_mask_keys
                    & (allatom_uid_queries == allatom_uid_keys)
                )
                .float()
                .unsqueeze(-1)
            )
            allatom_p = self.embed_atompair_ref_pos(allatom_d) * allatom_v
            allatom_p = (
                allatom_p + self.embed_atompair_ref_dist(allatom_d_norm) * allatom_v
            )
            allatom_p = allatom_p + self.embed_atompair_mask(allatom_v) * allatom_v
            allatom_p = allatom_p + self.c_to_p_trans_q(c.view(B, N, 1, c.shape[-1]))
            allatom_p = allatom_p + self.c_to_p_trans_k(c.view(B, 1, N, c.shape[-1]))
            allatom_p = allatom_p + self.p_mlp(allatom_p)
        return q, c, p, to_keys, allatom_p if self.atom_trans_bias else None


class AtomAttentionEncoder(Module):
    def __init__(
        self,
        atom_s,
        token_s,
        atoms_per_window_queries,
        atoms_per_window_keys,
        atom_encoder_depth=3,
        atom_encoder_heads=4,
        structure_prediction=True,
        activation_checkpointing=False,
        gaussian_random_3d_encoding_dim=0,
        transformer_post_layer_norm=False,
        tfmr_s=None,
        flex_attention=False,
        sdp_attention=False,
        use_qk_norm=False,
        all_atom_prelayer_depth=0,
        all_atom_prelayer_heads=4,
        all_atom_postlayer_depth=0,
        all_atom_postlayer_heads=4,
        anchor_attention=False,
        absolute_coordinate_encoding=False,
    ):
        super().__init__()

        self.structure_prediction = structure_prediction
        if structure_prediction:
            self.gaussian_random_3d_encoding_dim = gaussian_random_3d_encoding_dim
            if gaussian_random_3d_encoding_dim > 0:
                self.encoding_3d = GaussianRandom3DEncodings(
                    gaussian_random_3d_encoding_dim
                )
            r_input_size = 3 + gaussian_random_3d_encoding_dim
            self.r_to_q_trans = LinearNoBias(r_input_size, atom_s)
            init.final_init_(self.r_to_q_trans.weight)
        if all_atom_prelayer_depth > 0:
            self.all_atom_prelayer = AllAtomTransformer(
                dim=atom_s,
                dim_single_cond=atom_s,
                depth=all_atom_prelayer_depth,
                heads=all_atom_prelayer_heads,
                activation_checkpointing=activation_checkpointing,
                post_layer_norm=transformer_post_layer_norm,
                flex_attention=False,
                sdp_attention=True,
                use_qk_norm=use_qk_norm,
            )
        else:
            self.all_atom_prelayer = None

        self.atom_encoder = AtomTransformer(
            dim=atom_s,
            dim_single_cond=atom_s,
            attn_window_queries=atoms_per_window_queries,
            attn_window_keys=atoms_per_window_keys,
            depth=atom_encoder_depth,
            heads=atom_encoder_heads,
            activation_checkpointing=activation_checkpointing,
            post_layer_norm=transformer_post_layer_norm,
            flex_attention=flex_attention,
            sdp_attention=sdp_attention,
            use_qk_norm=use_qk_norm,
        )

        if all_atom_postlayer_depth > 0:
            self.all_atom_postlayer = AllAtomTransformer(
                dim=atom_s,
                dim_single_cond=atom_s,
                depth=all_atom_postlayer_depth,
                heads=all_atom_postlayer_heads,
                activation_checkpointing=activation_checkpointing,
                post_layer_norm=transformer_post_layer_norm,
                flex_attention=False,
                sdp_attention=True,
                use_qk_norm=use_qk_norm,
            )
        else:
            self.all_atom_postlayer = None
        self.anchor_attention = anchor_attention
        if self.anchor_attention:
            # self.anchor_attention_layer = AllAtomTransformer(
            #     dim=atom_s,
            #     dim_single_cond=atom_s,
            #     depth=1,
            #     heads=atom_encoder_heads,
            #     activation_checkpointing=activation_checkpointing,
            #     post_layer_norm=transformer_post_layer_norm,
            #     pair_bias_attn=False,
            #     flex_attention=False,
            #     sdp_attention=True,
            #     global_mask=True,
            # )
            self.anchor_attention_layer = AnchorTransformer(
                depth=2,
                heads=atom_encoder_heads,
                dim=atom_s,
                activation_checkpointing=activation_checkpointing,
                post_layer_norm=transformer_post_layer_norm,
            )
        self.absolute_coordinate_encoding = absolute_coordinate_encoding
        if self.absolute_coordinate_encoding:
            self.coordinate_embedding_layer = nn.Sequential(
                LinearNoBias(3, atom_s),
                nn.ReLU(),
                LinearNoBias(atom_s, atom_s),
                nn.ReLU(),
                LinearNoBias(atom_s, atom_s),
                nn.ReLU(),
                LinearNoBias(atom_s, atom_s),
            )
            init.final_init_(self.coordinate_embedding_layer[6].weight)

        self.atom_to_token_trans = nn.Sequential(
            LinearNoBias(atom_s, tfmr_s if structure_prediction else token_s),
            nn.ReLU(),
        )
        self.atoms_per_window_queries = atoms_per_window_queries
        self.atoms_per_window_keys = atoms_per_window_keys

    def forward(
        self,
        feats,
        q,
        c,
        atom_enc_bias,
        to_keys,
        r=None,  # Float['bm m 3'],
        multiplicity=1,
        all_atom_bias=None,
    ):
        B, N, _ = feats["ref_pos"].shape
        atom_mask = feats["atom_pad_mask"].bool()  # Bool['b m'],

        if self.structure_prediction:
            # only here the multiplicity kicks in because we use the different positions r
            q = q.repeat_interleave(multiplicity, 0)

            r_input = r
            if self.gaussian_random_3d_encoding_dim > 0:
                r_input = torch.cat([r_input, self.encoding_3d(r)], dim=-1)

            r_to_q = self.r_to_q_trans(r_input)
            q = q + r_to_q
            if self.absolute_coordinate_encoding:
                q = q + self.coordinate_embedding_layer(
                    feats["absolute_coords"].squeeze(0)
                ).repeat_interleave(multiplicity, dim=0)
            # initalize to 0

        c = c.repeat_interleave(multiplicity, 0)
        atom_mask = atom_mask.repeat_interleave(multiplicity, 0)

        if self.all_atom_prelayer is not None:
            q = self.all_atom_prelayer(q, c, all_atom_bias, atom_mask, multiplicity)

        q = self.atom_encoder(
            q=q,
            mask=atom_mask,
            c=c,
            bias=atom_enc_bias,
            multiplicity=multiplicity,
            to_keys=to_keys,
        )

        if self.all_atom_postlayer is not None:
            q = self.all_atom_postlayer(q, c, all_atom_bias, atom_mask, multiplicity)

        if self.anchor_attention:
            is_anchor = (
                (feats["atom_to_token"][0].float() @ feats["is_anchor"].float().t())
                .squeeze(1)
                .bool()
            )
            # attention_mask = is_anchor.unsqueeze(0) | is_anchor.unsqueeze(1)
            # q = self.anchor_attention_layer(q, c, None, attention_mask, multiplicity)
            if is_anchor.sum() > 0:
                q = self.anchor_attention_layer(
                    q,
                    q[:, is_anchor, :],
                    c,
                    c[:, is_anchor, :],
                    None,
                    atom_mask,
                    multiplicity,
                )

        with torch.autocast("cuda", enabled=False):
            q_to_a = self.atom_to_token_trans(q).float()
            atom_to_token = feats["atom_to_token"].float()
            atom_to_token = atom_to_token.repeat_interleave(multiplicity, 0)
            atom_to_token_mean = atom_to_token / (
                atom_to_token.sum(dim=1, keepdim=True) + 1e-6
            )
            a = torch.bmm(atom_to_token_mean.transpose(1, 2), q_to_a)

        a = a.to(q)

        return a, q, c, to_keys


class AtomAttentionDecoder(Module):
    """Algorithm 6."""

    def __init__(
        self,
        atom_s,
        tfmr_s,
        attn_window_queries,
        attn_window_keys,
        atom_decoder_depth=3,
        atom_decoder_heads=4,
        activation_checkpointing=False,
        transformer_post_layer_norm=False,
        predict_res_type=False,
        predict_atom_type=False,
        predict_bond_type: bool = False,
        predict_bond_len: bool = False,
        restrict_atom_types: bool = False,
        inverse_fold=False,
        flex_attention=False,
        sdp_attention=False,
        use_qk_norm=False,
        all_atom_prelayer_depth=0,
        all_atom_prelayer_heads=4,
        all_atom_postlayer_depth=0,
        all_atom_postlayer_heads=4,
    ):
        super().__init__()
        self.predict_res_type = predict_res_type
        self.predict_atom_type = predict_atom_type
        self.predict_bond_type = predict_bond_type
        self.predict_bond_len = predict_bond_len
        self.restrict_atom_types = restrict_atom_types
        self.inverse_fold = inverse_fold
        self.a_to_q_trans = LinearNoBias(tfmr_s, atom_s)
        init.final_init_(self.a_to_q_trans.weight)

        if all_atom_prelayer_depth > 0:
            self.all_atom_prelayer = AllAtomTransformer(
                dim=atom_s,
                dim_single_cond=atom_s,
                depth=all_atom_prelayer_depth,
                heads=all_atom_prelayer_heads,
                activation_checkpointing=activation_checkpointing,
                post_layer_norm=transformer_post_layer_norm,
                flex_attention=False,
                sdp_attention=True,
                use_qk_norm=use_qk_norm,
            )
        else:
            self.all_atom_prelayer = None

        self.atom_decoder = AtomTransformer(
            dim=atom_s,
            dim_single_cond=atom_s,
            attn_window_queries=attn_window_queries,
            attn_window_keys=attn_window_keys,
            depth=atom_decoder_depth,
            heads=atom_decoder_heads,
            activation_checkpointing=activation_checkpointing,
            post_layer_norm=transformer_post_layer_norm,
            flex_attention=flex_attention,
            sdp_attention=sdp_attention,
            use_qk_norm=use_qk_norm,
        )

        if all_atom_postlayer_depth > 0:
            self.all_atom_postlayer = AllAtomTransformer(
                dim=atom_s,
                dim_single_cond=atom_s,
                depth=all_atom_postlayer_depth,
                heads=all_atom_postlayer_heads,
                activation_checkpointing=activation_checkpointing,
                post_layer_norm=transformer_post_layer_norm,
                flex_attention=False,
                sdp_attention=True,
                use_qk_norm=use_qk_norm,
            )
        else:
            self.all_atom_postlayer = None

        if transformer_post_layer_norm and not inverse_fold:
            self.atom_feat_to_atom_pos_update = LinearNoBias(atom_s, 3)
            init.final_init_(self.atom_feat_to_atom_pos_update.weight)
        elif not inverse_fold:
            self.atom_feat_to_atom_pos_update = nn.Sequential(
                nn.LayerNorm(atom_s), LinearNoBias(atom_s, 3)
            )
            init.final_init_(self.atom_feat_to_atom_pos_update[1].weight)

        if predict_res_type:
            self.res_type_predictor = Linear(atom_s, len(const.tokens))

        if predict_atom_type:
            if self.restrict_atom_types:
                self.allowed_atom_indices = torch.tensor(
                    const.ALLOWED_ATOMIC_NUMS, dtype=torch.long
                )
                self.atom_type_predictor = Linear(
                    atom_s, len(const.ALLOWED_ATOMIC_NUMS)
                )
            else:
                self.atom_type_predictor = Linear(atom_s, const.num_elements)


        if self.predict_bond_type:
            self.bond_type_head = nn.Sequential(
                nn.Linear(atom_s * 2, atom_s, bias=False),
                nn.ReLU(),
                nn.Linear(atom_s, len(const.bond_types) + 1, bias=False),
            )

        if self.predict_bond_len:
            self.bond_len_head = nn.Sequential(
                nn.Linear(atom_s * 2, atom_s, bias=False),
                nn.ReLU(),
                nn.Linear(atom_s, 1, bias=False),
            )


    def forward(
        self,
        a,  # Float['bm n 2ts'],
        q,  # Float['bm m as'],
        c,  # Float['bm m as'],
        atom_dec_bias,  # Float['bm m m az'],
        feats,
        to_keys,
        multiplicity=1,
        all_atom_bias=None,
    ):
        with torch.autocast("cuda", enabled=False):
            atom_to_token = feats["atom_to_token"].float()
            atom_to_token = atom_to_token.repeat_interleave(multiplicity, 0)

            a_to_q = self.a_to_q_trans(a.float())
            a_to_q = torch.bmm(atom_to_token, a_to_q)

        q = q + a_to_q.to(q)
        atom_mask = feats["atom_pad_mask"]  # Bool['b m'],
        atom_mask = atom_mask.repeat_interleave(multiplicity, 0)

        if self.all_atom_prelayer is not None:
            q = self.all_atom_prelayer(q, c, all_atom_bias, atom_mask, multiplicity)

        q = self.atom_decoder(
            q=q,
            mask=atom_mask,
            c=c,
            bias=atom_dec_bias,
            multiplicity=multiplicity,
            to_keys=to_keys,
        )

        if self.all_atom_postlayer is not None:
            q = self.all_atom_postlayer(q, c, all_atom_bias, atom_mask, multiplicity)

        need_s_feat = self.predict_res_type or self.predict_bond_type or self.predict_bond_len

        res_type = None
        s_feat = None
        if need_s_feat:
            idx = torch.argmax(feats["atom_to_token"].int(), dim=-1)
            mask = feats["atom_pad_mask"].repeat_interleave(multiplicity, 0)
            idx = idx.repeat_interleave(multiplicity, 0)
            src = q * mask[:, :, None]
            idx_expanded = idx.unsqueeze(-1).expand(-1, -1, q.size(-1))
            s_feat = torch.zeros(
                (q.shape[0], feats["res_type"].shape[1], q.shape[-1]),
                device=idx_expanded.device,
            )
            s_feat.scatter_add_(dim=1, index=idx_expanded, src=src)

        if self.predict_res_type and s_feat is not None:
            res_type = self.res_type_predictor(s_feat)

        atom_type = None
        if self.predict_atom_type:
            if self.restrict_atom_types:
                small_logits = self.atom_type_predictor(q)
                pad_val = -1e9
                full_shape = (*small_logits.shape[:-1], const.num_elements)
                atom_type_full = small_logits.new_full(full_shape, pad_val)
                atom_type_full.index_copy_(
                    -1, self.allowed_atom_indices.to(small_logits.device), small_logits
                )
                atom_type = atom_type_full
            else:
                atom_type = self.atom_type_predictor(q)

        bond_type_logits = None
        bond_len_pred = None

        if (self.predict_bond_type or self.predict_bond_len) and s_feat is not None:
            B, n_tok, D = s_feat.shape
            token_mask = (feats["design_mask"] * feats["token_pad_mask"]).bool()
            token_mask = token_mask.repeat_interleave(multiplicity, 0)

            if self.predict_bond_type:
                bond_type_logits = s_feat.new_zeros(
                    B, n_tok, n_tok, len(const.bond_types)+1
                )
            if self.predict_bond_len:
                bond_len_pred = s_feat.new_zeros(B, n_tok, n_tok)

            for b in range(B):
                mask_b = token_mask[b]
                s_design = s_feat[b, mask_b]  # (M, D)
                M = s_design.size(0)
                si = s_design.unsqueeze(1).expand(-1, M, -1)  # (M, M, D)
                sj = s_design.unsqueeze(0).expand(M, -1, -1)  # (M, M, D)
                pair_tok = torch.cat([si, sj], dim=-1)  # (M, M, 2D)
                idx = torch.nonzero(mask_b, as_tuple=False).squeeze(1)

                if self.predict_bond_type:
                    bond_type_logits[b][idx[:, None], idx[None, :]] = self.bond_type_head(pair_tok)
                if self.predict_bond_len:
                    bond_len_pred[b][idx[:, None], idx[None, :]] = self.bond_len_head(pair_tok).squeeze(-1)
        r_update = None
        if not self.inverse_fold:
            r_update = self.atom_feat_to_atom_pos_update(q)

        return r_update, res_type, atom_type, bond_type_logits, bond_len_pred
