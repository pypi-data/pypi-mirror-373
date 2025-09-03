from __future__ import annotations

import torch
from torch import nn
from torch.nn import Module

from foldeverything.model.modules.encoders import (
    PairwiseConditioning,
    AtomEncoder,
)


class DiffusionConditioning(Module):
    def __init__(
        self,
        token_s: int,
        token_z: int,
        atom_s: int,
        atom_z: int,
        atoms_per_window_queries: int = 32,
        atoms_per_window_keys: int = 128,
        atom_encoder_depth: int = 3,
        atom_encoder_heads: int = 4,
        token_transformer_depth: int = 24,
        token_transformer_heads: int = 8,
        extra_token_transformer_heads: int = None,
        extra_token_transformer_depth: int = None,
        atom_decoder_depth: int = 3,
        atom_decoder_heads: int = 4,
        atom_feature_dim: int = 128,
        conditioning_transition_layers: int = 2,
        use_no_atom_char: bool = False,
        use_atom_backbone_feat: bool = False,
        use_residue_feats_atoms: bool = False,
        all_atom_conditioning: bool = False,
        all_atom_encoder_prelayer_depth: int = 0,
        all_atom_encoder_postlayer_depth: int = 0,
        all_atom_decoder_prelayer_depth: int = 0,
        all_atom_decoder_postlayer_depth: int = 0,
    ) -> None:
        super().__init__()

        self.pairwise_conditioner = PairwiseConditioning(
            token_z=token_z,
            dim_token_rel_pos_feats=token_z,
            num_transitions=conditioning_transition_layers,
        )

        self.atom_encoder = AtomEncoder(
            atom_s=atom_s,
            atom_z=atom_z,
            token_s=token_s,
            token_z=token_z,
            atoms_per_window_queries=atoms_per_window_queries,
            atoms_per_window_keys=atoms_per_window_keys,
            atom_feature_dim=atom_feature_dim,
            structure_prediction=True,
            use_no_atom_char=use_no_atom_char,
            use_atom_backbone_feat=use_atom_backbone_feat,
            use_residue_feats_atoms=use_residue_feats_atoms,
            atom_trans_bias=all_atom_conditioning,
        )

        self.atom_enc_proj_z = nn.ModuleList()
        for _ in range(atom_encoder_depth):
            self.atom_enc_proj_z.append(
                nn.Sequential(
                    nn.LayerNorm(atom_z),
                    nn.Linear(atom_z, atom_encoder_heads, bias=False),
                )
            )

        self.atom_dec_proj_z = nn.ModuleList()
        for _ in range(atom_decoder_depth):
            self.atom_dec_proj_z.append(
                nn.Sequential(
                    nn.LayerNorm(atom_z),
                    nn.Linear(atom_z, atom_decoder_heads, bias=False),
                )
            )

        self.token_trans_proj_z = nn.ModuleList()
        for _ in range(token_transformer_depth):
            self.token_trans_proj_z.append(
                nn.Sequential(
                    nn.LayerNorm(token_z),
                    nn.Linear(token_z, token_transformer_heads, bias=False),
                )
            )

        self.extra_token_trans_proj_z = None
        if extra_token_transformer_heads is not None:
            self.extra_token_trans_proj_z = nn.ModuleList()
            for _ in range(extra_token_transformer_depth):
                self.extra_token_trans_proj_z.append(
                    nn.Sequential(
                        nn.LayerNorm(token_z),
                        nn.Linear(token_z, extra_token_transformer_heads, bias=False),
                    )
                )
        if all_atom_conditioning:
            self.all_atom_proj_z = nn.Sequential(
                nn.LayerNorm(atom_z),
                nn.Linear(atom_z, atom_encoder_heads, bias=False),
            )

    def forward(
        self,
        s_trunk,  # Float['b n ts']
        z_trunk,  # Float['b n n tz']
        relative_position_encoding,  # Float['b n n tz']
        feats,
    ):
        z = self.pairwise_conditioner(
            z_trunk,
            relative_position_encoding,
        )

        q, c, p, to_keys, all_atom_p = self.atom_encoder(
            feats=feats,
            s_trunk=s_trunk,  # Float['b n ts'],
            z=z,  # Float['b n n tz'],
        )

        atom_enc_bias = []
        for layer in self.atom_enc_proj_z:
            atom_enc_bias.append(layer(p))
        atom_enc_bias = torch.cat(atom_enc_bias, dim=-1)

        atom_dec_bias = []
        for layer in self.atom_dec_proj_z:
            atom_dec_bias.append(layer(p))
        atom_dec_bias = torch.cat(atom_dec_bias, dim=-1)

        token_trans_bias = []
        for layer in self.token_trans_proj_z:
            token_trans_bias.append(layer(z))
        token_trans_bias = torch.cat(token_trans_bias, dim=-1)

        if self.extra_token_trans_proj_z is not None:
            extra_token_trans_bias = []
            for layer in self.extra_token_trans_proj_z:
                extra_token_trans_bias.append(layer(z))
            extra_token_trans_bias = torch.cat(extra_token_trans_bias, dim=-1)
        else:
            extra_token_trans_bias = None
        if all_atom_p is not None:
            all_atom_bias = self.all_atom_proj_z(all_atom_p)
        else:
            all_atom_bias = None
        return (
            q,
            c,
            to_keys,
            atom_enc_bias,
            atom_dec_bias,
            token_trans_bias,
            extra_token_trans_bias,
            all_atom_bias,
        )


class AllAtomDiffusionConditioning(Module):
    def __init__(
        self,
        token_s: int,
        token_z: int,
        atom_s: int,
        atom_z: int,
        atom_feature_dim: int = 128,
        conditioning_transition_layers: int = 2,
        use_no_atom_char: bool = False,
        use_atom_backbone_feat: bool = False,
        use_residue_feats_atoms: bool = False,
    ):
        pass

    def forward(
        self,
        s_trunk,
        z_trunk,
        relative_position_encoding,
        feats,
    ):
        pass
