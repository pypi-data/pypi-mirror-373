from typing import Dict, List, Optional
import torch
from dataclasses import dataclass

loss_classes = {}

# TODO: for all of these losses, we should only include pairs of positions
# where at least one of them is a designed residue.

# todo: log pairs to optimize

@dataclass
class LossTerm:
    kind: str
    name: str
    weight: float
    requires_target: bool

    def save_info(self, loss_info, key, value):
        if loss_info is not None:
            loss_info[f"{self.name}_{key}"] = value

    def save_info_list_extend(self, loss_info, key, value_list):
        if loss_info is not None:
            if key not in loss_info:
                loss_info[key] = []
            loss_info[key].extend(value_list)

@dataclass
class IntraContactDistogramEntropy(LossTerm):
    asym_id: Optional[int]
    sequence_distance_threshold: int
    spatial_distance_threshold: int
    num_pairs: int
    bins_threshold: int

    @staticmethod
    def guess_asym_id(batch, design_mask, context="IntraContactDistogramEntropy"):
        # The guessed asym_id is whatever chain has the most designed residues
        asym_id = torch.mode(batch["asym_id"][design_mask]).values.item()
        print(f"Guessed asym_id based on design_mask for {context}: {asym_id}")
        if not (batch["asym_id"][design_mask] == asym_id).all().item():
            print("Warning: not all designed residues are in this chain!")
        return asym_id

    def compute_loss(self, batch, out, design_mask, loss_info=None):
        if self.asym_id is None:
            self.asym_id = self.guess_asym_id(batch, design_mask)

        entropy = distogram_entropy(
            out["pdistogram"],
            threshold_angstroms=self.bins_threshold
        )
        contact_mask = primary_sequence_token_distance_mask(
            batch,
            min_distance=self.sequence_distance_threshold
        ).bool() & specific_asym_id_mask(batch, self.asym_id)
        if contact_mask.sum().item() == 0:
            raise ValueError(f"Sequence length is too short for the specified sequence distance threshold {self.sequence_distance_threshold}")
        
        entropy_cutoff = ((~contact_mask) * 1e6 + entropy).flatten().topk(
            k=self.num_pairs * 2,
            largest=False
        )[0][-1]
        pairs = contact_mask & (entropy <= entropy_cutoff).squeeze()
        
        self.save_info(loss_info, "num_pairs", pairs.sum().item())
        self.save_info(loss_info, "entropy_cutoff", entropy_cutoff.item())
        self.save_info(loss_info, "entropy", entropy)
        self.save_info_list_extend(loss_info, "pairs_to_optimize", pairs.nonzero().tolist())
        
        if pairs.sum().item() == 0:
            return None

        loss = (entropy * pairs.unsqueeze(0)).nansum() / pairs.sum()
        self.save_info(loss_info, "loss", loss.item())
        return loss

loss_classes["intra_contact_distogram_entropy"] = IntraContactDistogramEntropy

@dataclass
class InterContactDistogramEntropy(LossTerm):
    asym_id1: Optional[int]
    asym_id2: Optional[int]
    spatial_distance_threshold: int
    num_pairs: int
    bins_threshold: int


    def compute_loss(self, batch, out, design_mask, loss_info=None):
        entropy = distogram_entropy(
            out["pdistogram"],
            threshold_angstroms=self.bins_threshold
        )
        if self.asym_id1 is None:
            # First asym_id defaults to the designed chain
            assert self.asym_id2 is None
            self.asym_id1 = IntraContactDistogramEntropy.guess_asym_id(
                batch,
                design_mask,
                context="InterContactDistogramEntropy asym_id1"
            )
        if self.asym_id2 is None:
            # Second asym_id defaults to the longest chain different from asym_id1
            asym_ids = batch["asym_id"].squeeze()
            asym_ids = asym_ids[asym_ids != self.asym_id1]
            self.asym_id2 = torch.mode(asym_ids).values.item()
            print(f"Guessed asym_id2 for InterContactDistogramEntropy: {self.asym_id2}")
            if not (asym_ids == self.asym_id2).all().item():
                print("Warning: there are other chains not being included here")

        contact_mask = specific_asym_id_mask(batch, self.asym_id1, self.asym_id2).bool()
        entropy_cutoff = ((~contact_mask) * 1e6 + entropy).flatten().topk(
            k=self.num_pairs * 2,
            largest=False
        )[0][-1]
        pairs = contact_mask & (entropy <= entropy_cutoff).squeeze()

        self.save_info(loss_info, "num_pairs", pairs.sum().item())
        self.save_info(loss_info, "entropy_cutoff", entropy_cutoff.item())
        self.save_info(loss_info, "entropy", entropy)
        self.save_info_list_extend(loss_info, "pairs_to_optimize", pairs.nonzero().tolist())
        
        if pairs.sum().item() == 0:
            return None

        loss = (entropy * pairs.unsqueeze(0)).nansum() / pairs.sum()
        self.save_info(loss_info, "loss", loss.item())
        return loss
    
loss_classes["inter_contact_distogram_entropy"] = InterContactDistogramEntropy
    

class HallucinationLoss:
    def __init__(self, terms : List[Dict]):
        self.loss_terms = []
        for loss_dict in terms:
            loss_class = loss_classes[loss_dict["kind"]]
            self.loss_terms.append(loss_class(**loss_dict))

    def compute_loss(self, batch, out, design_mask, include_target=True, loss_info=None):
        losses_to_compute = [
            loss for loss in self.loss_terms
            if (not loss.requires_target) or include_target
        ]
        weighted_losses = [
            loss.compute_loss(batch, out, design_mask, loss_info=loss_info) * loss.weight
            for loss in losses_to_compute
        ]
        total_loss = sum(weighted_losses)
        if loss_info is not None:
            loss_info["loss"] = total_loss.item() if hasattr(total_loss, "item") else total_loss
        return total_loss
    
    def __str__(self):
        return str(self.loss_terms)

    

# Helper functions
    
def distogram_atom_distance_mask(pdistogram, min_distance=10):
    predicted_distances = predicted_distance(pdistogram)
    return predicted_distances < min_distance

def predicted_distance(features, out, na_value=torch.nan):
    pdistogram = out["pdistogram"]
    predicted_distances = (
        torch.softmax(pdistogram, dim=-1) * torch.linspace(0, 22, 64, device=pdistogram.device).reshape((1, 1, -1))).sum(axis=-1).squeeze()

    # Mask out based on features["token_pad_mask"] (outer product)
    pad_mask = features["token_pad_mask"].squeeze().bool()
    pad_mask_pairwise = pad_mask[:, None] * pad_mask[None, :]
    predicted_distances = predicted_distances.masked_fill(~pad_mask_pairwise, na_value)
    return predicted_distances

def primary_sequence_atom_distance_mask(batch, min_distance=34):
    atom_to_token = batch["atom_to_token"].argmax(dim=-1).squeeze()
    result = ((atom_to_token[:, None] - atom_to_token[None, :]) >= min_distance)
    result = result * batch["atom_pad_mask"].squeeze()
    return result

def primary_sequence_token_distance_mask(batch, min_distance=34):
    token_indices = batch["token_index"].squeeze()
    asym_ids = batch["asym_id"].squeeze()
    different_asym_id = asym_ids[:, None] != asym_ids[None, :]
    result = ((token_indices[:, None] - token_indices[None, :]).abs() >= min_distance) | different_asym_id

    pad_mask = batch["token_pad_mask"].squeeze()
    result = result * (pad_mask[:, None] * pad_mask[None, :])
    return result

def different_asym_id_mask(batch):
    asym_ids = batch["asym_id"].squeeze()
    return asym_ids[:, None] != asym_ids[None, :]

def specific_asym_id_mask(batch, asym_id1, asym_id2=None):
    asym_ids = batch["asym_id"].squeeze()
    if asym_id2 is None:
        return (asym_ids[:, None] == asym_id1) & (asym_ids[None, :] == asym_id1)
    else:
        return (
            (asym_ids[:, None] == asym_id1) & (asym_ids[None, :] == asym_id2)
        ) | (
            (asym_ids[:, None] == asym_id2) & (asym_ids[None, :] == asym_id1)
        )

def spatial_atom_distance_mask(batch, out, min_distance=10):
    # Mask that is 1 if the distance between any two atoms is less than min_distance
    coords = out["sample_atom_coords"].squeeze()
    result = ((coords[:, None, :] - coords[None, :, :]) ** 2).sum(dim=-1) < min_distance ** 2
    return result.float()

def distogram_entropy(pdistogram, threshold_angstroms=10, pdistogram_mask=None):
    if pdistogram_mask is None:
        pdistogram_mask = torch.ones(pdistogram.shape[:3], device=pdistogram.device)
    
    pdistogram = pdistogram.squeeze(-2)
    pdistogram_mask = pdistogram_mask.bool()

    assert tuple(pdistogram.shape) == tuple(pdistogram_mask.shape[:3]) + (64,), (pdistogram_mask.shape, pdistogram.shape)

    bins = (torch.linspace(0, 22, 64, device=pdistogram.device) < threshold_angstroms).float()
    qstar = torch.softmax(pdistogram - 1e7 * (1 - bins), dim=-1)
    q = torch.softmax(pdistogram, dim=-1)
    log_q = torch.log(q + 1e-10) # avoid log(0)

    result = -torch.einsum("bijm,bijm->bij", qstar, log_q).masked_fill(~pdistogram_mask, torch.nan)
    return result