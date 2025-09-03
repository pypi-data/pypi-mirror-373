import collections
import copy
from dataclasses import asdict, dataclass, replace
from frozendict import frozendict
from matplotlib import pyplot as plt
import pandas as pd
import torch
import tempfile
from typing import Callable, Dict, List, Optional
import time
import wandb
import numpy as np
import math

from tqdm import tqdm
from foldeverything.data import const
from foldeverything.data.data import Coords, Input, Structure, convert_ccd
from foldeverything.data.feature.af3 import (
    process_atom_features,
    process_ensemble_features,
)
from foldeverything.data.write.pdb import to_pdb
from foldeverything.model.loss.validation import compute_subset_rmsd
from foldeverything.task.hallucination.loss import (
    HallucinationLoss,
    distogram_entropy,
    predicted_distance,
)
from foldeverything.task.hallucination.plot import (
    plot_loss,
    plot_mutations,
    plot_distogram_animation,
)
from foldeverything.task.predict.data_ligands import collate

torch.autograd.set_detect_anomaly(True)


def tree_map(func, tree):
    if isinstance(tree, dict):
        return {k: tree_map(func, v) for k, v in tree.items()}
    elif isinstance(tree, (list, tuple)):
        return type(tree)(tree_map(func, item) for item in tree)
    else:
        return func(tree)


def clean_batch_in_place(batch):
    ignore_list = [
        "structure_group",
        "token_disto_mask",
        "token_distance_maskdisto_coords_ensemble",
        "noisy_center_coords",
        "frame_resolved_mask",
        "token_pair_mask",
        "center_coords",
        "res_type_clone",
        "disto_coords_ensemble",
        "disto_target",
        "token_distance_mask",
        "r_set_to_rep_atom",
        "absolute_coords",
    ]
    for k in ignore_list:
        if k in batch:
            del batch[k]

    # We are designing residues using hallucination, not the boltzgen diffusion model,
    # so we zero out the design mask that is given to the model.
    batch["design_mask"] = torch.zeros_like(batch["design_mask"])


def compute_rmsd(atom_coords: torch.Tensor, pred_atom_coords: torch.Tensor):
    rmsd, _ = compute_subset_rmsd(
        atom_coords,
        pred_atom_coords,
        atom_mask=torch.ones_like(atom_coords[..., 0]),
        align_weights=torch.ones_like(atom_coords[..., 0]),
        subset_mask=torch.ones_like(atom_coords[..., 0]),
        multiplicity=1,
    )
    return rmsd


@dataclass
class BinderHallucinationConfig:
    loss: HallucinationLoss
    optimization_stages: List[Dict]
    default_lr: float = 0.05
    initial_design_randomization: str = "full"
    update_atom_features: bool = True
    max_consecutive_steps_with_no_mutations: int = 100
    final_design_selection_criteria: str = "-loss"
    disallowed_amino_acids: List[str] = ()

    def check_valid(self):
        pass

class AbortDesign(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


def evaluate_expression(expression, namespace, include_torch_functions=False, include_math_functions=False):
    namespace = dict(namespace)
    if include_torch_functions:
        namespace.update({
            'exp': torch.exp,
            'log': torch.log,
            'log10': torch.log10,
            'sqrt': torch.sqrt,
            'abs': torch.abs,
            'min': torch.min,
            'max': torch.max,
            'sigmoid': torch.sigmoid,
        })
    if include_math_functions:
        namespace.update({
            'exp': math.exp,
            'log': math.log,
            'log10': math.log10,
            'sqrt': math.sqrt,
            'abs': abs,
            'min': min,
            'max': max,
            'sigmoid': lambda x: 1 / (1 + math.exp(-x)),
        })
    try:
        return eval(expression, {"__builtins__": {}}, namespace)
    except Exception as e:
        raise ValueError(
            f"Invalid expression: '{expression}'. "
            f"Error: {e}"
        )

@dataclass
class DesignRecord:
    hard_ptm: float
    hard_iptm: float
    loss: float
    step: int
    stage_num: int
    protocol: str
    argmax_sequence: str
    designed_one_hot_sequence: torch.Tensor
    affinity_value: float = None
    affinity_probability: float = None

    def evaluate_expression(self, expression):
        return evaluate_expression(
            expression,
            asdict(self),
            include_math_functions=True)

    def is_better_than(self, other, criteria="ptm+iptm"):
        if other is None:
            return True
        return self.evaluate_expression(criteria) > other.evaluate_expression(criteria)

    def __str__(self):
        return f"<Best design loss={self.loss} hard_ptm={self.hard_ptm} hard_iptm={self.hard_iptm} affinity_value={self.affinity_value} affinity_probability={self.affinity_probability} at stage {self.stage_num} {self.protocol} step {self.step}, sequence: {self.argmax_sequence}>"


def mutations_in_uppercase(reference_seq: str, current_seq: str) -> str:
    lower = current_seq.lower()
    result = "".join(
        lower[i].upper() if lower[i].lower() != reference_seq[i].lower() else lower[i]
        for i in range(len(lower))
    )
    return result


class BinderHallucination(torch.nn.Module):
    def __init__(
        self,
        boltz_model,
        initial_features: Dict[str, torch.Tensor],
        config: BinderHallucinationConfig,
        molecules: Dict,
        canonical_atoms: Dict,
        wandb_config: Optional[dict] = None,
        design_prefix: str = "",  # Prefix for wandb logging (e.g., "design_1"),
        save_design_callback: Callable[[DesignRecord], None] = None,
    ):
        super().__init__()
        self.config = config
        self.config.check_valid()
        self.design_mask = initial_features["design_mask"].clone().bool().detach()
        self.batch = dict(initial_features)
        clean_batch_in_place(self.batch)
        self.device = self.batch["res_type"].device

        # design_mask_expanded is the same shape as res_type (i.e. batch, seq_len, num_tokens)
        # indicating positions and token indices (i.e. the canonical amino acids) that we allow to vary
        self.design_mask_expanded = (
            self.design_mask.unsqueeze(-1).expand(self.batch["res_type"].shape).clone()
        )
        non_canonical_token_ids = torch.tensor(
            [const.token_ids[x] for x in const.non_canonincal_tokens]
        )
        self.design_mask_expanded[:, :, non_canonical_token_ids] = (
            False  # Zero out non-canonical tokens
        )

        self.res_type_from_initial_batch = self.batch.pop("res_type").clone().float()
        self.initial_structure_bonds, = self.batch["structure_bonds"].copy()

        # We drop non-covalent bond types (SINGLE, DOUBLE, TRIPLE, AROMATIC) as only
        # COVALENT bonds are used in writing mmcif output files, and output writing
        # is the only reason we keep track of atom-level (rather than token-level) bonds.
        self.initial_structure_bonds = self.initial_structure_bonds[
            self.initial_structure_bonds["type"] == const.bond_type_ids["COVALENT"]
        ]

        self.initial_atom_to_token_map = torch.argmax(self.batch["atom_to_token"].squeeze(0).float(), dim=-1)

        # Remove bonds that involve masked out tokens (e.g. ligands on the exclusion list)
        #for i in range(self.initial_structure_bonds.shape[0]):
            
        for aa in self.config.disallowed_amino_acids:
            assert aa in const.prot_letter_to_token, f"Invalid disallowed amino acid {aa}, expected one of {const.prot_letter_to_token.keys()}"
        
        self.allowed_designed_token_ids = torch.tensor([
            const.token_ids[x] for x in const.canonical_tokens
            if const.prot_token_to_letter[x] not in self.config.disallowed_amino_acids
        ], device=self.device)
        self.allowed_designed_tokens = [
            x for x in const.canonical_tokens
            if const.prot_token_to_letter[x] not in self.config.disallowed_amino_acids
        ]

        self.designed_soft_sequence = None

        self.seq_len = int(self.batch["token_pad_mask"].sum())
        self.num_designed_tokens = self.design_mask.sum()
        self.design_prefix = design_prefix

        self.max_tokens = int(self.batch["token_pad_mask"].shape[-1])
        self.max_atoms = int(self.batch["atom_pad_mask"].shape[-1])
        assert self.max_atoms % 32 == 0

        self.boltz_model = boltz_model
        self.boltz_model.always_enable_grad = True
        self.boltz_model.eval()

        self.trajectories = []
        self.wandb_config = wandb_config
        if self.wandb_config is not None:
            # Include design prefix in table columns if provided
            table_name = (
                f"{design_prefix}_trajectory" if design_prefix else "trajectory"
            )
            self.table = wandb.Table(columns=["stage", "step", "sequence", "mutations"])
            self.table_name = table_name
        else:
            self.table = None
            self.table_name = None

        self.best_design = None
        self.molecules = molecules
        self.canonical_atoms = canonical_atoms
        self.canonical_atom_name_to_index_within_residue = {}
        for res_type, res_data in self.canonical_atoms.items():
            for i, atom_name in enumerate(res_data["name"]):
                self.canonical_atom_name_to_index_within_residue[res_type, atom_name] = i

        self.loss = copy.deepcopy(self.config.loss)
        self.last_soft_res_type_transform = None
        self.saved_design_sequences = set()
        self.save_design_callback = save_design_callback
        self.reset_for_new_attempt()

    def get_asym_ids(self):
        mask = self.batch["token_pad_mask"].squeeze(0)
        asym_ids = self.batch["asym_id"].squeeze(0)
        return [asym_ids[i].item() for i in range(len(asym_ids)) if mask[i]]

    def get_hard_res_type(self):
        result = torch.nn.functional.one_hot(
            torch.argmax(self.get_res_type(
                self.designed_soft_sequence,
                default_for_unused_tokens=self.designed_soft_sequence.min() - 1
            ), dim=-1),
            num_classes=const.num_tokens,
        ).float()
        assert result.shape == self.res_type_from_initial_batch.shape, (
            f"result.shape: {result.shape}, self.res_type_from_initial_batch.shape: {self.res_type_from_initial_batch.shape}"
        )
        return result

    def get_batch(self, res_type, design_only=False):
        assert res_type.shape == self.res_type_from_initial_batch.shape, (
            f"res_type.shape: {res_type.shape}, self.res_type_from_initial_batch.shape: {self.res_type_from_initial_batch.shape}"
        )

        result = dict(self.batch)
        result["res_type"] = res_type

        if design_only:
            result["token_pad_mask"] = (
                self.batch["token_pad_mask"].bool() & self.design_mask
            ).float()

        self.update_features(
            batch=result,
            update_atom_features=self.config.update_atom_features,
        )
        return result

    def get_hard_sequences(self, batch=None, designed_residues_in_lowercase=False):
        if batch is None:
            batch = self.batch
        hard_res_types = torch.argmax(
            self.get_res_type(
                self.designed_soft_sequence,
                default_for_unused_tokens=self.designed_soft_sequence.min() - 1
            ), dim=-1
        ).squeeze(0)
        result = collections.defaultdict(list)
        token_pad_mask = batch["token_pad_mask"].squeeze(0)
        asym_ids = batch["asym_id"].squeeze(0)
        design_mask = self.design_mask.squeeze(0)
        for i in range(len(hard_res_types)):
            if token_pad_mask[i]:
                letter = const.prot_token_to_letter.get(
                    const.tokens[hard_res_types[i]], f"[{const.tokens[hard_res_types[i]]}]")
                if designed_residues_in_lowercase and design_mask[i]:
                    letter = letter.lower()
                result[asym_ids[i].item()].append(letter)
        return {k: "".join(v) for k, v in result.items()}
    
    def get_hard_designed_sequence_string(self):
        with torch.no_grad():
            argmax_sequence = torch.argmax(
                self.designed_soft_sequence, dim=-1
            ).squeeze()
            argmax_sequence_as_string = "".join(
                const.prot_token_to_letter[self.allowed_designed_tokens[i]]
                for i in argmax_sequence
            )
        return argmax_sequence_as_string

    def get_res_type(self, designed_amino_acid_soft_sequence, default_for_unused_tokens=0.0):
        result = self.res_type_from_initial_batch.clone()
        assert result.shape[0] == 1
        result[:, self.design_mask.squeeze(0)] = default_for_unused_tokens
        design_positions = self.design_mask.squeeze(0).nonzero(as_tuple=False).flatten()
        pos_indices, token_indices = torch.meshgrid(
            design_positions, self.allowed_designed_token_ids, indexing="ij"
        )
        result[0, pos_indices, token_indices] = (
            designed_amino_acid_soft_sequence.squeeze(0)
        )
        assert torch.allclose(
            result[self.design_mask][:, self.allowed_designed_token_ids],
            designed_amino_acid_soft_sequence.squeeze(0),
        )
        assert result.shape == self.res_type_from_initial_batch.shape, (
            f"result.shape: {result.shape}, self.res_type_from_initial_batch.shape: {self.res_type_from_initial_batch.shape}"
        )
        return result

    def summarize_features(self, batch=None):
        chain_sequence_strings = self.get_hard_sequences(batch=batch, designed_residues_in_lowercase=True)
        result = f"Chain sequences (lowercase indicates designed residues):\n{chain_sequence_strings}"
        return result

    def configure_optimizers(self, lr=None, weight_decay=0.0):
        if lr is None:
            lr = self.config.default_lr
        self.optimizer = torch.optim.SGD(
            [self.designed_soft_sequence], lr=lr, weight_decay=weight_decay
        )
        return self.optimizer
    
    def reset_for_new_attempt(self):
        #self.trajectories = []  # debug memory leak
        self.hard_predicted_structures = collections.defaultdict(list)  # keyed by hard design sequence
        self.trajectories.append(collections.defaultdict(list))
        self.best_design = None
        self.last_transform = None

        initial_designed_soft_sequence = self.res_type_from_initial_batch[
            :,
            self.design_mask.squeeze(0),
        ][:, :, self.allowed_designed_token_ids].clone()

        # Set initial design sequence
        if self.config.initial_design_randomization == "full":
            # Fully random amino acids for designed residues.
            initial_designed_soft_sequence = (
                torch.distributions.Gumbel(0, 1)
                .sample(initial_designed_soft_sequence.shape)
                .to(self.device))
        elif self.config.initial_design_randomization == "none":
            pass
        else:
            raise ValueError(f"Invalid initial_design_randomization: {self.config.initial_design_randomization}")

        self.designed_soft_sequence = torch.nn.Parameter(initial_designed_soft_sequence, requires_grad=True)
        self.configure_optimizers()

    
    def optimize(self, quiet=False, max_aborts=1000):
        num_aborts = 0
        while num_aborts < max_aborts:
            print(f"Optimizing attempt #{num_aborts+1}")
            success = True
            for stage_num, stage_dict in enumerate(self.config.optimization_stages):
                stage_dict = dict(stage_dict)
                if stage_dict.get("steps", 1) > 0:
                    protocol = stage_dict.pop("protocol")
                    if not quiet:
                        print(f"Optimizing stage #{stage_num} ({protocol})")
                    try:
                        self.optimize_stage(protocol, stage_num, stage_dict)
                    except AbortDesign as e:
                        print(f"Aborting at stage #{stage_num} ({protocol}) because {e}")
                        num_aborts += 1
                        self.reset_for_new_attempt()
                        success = False
                        break
                    if not quiet:
                        print(f"Finished optimizing stage #{stage_num} ({protocol})")
                        print(self.summarize_features())
                        print(f"Loss: {self.trajectories[-1]['loss'][-1]}")
            
            if success:
                break

        # Assign the best design to the current sequence.
        if self.best_design is None:
            print("No best design found.")
        else:
            with torch.no_grad():
                self.designed_soft_sequence[:] = self.best_design.designed_one_hot_sequence.detach()

        return self.best_design

    def optimize_protocol_warm_up(self, steps, lr_decay=1.0):
        (param_group,) = self.optimizer.param_groups
        for step in range(steps):
            self.new_trajectory_step()
            param_group["lr"] *= lr_decay
            yield {
                "transform": lambda logits: torch.softmax(logits, dim=-1),
                "lr": param_group["lr"],
                "step": step,
                "do_backward": True,
            }

    def optimize_protocol_linear_combination(
        self, steps, temperature=1.0, lr_decay=1.0
    ):
        # initialize from softmax
        with torch.no_grad():
            self.designed_soft_sequence[:] = torch.softmax(
                self.designed_soft_sequence, dim=-1
            ).detach()
        (param_group,) = self.optimizer.param_groups
        for step in range(steps):
            self.new_trajectory_step()
            lambda_value = (step + 1) / steps
            param_group["lr"] *= lr_decay
            yield {
                "transform": lambda logits: (
                    (1 - lambda_value) * logits + (lambda_value) * torch.softmax(logits / temperature, dim=-1)
                ),
                "lr": param_group["lr"],
                "lambda": lambda_value,
                "step": step,
                "do_backward": True,
            }

    def optimize_protocol_annealing(self, steps, lr_decay=1.0):
        (param_group,) = self.optimizer.param_groups
        initial_lr = param_group["lr"]
        for step in range(steps):
            self.new_trajectory_step()
            temperature = 1e-2 + (1 - 1e-2) * (1 - (step + 1) / steps) ** 2
            if lr_decay == "temperature":
                param_group["lr"] = initial_lr * temperature
            else:
                param_group["lr"] *= lr_decay
            yield {
                "transform": lambda logits: torch.nn.functional.softmax(logits / temperature, dim=-1),
                "lr": param_group["lr"],
                "step": step,
                "do_backward": True,
                "temperature": temperature,
            }

    def optimize_protocol_one_hot(self, steps):
        # initialize from one-hot
        with torch.no_grad():
            hard = torch.nn.functional.one_hot(
                torch.argmax(self.designed_soft_sequence, dim=-1),
                num_classes=self.designed_soft_sequence.shape[-1],
            ).float()
            self.designed_soft_sequence[:] = hard.detach()

        for step in range(steps):
            self.new_trajectory_step()
            yield {
                "transform": lambda logits: (
                    torch.nn.functional.one_hot(
                        torch.argmax(logits, dim=-1),
                        num_classes=logits.shape[-1]
                    ).float() - logits.detach() + logits
                ),
                "step": step,
                "do_backward": True,
            }

    def optimize_protocol_semigreedy(
        self,
        steps,
        num_tries=10,
        improvement_to_immediately_accept=1000,
        mutation_bias=None,
        predict_args={}
    ):
        if mutation_bias is None:
            mutation_bias = {}
        
        mutation_bias_requires_gradient = mutation_bias.get("requires_gradient", False)
        mutation_bias_expression = mutation_bias.get("expression", "plddt")
        mutation_bias_temperature = mutation_bias.get("temperature", 0.001)

        with torch.no_grad():
            if self.best_design is not None:
                print(
                    f"Initializing semigreedy from best design: {self.best_design}"
                )
                self.designed_soft_sequence[:] = (
                    self.best_design.designed_one_hot_sequence.detach()
                )
            else:
                print("Initializing semigreedy from previous design")
                hard = torch.nn.functional.one_hot(
                    torch.argmax(self.designed_soft_sequence, dim=-1),
                    num_classes=self.designed_soft_sequence.shape[-1],
                ).float()
                self.designed_soft_sequence[:] = hard.detach()

        for step in range(steps):
            logits = self.designed_soft_sequence.clone()
                
            if mutation_bias_requires_gradient:
                # Hard but with gradient flow
                hard = torch.nn.functional.one_hot(
                    torch.argmax(logits, dim=-1),
                    num_classes=logits.shape[-1]
                ).float() - logits.detach() + logits

                self.optimizer.zero_grad()
                prediction = self.forward(
                    res_type=self.get_res_type(hard),
                    return_batch=True,
                    return_raw_prediction=True)
                expression_value = evaluate_expression(
                    mutation_bias_expression,
                    {
                        "iptm": torch.mean(prediction["raw_prediction"]["iptm"]),
                        "ptm": prediction["raw_prediction"]["ptm"],
                    },
                    include_torch_functions=True)
                expression_value.backward()
                grad = self.designed_soft_sequence.grad
                mutation_raw_probability_logits = grad.squeeze(0).clone()
            else:
                # Hard, no gradient needed
                hard = torch.nn.functional.one_hot(
                    torch.argmax(logits, dim=-1), num_classes=logits.shape[-1]).float()
                prediction = self.forward(
                    res_type=self.get_res_type(hard),
                    return_batch=True,
                    return_raw_prediction=True)
                if mutation_bias_expression == "plddt":
                    mutation_raw_probability_logits = (1 - prediction["plddt"])[
                        self.design_mask
                    ].unsqueeze(-1).broadcast_to((-1, self.designed_soft_sequence.shape[-1])).clone()
                elif mutation_bias_expression == "uniform":
                    mutation_raw_probability_logits = torch.ones_like(logits).squeeze(0)
                else:
                    raise ValueError(f"Unsupported mutation bias: {mutation_bias_expression}")

            starting_coords = prediction["structure"].atoms["coords"]
            starting_rep_atom_indices = torch.nonzero(prediction["batch"]["token_to_rep_atom"])[:,-1].cpu().numpy()
            starting_rep_atom_coords = starting_coords[starting_rep_atom_indices]

            current_design_record = DesignRecord(
                    hard_ptm=prediction["ptm"],
                    hard_iptm=prediction["iptm"],
                    loss=None,
                    step=None,
                    stage_num=None,
                    protocol=None,
                    argmax_sequence=None,
                    designed_one_hot_sequence=hard.clone().detach(),
                    affinity_value=prediction["affinity_pred_value"],
                    affinity_probability=prediction["affinity_probability_binary"],
                )
            current_quality = current_design_record.evaluate_expression(
                self.config.final_design_selection_criteria
            )

            best_logits = logits.clone()

            soft_sequences_to_try = []
            pbar = tqdm(range(num_tries), desc="Trying sequences")
            best_quality = current_quality
            num_improved = 0
            improvement_description = f"{current_quality:.3f}"
            mutation_raw_probability_logits += logits.detach().squeeze() * -1000  # don't pick the existing aa
            for i in pbar:
                new_logits = logits.clone()

                mutation_raw_probability_logits_flat = mutation_raw_probability_logits.view(-1)
                mutation_probabilities = torch.softmax(
                    mutation_raw_probability_logits_flat / mutation_bias_temperature, dim=0).view(
                        mutation_raw_probability_logits.shape)
                mutation_probabilities_flat = mutation_probabilities.view(-1).cpu().numpy()

                sampled_pos_flat = np.random.choice(
                    np.arange(len(mutation_probabilities_flat)),
                    p=mutation_probabilities_flat
                )
                sampled_pos = sampled_pos_flat // mutation_probabilities.shape[-1]
                sampled_aa = sampled_pos_flat % mutation_probabilities.shape[-1]

                new_logits[:, sampled_pos, :] = 0.0
                new_logits[:, sampled_pos, sampled_aa] = 1.0
                soft_sequences_to_try.append(new_logits)

                new_hard = torch.nn.functional.one_hot(
                    torch.argmax(new_logits, dim=-1), num_classes=new_logits.shape[-1]
                ).float()

                with torch.no_grad():
                    new_prediction = self.forward(
                        res_type=self.get_res_type(new_hard),
                        return_batch=True,
                        return_raw_prediction=True)

                # Compute rmsd vs current prediction
                new_coords = new_prediction["structure"].atoms["coords"]
                new_rep_atom_indices = torch.nonzero(new_prediction["batch"]["token_to_rep_atom"])[:,-1].cpu().numpy()
                new_rep_atom_coords = new_coords[new_rep_atom_indices]
                rmsd = compute_rmsd(
                    torch.tensor(new_rep_atom_coords.copy()).unsqueeze(0),
                    torch.tensor(starting_rep_atom_coords.copy()).unsqueeze(0)).item()

                new_design_record = DesignRecord(
                    hard_ptm=new_prediction["ptm"],
                    hard_iptm=new_prediction["iptm"],
                    loss=None,
                    step=None,
                    stage_num=None,
                    protocol=None,
                    argmax_sequence=None,
                    designed_one_hot_sequence=new_hard.clone().detach(),
                    affinity_value=new_prediction["affinity_pred_value"],
                    affinity_probability=new_prediction["affinity_probability_binary"],
                )
                quality = new_design_record.evaluate_expression(
                    self.config.final_design_selection_criteria
                )

                if new_design_record.is_better_than(current_design_record, criteria=self.config.final_design_selection_criteria):
                    num_improved += 1
                    current_design_record = new_design_record
                    best_quality = quality
                    best_logits = new_logits
                    prediction = new_prediction
                    improvement_description = (
                        f"{current_quality:.3f} -> {best_quality:.3f}"
                    )

                pbar.set_postfix(
                    {
                        f"{self.config.final_design_selection_criteria} (final metric)": quality,
                        "ptm": new_prediction["ptm"],
                        "iptm": new_prediction["iptm"],
                        "num_improved": num_improved,
                        "best": improvement_description,
                        "rmsd": rmsd,
                    }
                )

                if quality - current_quality > improvement_to_immediately_accept:
                    print(
                        f"Improved by more than {improvement_to_immediately_accept}, accepting immediately."
                    )
                    break

            with torch.no_grad():
                self.designed_soft_sequence[:] = best_logits.detach()

            if num_improved == 0:
                print("No improvement, stopping.")
                break
            else:
                print(f"Found {num_improved} improvements, continuing with best.")

            yield {
                "transform": lambda logits: torch.nn.functional.one_hot(
                    torch.argmax(logits, dim=-1),
                    num_classes=logits.shape[-1],
                ).float(),
                "do_backward": False,
                "step": step,
                "semigreedy_fraction_improved": num_improved / num_tries,
                "semigreedy_best_quality": best_quality,
                "semigreedy_num_tries": num_tries,
                "semigreedy_num_actual_tries": i,
                "semigreedy_num_improved": num_improved,
                "semigreedy_starting_quality": current_quality,
            }

    def optimize_protocol_collect_stats(self, steps, rmsd_threshold_to_abort=None, do_soft_prediction=True):
        # No-op protocol that just allows the structure predictors to run and stats to be computed.
        for step in range(steps):
            yield {
                "do_backward": False,
                "step": step,
                "transform": self.last_transform if do_soft_prediction else None
            }

        hard_sequence_string = self.get_hard_designed_sequence_string()
        hard_predictions = self.hard_predicted_structures.get(hard_sequence_string, [])
        if len(hard_predictions) > 1:
            # Compute RMSD matrix across all structures
            rmsd_matrix = np.zeros((len(hard_predictions), len(hard_predictions))) * np.nan
            for i in range(len(hard_predictions)):
                for j in range(len(hard_predictions)):
                    rmsd_matrix[i, j] = compute_rmsd(
                        torch.tensor(hard_predictions[i].atoms["coords"].copy()).unsqueeze(0),
                        torch.tensor(hard_predictions[j].atoms["coords"].copy()).unsqueeze(0)
                    )
            print(f"RMSD matrix (all atom) for hard predictions using designed sequence {hard_sequence_string}")
            # Display it to two decimal places
            print(np.round(rmsd_matrix, 2))
            self.log_trajectory_item("hard_rmsd_matrix", rmsd_matrix)
            self.log_trajectory_item("hard_rmsd_matrix_max", np.max(rmsd_matrix))
            if rmsd_threshold_to_abort is not None and np.max(rmsd_matrix) > rmsd_threshold_to_abort:
                message = f"RMSD threshold {rmsd_threshold_to_abort} exceeded (max was {np.max(rmsd_matrix):.2f})"
                self.log_trajectory_item("abort_reason", message)
                raise AbortDesign(message)

    def log_trajectory_item(self, key, value):
        value = tree_map(lambda x: x.detach().cpu().numpy() if isinstance(x, torch.Tensor) else x, value)
        current_trajectory = self.trajectories[-1]
        length = max(len(v) for v in current_trajectory.values()) if current_trajectory else 0
        if length == 0:
            current_trajectory[key] = [value]
        else:
            if len(current_trajectory[key]) < length:
                current_trajectory[key].extend([None] * (length - len(current_trajectory[key])))
            assert len(current_trajectory[key]) == length
            current_trajectory[key][-1] = value

    def new_trajectory_step(self):
        for key in self.trajectories[-1]:
            self.trajectories[-1][key].append(None)

    def get_current_trajectory_step_items(self):
        return frozendict({k: v[-1] for k, v in self.trajectories[-1].items() if len(v) > 0})

    def emit_design(self, record):
        sequence = record.argmax_sequence.upper()
        if sequence not in self.saved_design_sequences:
            if self.save_design_callback is not None:
                self.save_design_callback(record)
            self.saved_design_sequences.add(sequence)

    def optimize_stage(self, protocol, stage_num, stage_dict):
        stage_dict = dict(stage_dict)
        candidate_final_design = stage_dict.pop("candidate_final_design")
        include_target = stage_dict.pop("include_target")
        soft_prediction_requires_structure = stage_dict.pop("soft_prediction_requires_structure", True)
        hard_prediction_every_n_steps = stage_dict.pop("hard_prediction_every_n_steps", 0)
        abort_if = stage_dict.pop("abort_if", None)
        hard_predict_args = stage_dict.pop("hard_predict_args", {})

        weight_decay = stage_dict.pop("weight_decay", 0.0)
        max_consecutive_steps_with_no_mutations = stage_dict.pop(
            "max_consecutive_steps_with_no_mutations",
            self.config.max_consecutive_steps_with_no_mutations,
        )
        lr = stage_dict.pop("lr", self.config.default_lr)
        self.configure_optimizers(lr=lr, weight_decay=weight_decay)

        protocol_implementations = {
            "warm_up": self.optimize_protocol_warm_up,
            "linear_combination": self.optimize_protocol_linear_combination,
            "annealing": self.optimize_protocol_annealing,
            "one_hot": self.optimize_protocol_one_hot,
            "semigreedy": self.optimize_protocol_semigreedy,
            "collect_stats": self.optimize_protocol_collect_stats,
        }
        assert protocol in protocol_implementations, (
            f"Invalid protocol: {protocol}. Options are: {list(protocol_implementations.keys())}"
        )

        wandb.config.update(
            {
                f"{self.design_prefix}/stage_{stage_num}_protocol": protocol,
                f"{self.design_prefix}/stage_{stage_num}_steps": stage_dict.get("steps"),
                f"{self.design_prefix}/stage_{stage_num}_include_target": include_target,
                f"{self.design_prefix}/stage_{stage_num}_candidate_final_design": candidate_final_design,
            }
        )

        argmax_sequence_as_string = self.get_hard_designed_sequence_string()

        iterator = protocol_implementations[protocol](**stage_dict)
        consecutive_steps_with_no_mutations = 0
        pbar = tqdm(enumerate(iterator), total=stage_dict["steps"], desc=protocol)
        
        for step, item in pbar:
            item["protocol"] = protocol
            self.last_transform = item.pop("transform")
            do_backward = item.pop("do_backward")

            transformed_res_type = None
            if self.last_transform is not None:
                transformed_res_type = self.get_res_type(self.last_transform(self.designed_soft_sequence))

            do_soft_prediction = transformed_res_type is not None
            do_hard_prediction = hard_prediction_every_n_steps > 0 and step % hard_prediction_every_n_steps == 0
            hard_res_type = self.get_hard_res_type()
            
            self.optimizer.zero_grad()

            soft_prediction = None
            prediction_for_loss_computation = None
            hard_soft_res_type_diff = None
            if do_soft_prediction:
                soft_forward_time = time.time()
                soft_prediction = self.forward(
                    res_type=transformed_res_type,
                    design_only=not include_target,
                    return_batch=True,
                    requires_structure=soft_prediction_requires_structure,
                )
                soft_forward_time = time.time() - soft_forward_time
                self.log_trajectory_item("soft_forward_time", soft_forward_time)
                prediction_for_loss_computation = soft_prediction

                # Difference between hard and soft res_type (logged in progress bar)
                hard_soft_res_type_diff = torch.max(torch.abs(transformed_res_type - hard_res_type)).item()
            
            hard_prediction = None  # prediction using hard (one hot) res type
            if do_hard_prediction:
                # Shortcut if the soft res_type is actually already hard.
                if do_soft_prediction and hard_soft_res_type_diff == 0.0 and soft_prediction_requires_structure:
                    hard_prediction = soft_prediction
                else:
                    hard_forward_time = time.time()
                    with torch.no_grad():
                        hard_prediction = self.forward(
                            res_type=hard_res_type,
                            return_batch=True,
                            **hard_predict_args,
                        )
                    hard_forward_time = time.time() - hard_forward_time
                    self.log_trajectory_item("hard_forward_time", hard_forward_time)

                if prediction_for_loss_computation is None:
                    prediction_for_loss_computation = hard_prediction

            # Compute loss using HallucinationLoss
            loss_info = {}
            if prediction_for_loss_computation is None:
                loss = None
            else:
                loss = self.loss.compute_loss(
                    prediction_for_loss_computation["batch"],
                    prediction_for_loss_computation,
                    design_mask=self.design_mask,
                    include_target=include_target,
                    loss_info=loss_info,
                )
                if torch.isnan(loss):
                    print("NaN loss, stopping.")
                    break

                # Run backward only if requires grad.
                if do_backward:
                    backward_time = time.time()
                    loss.backward()
                    backward_time = time.time() - backward_time
                    self.log_trajectory_item("backward_time", backward_time)
                self.log_trajectory_item("loss", loss.item())

            argmax_sequence_as_string = self.get_hard_designed_sequence_string()

            # Compute additional metrics with detached tensors
            with torch.no_grad():
                token_pad_mask = prediction_for_loss_computation["batch"]["token_pad_mask"].squeeze()
                token_pad_mask_pairwise = (
                    token_pad_mask.unsqueeze(0).bool()
                    & token_pad_mask.unsqueeze(1).bool()
                ).unsqueeze(0)

                entropy = None
                predicted_distances = None
                if soft_prediction is not None:
                    entropy = distogram_entropy(
                        soft_prediction["pdistogram"].detach(),
                        threshold_angstroms=1e3,
                        pdistogram_mask=token_pad_mask_pairwise,
                    )
                    predicted_distances = predicted_distance(
                        soft_prediction["batch"], soft_prediction, na_value=torch.nan
                )

            # Track mutations
            num_mutations = 0
            sequence_with_mutations_in_uppercase = argmax_sequence_as_string.lower()
            prev_sequences = [
                seq.upper() for seq in self.trajectories[-1].get("sequence", [])
                if seq is not None
            ]
            if len(prev_sequences) > 0:
                prev_seq = prev_sequences[-1]
                curr_seq = argmax_sequence_as_string.upper()
                sequence_with_mutations_in_uppercase = mutations_in_uppercase(
                    prev_seq, curr_seq
                )
                num_mutations = sum(1 for a, b in zip(prev_seq, curr_seq) if a != b)

                if num_mutations == 0:
                    consecutive_steps_with_no_mutations += 1
                else:
                    consecutive_steps_with_no_mutations = 0

            # Update progress bar
            pbar_postfix = {"loss": f"{loss.item():.4f}", "nmut": num_mutations}
            pbar_postfix["hd_sft_diff"] = hard_soft_res_type_diff

            # Log to wandb
            if self.table is not None:
                self.table.add_data(
                    protocol, step, sequence_with_mutations_in_uppercase, num_mutations
                )

            print(sequence_with_mutations_in_uppercase)

            self.log_trajectory_item("include_target", include_target)
            self.log_trajectory_item("candidate_final_design", candidate_final_design)
            self.log_trajectory_item("iterator_parameters", dict(item))
            self.log_trajectory_item("num_mutations", num_mutations)
            self.log_trajectory_item("current_step", step)
            self.log_trajectory_item("total_steps", stage_dict["steps"])
            self.log_trajectory_item("temperature", item.get("temperature", None))
            self.log_trajectory_item("lr", item.get("lr", None))
            self.log_trajectory_item("sequence", sequence_with_mutations_in_uppercase)
            self.log_trajectory_item("protocol", protocol)
            self.log_trajectory_item("stage", f"{stage_num}_{protocol}")
            if entropy is not None:
                self.log_trajectory_item("entropy", entropy.squeeze().detach().cpu().numpy())
            if predicted_distances is not None:
                self.log_trajectory_item("predicted_distances", (
                    predicted_distances.squeeze().detach().cpu().numpy()
                ))
            self.log_trajectory_item("designed_soft_sequence_max", torch.max(self.designed_soft_sequence).item())
            self.log_trajectory_item("designed_soft_sequence_min", torch.min(self.designed_soft_sequence).item())
            self.log_trajectory_item("designed_soft_sequence_mean", torch.mean(self.designed_soft_sequence).item())
            self.log_trajectory_item("designed_soft_sequence_norm", torch.norm(self.designed_soft_sequence).item())
            
            if transformed_res_type is not None:
                self.log_trajectory_item("transformed_res_type_max", torch.max(transformed_res_type).item())
                self.log_trajectory_item("transformed_res_type_min", torch.min(transformed_res_type).item())
                self.log_trajectory_item("transformed_res_type_mean", torch.mean(transformed_res_type).item())
                self.log_trajectory_item("transformed_res_type_norm", torch.norm(transformed_res_type).item())
            
            if self.designed_soft_sequence.grad is not None:
                self.log_trajectory_item("gradient_max", torch.max(self.designed_soft_sequence.grad).item())
                self.log_trajectory_item("gradient_min", torch.min(self.designed_soft_sequence.grad).item())
                self.log_trajectory_item("gradient_mean", torch.mean(self.designed_soft_sequence.grad).item())
                self.log_trajectory_item("gradient_norm", torch.norm(self.designed_soft_sequence.grad).item())
            
            self.log_trajectory_item("time", time.time())
            self.log_trajectory_item("loss_info", loss_info)

            # Process hard prediction
            hard_ptm = None
            hard_iptm = None
            affinity_pred_value = None
            affinity_probability_binary = None
            structure_pdb = None
            if do_hard_prediction:
                structure_pdb = to_pdb(hard_prediction["structure"])
                self.hard_predicted_structures[argmax_sequence_as_string].append(
                    hard_prediction["structure"])
                self.log_trajectory_item("structure_pdb", structure_pdb)
                hard_ptm = hard_prediction["ptm"]
                hard_iptm = hard_prediction["iptm"]
                affinity_pred_value = hard_prediction["affinity_pred_value"]
                affinity_probability_binary = hard_prediction["affinity_probability_binary"]
                pbar_postfix["ptm"] = hard_ptm
                pbar_postfix["iptm"] = hard_iptm
                
                if affinity_pred_value is not None:
                    pbar_postfix["aff_v"] = affinity_pred_value
                    pbar_postfix["aff_p"] = affinity_probability_binary

                for k, v in hard_prediction.items():
                    if k not in ["batch", "structure", "pdistogram"]:
                        self.log_trajectory_item(f"hard_{k}", v)

                # Compute RMSD between soft and hard prediction
                if do_soft_prediction and soft_prediction_requires_structure and hard_prediction is not soft_prediction:
                    hard_prediction_coords = hard_prediction["structure"].atoms["coords"]
                    soft_prediction_coords = soft_prediction["structure"].atoms["coords"]
                    rep_atom_indices = torch.nonzero(hard_prediction["batch"]["token_to_rep_atom"])[:,-1].cpu().numpy()
                    hard_prediction_rep_atom_coords = hard_prediction_coords[rep_atom_indices]
                    soft_prediction_rep_atom_coords = soft_prediction_coords[rep_atom_indices]
                    rmsd = compute_rmsd(
                        torch.tensor(hard_prediction_rep_atom_coords.copy()).unsqueeze(0),
                        torch.tensor(soft_prediction_rep_atom_coords.copy()).unsqueeze(0)).item()
                    self.log_trajectory_item("rmsd_hard_v_soft", rmsd)
                    pbar_postfix["hd_vs_sft_rmsd"] = rmsd

            if candidate_final_design:
                assert include_target, "candidate_final_design requires include_target"

            record = DesignRecord(
                hard_ptm=hard_ptm,
                hard_iptm=hard_iptm,
                loss=loss.item() if loss is not None else None,
                step=step,
                stage_num=stage_num,
                protocol=protocol,
                argmax_sequence=argmax_sequence_as_string if self.best_design is None else mutations_in_uppercase(
                    self.best_design.argmax_sequence, argmax_sequence_as_string
                ),
                designed_one_hot_sequence=torch.nn.functional.one_hot(
                    torch.argmax(self.designed_soft_sequence, dim=-1),
                    num_classes=self.designed_soft_sequence.shape[-1],
                ).float().clone(),
                affinity_value=affinity_pred_value,
                affinity_probability=affinity_probability_binary,
            )

            new_best = False
            if candidate_final_design and do_hard_prediction:
                self.log_trajectory_item("final_design_criteria_value", record.evaluate_expression(self.config.final_design_selection_criteria))
                if record.is_better_than(self.best_design, criteria=self.config.final_design_selection_criteria):
                    self.best_design = record
                    print(
                        f"New best design "
                        f"[{self.config.final_design_selection_criteria}={self.best_design.evaluate_expression(self.config.final_design_selection_criteria)}]: "
                        f"{self.best_design}"
                    )
                    new_best = True
                    self.emit_design(record)

            self.log_trajectory_item("new_best", new_best)

            abort_exception = None
            if abort_if is not None:
                abort_if_value = record.evaluate_expression(abort_if)
                if abort_if_value:
                    abort_message = f"{abort_if} = {abort_if_value} for {record}"
                    abort_exception = AbortDesign(abort_message)
                    self.log_trajectory_item("abort_reason", abort_message)

            # Log to wandb with design prefix
            wandb_row = dict(self.get_current_trajectory_step_items())
            exclude_from_wandb = [
                "entropy",
                "predicted_distances",
                "protocol",
                "sequence",
                "include_target",
                "structure_pdb",
            ]
            for k in exclude_from_wandb:
                if k in wandb_row:
                    del wandb_row[k]

            # Add design prefix to all wandb metrics
            if self.design_prefix:
                wandb_row = {
                    f"{self.design_prefix}/optimize/{k}": v
                    for k, v in wandb_row.items()
                }
            else:
                wandb_row = {f"optimize/{k}": v for k, v in wandb_row.items()}
            wandb.log(wandb_row)

            if abort_exception is not None:
                raise abort_exception

            if (
                consecutive_steps_with_no_mutations
                >= max_consecutive_steps_with_no_mutations
            ):
                print(
                    f"No mutations for {consecutive_steps_with_no_mutations} steps, stopping."
                )
                break

            pbar.set_postfix(pbar_postfix)

            if do_backward:
                self.optimizer.step()

    def forward(
            self,
            res_type=None,
            requires_structure=True,
            return_batch=False,
            return_raw_prediction=False,
            design_only=False,
            recycling_steps=None,
            num_sampling_steps=None,
            diffusion_samples=None):
        if recycling_steps is None:
            recycling_steps = self.boltz_model.predict_args["recycling_steps"]
        if num_sampling_steps is None:
            num_sampling_steps = self.boltz_model.predict_args["sampling_steps"]
        if diffusion_samples is None:
            diffusion_samples = self.boltz_model.predict_args["diffusion_samples"]

        # Forward pass on hard features, including structure model.
        result = {}
        if res_type is None:
            res_type = self.get_hard_res_type()
        batch = self.get_batch(res_type=res_type, design_only=design_only)

        if return_batch:
            result["batch"] = {
                k: v.detach() if torch.is_tensor(v) else v for k, v in batch.items()
            }
            
        prev_value_skip_run_structure = self.boltz_model.skip_run_structure
        prev_value_confidence_to_trunk_gradients = self.boltz_model.confidence_to_trunk_gradients
        self.boltz_model.skip_run_structure = not requires_structure
        self.boltz_model.confidence_to_trunk_gradients = True
        prediction_result = self.boltz_model(
            batch,
            recycling_steps=recycling_steps,
            num_sampling_steps=num_sampling_steps,
            diffusion_samples=diffusion_samples,
            run_confidence_sequentially=True,
            step_scale=self.boltz_model.structure_module.step_scale,
            noise_scale=self.boltz_model.structure_module.noise_scale,
            return_z_feats=False,
        )
        self.boltz_model.skip_run_structure = prev_value_skip_run_structure
        self.boltz_model.confidence_to_trunk_gradients = prev_value_confidence_to_trunk_gradients

        if return_raw_prediction:
            result["raw_prediction"] = prediction_result

        (ptm,) = prediction_result["ptm"]
        (iptm,) = prediction_result["iptm"]
        pair_chains_iptm = prediction_result["pair_chains_iptm"]

        result["ptm"] = float(ptm)
        result["iptm"] = float(iptm)
        result["plddt"] = prediction_result["plddt"].detach()
        result["pdistogram"] = prediction_result["pdistogram"]
        result["affinity_pred_value"] = None
        result["affinity_probability_binary"] = None
        if "affinity_pred_value" in prediction_result:
            result["affinity_pred_value"] = float(prediction_result["affinity_pred_value"])
            result["affinity_probability_binary"] = float(prediction_result["affinity_probability_binary"])

        for asym_id1 in pair_chains_iptm.keys():
            for asym_id2 in pair_chains_iptm[asym_id1].keys():
                result[f"pair_chains_iptm_{asym_id1}_{asym_id2}"] = float(
                    pair_chains_iptm[asym_id1][asym_id2]
                )

        if requires_structure:
            pad_mask = batch["atom_pad_mask"].detach().bool().squeeze().cpu().numpy()
            predicted_coords = (
                prediction_result["sample_atom_coords"].detach().squeeze().cpu().numpy()
            )
            predicted_coords_unpad = predicted_coords[pad_mask]

            final_features = {
                k: v.squeeze(0) if isinstance(v, torch.Tensor) else v[0]
                for k, v in batch.items()
            }

            structure, designed_atoms, designed_residues = Structure.from_feat(
                final_features
            )
            structure = replace(
                structure,
                coords=np.array(
                    [
                        (predicted_coords_unpad[i],)
                        for i in range(len(predicted_coords_unpad))
                    ],
                    dtype=Coords,
                ),
            )
            structure.atoms["coords"] = predicted_coords_unpad
            structure.atoms["is_present"][:] = True
            result["structure"] = structure

        return result

    def log_summary_plots(self) -> None:
        """Log summary plots and data to wandb."""

        # Determine prefix for wandb logging
        prefix = f"{self.design_prefix}/" if self.design_prefix else ""

        # Log loss plot
        loss_fig = plot_loss(self)
        wandb.log({f"{prefix}summary/loss_plot": wandb.Image(loss_fig)})
        plt.close(loss_fig)

        # Log mutations plot
        mutations_fig = plot_mutations(self)
        wandb.log({f"{prefix}summary/mutations": wandb.Image(mutations_fig)})
        plt.close(mutations_fig)

        # Log sequence table if it exists
        if self.table is not None:
            table_key = f"{prefix}summary/sequence_table"
            wandb.log({table_key: self.table})

        # Log distogram animation
        distogram_animation = plot_distogram_animation(self)
        with tempfile.NamedTemporaryFile(suffix=".gif", delete=False) as f:
            distogram_animation.save(f.name, writer="pillow")
            wandb.log(
                {
                    f"{prefix}summary/distogram_animation": wandb.Video(
                        f.name,
                        format="gif",
                        caption=f"Distogram entropy animation {self.design_prefix}"
                        if self.design_prefix
                        else "Distogram entropy animation",
                    )
                }
            )

    def trajectory_info_as_df(self, include_large=False):
        
            
        exclude_keys = set()
        if not include_large:
            exclude_keys.update(
                [
                    "entropy",
                    "predicted_distances",
                    "intra_contact_entropy",
                    "inter_contact_entropy",
                    "structure_pdb",
                ]
            )

        records = []
        for attempt_num in range(len(self.trajectories)):
            attempt_trajectory = self.trajectories[attempt_num]
            num_steps = max(len(attempt_trajectory[k]) for k in attempt_trajectory)
            for step_num in range(num_steps):
                record = {
                    "attempt_num": attempt_num,
                    "step_num": step_num,
                }
                record.update({
                    k: v[step_num] for k, v in attempt_trajectory.items()
                    if k not in exclude_keys and len(v) > 0
                })
                record = {
                    k: tree_map(
                        lambda x: x.detach().cpu().numpy() if isinstance(x, torch.Tensor) else x,
                        v
                    )
                    for k, v in record.items()
                }
                records.append(record)

        df = pd.DataFrame(records)
        return df

    def update_features(
        self,
        batch: Dict,
        update_atom_features: bool = True,
        random: np.random.RandomState = np.random,
    ) -> Dict:
        """Update features based on current res_type."""
        res_type = batch["res_type"]
        res_type_hard = torch.argmax(res_type, dim=-1).squeeze()
        (structure,) = batch["structure"]
        (tokenized,) = batch["tokenized"]

        new_features = {}
        if update_atom_features:
            input_data = Input(
                tokens=tokenized.tokens,
                bonds=tokenized.bonds,
                token_to_res=tokenized.token_to_res,
                structure=structure,
                msa={},
                templates={},
                record=None,
            )
            ensemble_features = process_ensemble_features(
                data=input_data,
                random=random,
                num_ensembles=1,
                ensemble_sample_replacement=False,
                fix_single_ensemble=True,
            )
            atom_features = process_atom_features(
                data=input_data,
                molecules=self.molecules,
                ensemble_features=ensemble_features,
                res_type_override=res_type_hard.cpu().numpy(),
                canonical_atoms=self.canonical_atoms,
                random=random,
                atom14=False,
                atom14_geometric=False,
            )
            atom_features = collate([atom_features])
            new_features.update(atom_features)

        designed_residues_hard = torch.argmax(
            res_type[self.design_mask], dim=-1
        ).squeeze(0)

        # Set the one-row MSA to the current hard designed residues.
        batch["msa"][:, :, self.design_mask.squeeze(0)] = designed_residues_hard

        # Same for profile, but one hot instead of indices
        batch["profile"][:, self.design_mask.squeeze(0)] = torch.nn.functional.one_hot(
            designed_residues_hard,
            num_classes=const.num_tokens,
        ).float()

        # Update ccd feature based on residue names
        if "ccd" in batch:
            res_type_letters = [
                const.tokens[res_type_idx]
                for res_type_idx in designed_residues_hard.cpu().numpy()
            ]
            ccds = [convert_ccd(res_name) for res_name in res_type_letters]
            ccds = torch.tensor(ccds, dtype=torch.long).to(batch["res_type"].device)
            batch["ccd"][:, self.design_mask.squeeze(0)] = ccds

        # Update structure_bonds
        if "structure_bonds" in batch:
            original_structure, = batch["structure"]
            new_structure_bonds = batch["structure_bonds"][0].copy()
            token_to_first_atom = torch.argmax(new_features["atom_to_token"].float(), dim=1).squeeze()
            token_to_num_atoms = torch.sum(new_features["atom_to_token"].float(), dim=1).squeeze()

            token_bond_pairs = [(x[0].item(), x[1].item()) for x in list(zip(*torch.where(batch["token_bonds"].squeeze())))]

            def map_original_atom_index_to_current_index(original_atom_index):
                atom_token = self.initial_atom_to_token_map[original_atom_index].item()
                if token_to_num_atoms[atom_token] == 1:
                    return token_to_first_atom[atom_token]
                else:
                    return token_to_first_atom[atom_token] + self.canonical_atom_name_to_index_within_residue[
                        const.tokens[res_type_hard[atom_token]],
                        original_structure.atoms[original_atom_index]["name"]
                    ]
            
            for i in range(len(self.initial_structure_bonds)):
                row = self.initial_structure_bonds[i].copy()
                atom_1_token = self.initial_atom_to_token_map[row["atom_1"]].item()
                atom_2_token = self.initial_atom_to_token_map[row["atom_2"]].item()
                if tokenized.tokens[atom_1_token]["res_name"] != "CYS" or tokenized.tokens[atom_2_token]["res_name"] != "CYS":
                    # Skip disulfides for this check. They seem to not always show up in token_bonds.
                    if not batch["token_bonds"][0, atom_1_token, atom_2_token]:
                        import ipdb; ipdb.set_trace()

                    assert batch["token_bonds"][0, atom_1_token, atom_2_token], (
                        f"token_bonds inconsistent with structure_bonds: {row} ; "
                        f"token_bonds: {token_bond_pairs} ; "
                    )

                row["atom_1"] = map_original_atom_index_to_current_index(row["atom_1"])
                row["atom_2"] = map_original_atom_index_to_current_index(row["atom_2"])
                new_structure_bonds[i] = row

            batch["structure_bonds"] = [new_structure_bonds]

        # Add affinity related features
        batch["affinity_token_mask"] = (
            batch["mol_type"] == const.chain_type_ids["NONPOLYMER"]
        )
        batch["profile_affinity"] = batch["profile"].clone()
        batch["deletion_mean_affinity"] = batch["deletion_mean"].clone() * 5

        # Copy to device
        for key, value in list(new_features.items()):
            if isinstance(value, torch.Tensor):
                new_features[key] = value.to(batch["res_type"].device)

        batch.update(new_features)
        clean_batch_in_place(batch)
        return batch
    
    def __str__(self):
        return f"""BinderHallucination(
            loss={self.loss},
            optimization_stages={self.config.optimization_stages},
        )"""
