from typing import Any

import numpy as np
import torch
from torch.nn.functional import one_hot

from foldeverything.data import const
from foldeverything.data.data import Tokenized


def load_dummy_templates_v2(tdim: int, num_tokens: int) -> list[dict]:
    """Load dummy templates for v2."""
    # Allocate features
    res_type = np.zeros((tdim, num_tokens), dtype=np.int64)
    frame_rot = np.zeros((tdim, num_tokens, 3, 3), dtype=np.float32)
    frame_t = np.zeros((tdim, num_tokens, 3), dtype=np.float32)
    cb_coords = np.zeros((tdim, num_tokens, 3), dtype=np.float32)
    ca_coords = np.zeros((tdim, num_tokens, 3), dtype=np.float32)
    frame_mask = np.zeros((tdim, num_tokens), dtype=np.float32)
    cb_mask = np.zeros((tdim, num_tokens), dtype=np.float32)
    template_mask = np.zeros((tdim, num_tokens), dtype=np.float32)
    query_to_template = np.zeros((tdim, num_tokens), dtype=np.int64)
    visibility_ids = np.zeros((tdim, num_tokens), dtype=np.float32)

    # Convert to one-hot
    res_type = torch.from_numpy(res_type)
    res_type = one_hot(res_type, num_classes=const.num_tokens)

    return {
        "template_restype": res_type,
        "template_frame_rot": torch.from_numpy(frame_rot),
        "template_frame_t": torch.from_numpy(frame_t),
        "template_cb": torch.from_numpy(cb_coords),
        "template_ca": torch.from_numpy(ca_coords),
        "template_mask_cb": torch.from_numpy(cb_mask),
        "template_mask_frame": torch.from_numpy(frame_mask),
        "template_mask": torch.from_numpy(template_mask),
        "query_to_template": torch.from_numpy(query_to_template),
        "visibility_ids": torch.from_numpy(visibility_ids),
    }


def compute_template_features(
    query_tokens: Tokenized,
    tmpl_tokens: list[dict],
    num_tokens: int,
) -> dict:
    """Compute the template features."""
    # Allocate features
    res_type = np.zeros((num_tokens,), dtype=np.int64)
    frame_rot = np.zeros((num_tokens, 3, 3), dtype=np.float32)
    frame_t = np.zeros((num_tokens, 3), dtype=np.float32)
    cb_coords = np.zeros((num_tokens, 3), dtype=np.float32)
    ca_coords = np.zeros((num_tokens, 3), dtype=np.float32)
    frame_mask = np.zeros((num_tokens,), dtype=np.float32)
    cb_mask = np.zeros((num_tokens,), dtype=np.float32)
    template_mask = np.zeros((num_tokens,), dtype=np.float32)
    query_to_template = np.zeros((num_tokens,), dtype=np.int64)
    visibility_ids = np.zeros((num_tokens,), dtype=np.float32)

    # Now create features per token
    asym_id_to_pdb_id = {}

    for token_dict in tmpl_tokens:
        idx = token_dict["q_idx"]
        monomeric = token_dict["is_monomeric"]
        pdb_id = token_dict["pdb_id"]
        token = token_dict["token"]
        query_token = query_tokens.tokens[idx]
        if not monomeric:
            asym_id_to_pdb_id[query_token["asym_id"]] = pdb_id

        res_type[idx] = token["res_type"]
        frame_rot[idx] = token["frame_rot"].reshape(3, 3)
        frame_t[idx] = token["frame_t"]
        cb_coords[idx] = token["disto_coords"]
        ca_coords[idx] = token["center_coords"]
        cb_mask[idx] = token["disto_mask"]
        frame_mask[idx] = token["frame_mask"]
        template_mask[idx] = 1.0

    # Set visibility_id for templated chains
    for asym_id, pdb_id in asym_id_to_pdb_id.items():
        indices = (query_tokens.tokens["asym_id"] == asym_id).nonzero()
        visibility_ids[indices] = pdb_id

    # Set visibility for non templated chain + olygomerics
    for asym_id in np.unique(query_tokens.structure.chains["asym_id"]):
        if asym_id not in asym_id_to_pdb_id:
            # We hack the chain id to be negative to not overlap with the above
            indices = (query_tokens.tokens["asym_id"] == asym_id).nonzero()
            visibility_ids[indices] = -1 - asym_id

    # Convert to one-hot
    res_type = torch.from_numpy(res_type)
    res_type = one_hot(res_type, num_classes=const.num_tokens)

    return {
        "template_restype": res_type,
        "template_frame_rot": torch.from_numpy(frame_rot),
        "template_frame_t": torch.from_numpy(frame_t),
        "template_cb": torch.from_numpy(cb_coords),
        "template_ca": torch.from_numpy(ca_coords),
        "template_mask_cb": torch.from_numpy(cb_mask),
        "template_mask_frame": torch.from_numpy(frame_mask),
        "template_mask": torch.from_numpy(template_mask),
        "query_to_template": torch.from_numpy(query_to_template),
        "visibility_ids": torch.from_numpy(visibility_ids),
    }


def compute_template_features_with_expansion(
    template_tokens: list[Tokenized],
    query_token_indices: list[int],
    tmlp_token_to_metadata: dict[int, dict[str, Any]],
    num_tokens: int,
) -> dict[str, np.ndarray]:
    """Compute the template features."""
    # Allocate features
    assert num_tokens == len(query_token_indices)
    res_type = np.zeros((num_tokens,), dtype=np.int64)
    frame_rot = np.zeros((num_tokens, 3, 3), dtype=np.float32)
    frame_t = np.zeros((num_tokens, 3), dtype=np.float32)
    cb_coords = np.zeros((num_tokens, 3), dtype=np.float32)
    ca_coords = np.zeros((num_tokens, 3), dtype=np.float32)
    frame_mask = np.zeros((num_tokens,), dtype=np.float32)
    cb_mask = np.zeros((num_tokens,), dtype=np.float32)
    template_mask = np.zeros((num_tokens,), dtype=np.float32)
    query_to_template = np.zeros((num_tokens,), dtype=np.int64)
    token_pair_mask = np.eye(num_tokens, dtype=np.float32)

    # Now create features per token
    tok_offset = 0
    for i, data in enumerate(template_tokens):
        for idx, token in enumerate(data.tokens):
            tok_idx = tok_offset + idx
            res_type[tok_idx] = token["res_type"]
            frame_rot[tok_idx] = token["frame_rot"].reshape(3, 3)
            frame_t[tok_idx] = token["frame_t"]
            cb_coords[tok_idx] = token["disto_coords"]
            ca_coords[tok_idx] = token["center_coords"]
            cb_mask[tok_idx] = token["disto_mask"]
            frame_mask[tok_idx] = token["frame_mask"]

            # Set query token info
            if (i, token["token_idx"]) in tmlp_token_to_metadata:
                metadata = tmlp_token_to_metadata[(i, token["token_idx"])]
                query_token_idx = metadata["q_idx"]
                template_mask[query_token_idx] = 1
                query_to_template[query_token_idx] = tok_idx

                # Set token pair mask
                # Should be one when same PDB and both monomeric
                for other_idx, other in enumerate(data.tokens):
                    if (i, other["token_idx"]) not in tmlp_token_to_metadata:
                        continue

                    other_tok_idx = tok_offset + other_idx
                    other_metadata = tmlp_token_to_metadata[(i, other["token_idx"])]
                    if (
                        other_metadata["pdb_id"] == metadata["pdb_id"]
                        and other_metadata["is_monomeric"]
                        and metadata["is_monomeric"]
                    ):
                        token_pair_mask[tok_idx, other_tok_idx] = 1

        tok_offset += len(data.tokens)

    # Convert to one-hot
    res_type = torch.from_numpy(res_type)
    res_type = one_hot(res_type, num_classes=const.num_tokens)

    return {
        "template_restype": res_type,
        "template_frame_rot": torch.from_numpy(frame_rot),
        "template_frame_t": torch.from_numpy(frame_t),
        "template_cb": torch.from_numpy(cb_coords),
        "template_ca": torch.from_numpy(ca_coords),
        "template_mask_cb": torch.from_numpy(cb_mask),
        "template_mask_frame": torch.from_numpy(frame_mask),
        "template_mask": torch.from_numpy(template_mask),
        "query_to_template": torch.from_numpy(query_to_template),
        "token_pair_mask": torch.from_numpy(token_pair_mask),
    }
