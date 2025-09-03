import os
from pathlib import Path
import pstats
import tempfile
import time
import torch
import numpy as np

from omegaconf import OmegaConf

import wandb
import yaml

import pandas as pd

import cProfile
import io
from pstats import SortKey

import tqdm
import gemmi
import gemmi.cif

from foldeverything.data.write.mmcif import to_mmcif
from foldeverything.model.loss.validation import compute_subset_rmsd

wandb.init(mode="disabled")

from scipy.stats import mannwhitneyu

from foldeverything.data.data import Input
from foldeverything.data.parse.schema import parse_yaml
from foldeverything.model.models.boltz import Boltz
from foldeverything.task.hallucination.binder_hallucinator import (
    BinderHallucination,
    BinderHallucinationConfig,
)
from foldeverything.task.hallucination.hallucination_task import get_atoms
from foldeverything.task.hallucination.loss import HallucinationLoss
from foldeverything.task.predict.data_ligands import DataConfig
from foldeverything.data.tokenize.af3 import AF3Tokenizer
from foldeverything.data.feature.af3 import AF3Featurizer
from foldeverything.task.predict.data_from_yaml import FromYamlDataModule, DataConfig
from foldeverything.task.predict.data_eval import EvalDataModule, DataConfig as EvalDataConfig
from foldeverything.data import const
from foldeverything.data.mol import load_canonicals, load_molecules
from foldeverything.task.predict.data_ligands import collate
from foldeverything.task.predict.predict import _load_from_checkpoint

MOLDIR = "/data/rbg/shared/projects/foldeverything/boltz2/ccd/mols"
CHECKPOINT = "/data/rbg/shared/projects/foldeverything/boltz2/boltz2_aff.ckpt"
CHECKPOINT_CONF = "/data/rbg/shared/projects/foldeverything/boltz2/boltz2_conf_final.ckpt"

def get_dummy_boltz_model(**kwargs):
    dummy_boltz_model = Boltz(
        atom_s=128,
        atom_z=16,
        token_s=384,
        token_z=128,
        num_bins=64,
        atom_feature_dim=388,
        alpha_pae=1.0,
        confidence_prediction=True,
        confidence_model_args=OmegaConf.create(
            {
                "confidence_args": OmegaConf.create({}),
                "pairformer_args": OmegaConf.create(
                    {
                        "num_blocks": 1,
                        "num_heads": 4,
                        "dropout": 0.0,
                        "post_layer_norm": False,
                        "activation_checkpointing": False,
                    }
                ),
            }
        ),
        training_args=OmegaConf.create(
            {
                "pairtoken_loss_weight": 0.0,
            }
        ),
        validation_args={},
        embedder_args={
            "atom_encoder_depth": 1,
            "atom_encoder_heads": 1,
        },
        msa_args={
            "msa_s": 64,
            "msa_blocks": 1,
            "msa_dropout": 0.0,
            "z_dropout": 0.0,
            "miniformer_blocks": True,
            "pairwise_head_width": 32,
            "pairwise_num_heads": 4,
            "use_paired_feature": True,
            "activation_checkpointing": False,
        },
        pairformer_args={
            "num_blocks": 1,
            "num_heads": 4,
            "dropout": 0.0,
            "post_layer_norm": False,
            "activation_checkpointing": False,
        },
        score_model_args={
            "sigma_data": 16,
            "dim_fourier": 256,
            "atom_encoder_depth": 1,
            "atom_encoder_heads": 1,
            "token_transformer_depth": 1,
            "token_transformer_heads": 2,
            "atom_decoder_depth": 1,
            "atom_decoder_heads": 1,
            "conditioning_transition_layers": 1,
            "transformer_post_ln": False,
            "activation_checkpointing": False,
        },
        diffusion_process_args={},
        diffusion_loss_args={},
        **kwargs,
    )
    return dummy_boltz_model


def get_real_boltz_model(max_tokens=100, recycling_steps=3, sampling_steps=200, diffusion_samples=1, checkpoint=CHECKPOINT):
    if not os.path.exists(checkpoint):
        print("WARNING: Checkpoint file not found: ", checkpoint)
        return None
    
    predict_args = {
        "recycling_steps": recycling_steps,
        "sampling_steps": sampling_steps,
        "diffusion_samples": diffusion_samples,
    }
    diffusion_process_args = {
        "sigma_min": 0.0001,  # min noise level
        "sigma_max": 160.0,  # max noise level
        "sigma_data": 16.0,  # standard deviation of data distribution
        "rho": 7,  # controls the sampling schedule
        "P_mean": -1.2,  # mean of log-normal distribution from which noise is drawn for training
        "P_std": 1.5,  # standard deviation of log-normal distribution from which noise is drawn for training
        "gamma_0": 0.8,
        "gamma_min": 1.0,
        "noise_scale": 1.003,
        "step_scale": 1.5,
        "mse_rotational_alignment": True,
        "coordinate_augmentation": True,
        "alignment_reverse_diff": True,
        "synchronize_sigmas": True,
    }
    msa_args = {
        'msa_s': 64,
        'msa_blocks': 4,
        'msa_dropout': 0.15,
        'z_dropout': 0.25,
        'miniformer_blocks': False,
        'pairwise_head_width': 32,
        'pairwise_num_heads': 4,
        'use_paired_feature': True,
        'activation_checkpointing': False,
        'use_trifast': True,
    }
    pairformer_args = {
        "activation_checkpointing": False,
        'num_blocks': 64,
        'num_heads': 16,
        'dropout': 0.25,
        'post_layer_norm': False,
        'use_trifast': True,
    }
    score_model_args = {
        'sigma_data': 16,
        'dim_fourier': 256,
        'atom_encoder_depth': 3,
        'atom_encoder_heads': 4,
        'token_transformer_depth': 24,
        'token_transformer_heads': 16,
        'atom_decoder_depth': 3,
        'atom_decoder_heads': 4,
        'conditioning_transition_layers': 2,
        'transformer_post_ln': False,
        'activation_checkpointing': False,
    }
    
    model_module = _load_from_checkpoint(
        Boltz,
        checkpoint,
        strict=False,
        use_ema=False,
        predict_args=predict_args,
        use_templates=True,
        max_seqs=1,
        max_tokens=max_tokens,
        batch_size=1,
        diffusion_process_args=diffusion_process_args,
        checkpoint_diffusion_conditioning=False,
        compile_structure=True,
        compile_pairformer=True,
        #msa_args=msa_args,
        #pairformer_args=pairformer_args,
        #score_model_args=score_model_args,
    )
    model_module.to(torch.device("cuda"))
    model_module.eval()
    #import ipdb; ipdb.set_trace()
    return model_module


def get_dummy_hallucinator(boltz_model, batch, extra_molecules=[], disallowed_amino_acids=[]):
    molecules = load_canonicals(MOLDIR)
    canonical_atoms = {
        token: get_atoms(token, molecules[token]) for token in const.canonical_tokens
    }
    print("Loading extra molecules: ", extra_molecules)
    molecules.update(load_molecules(MOLDIR, extra_molecules))
    result = BinderHallucination(
        boltz_model=boltz_model,
        initial_features=batch,
        config=BinderHallucinationConfig(
            loss=HallucinationLoss(terms=[]),
            update_atom_features=True,
            disallowed_amino_acids=disallowed_amino_acids,
            optimization_stages=[
                {
                    "protocol": "warm_up",
                    "steps": 2,
                    "include_target": False,
                },
                {
                    "protocol": "linear_combination",
                    "steps": 2,
                    "include_target": True,
                    "temperature": 1.0,
                },
                {
                    "protocol": "annealing",
                    "steps": 2,
                    "include_target": True,
                    "temperature_start": 1e-2,
                    "temperature_end": 1e-2,
                },
                {
                    "protocol": "one_hot",
                    "steps": 2,
                    "include_target": True,
                },
            ],
        ),
        molecules=molecules,
        canonical_atoms=canonical_atoms,
    )
    return result


def get_batch(yaml_path="tests/data/IAI.yaml"):
    data = FromYamlDataModule(
        cfg=DataConfig(
            tokenizer=AF3Tokenizer(atomize_modified_residues=False),
            featurizer=AF3Featurizer(),
            multiplicity=1,
            moldir=MOLDIR,
            yaml_path=yaml_path,
            backbone_only=False,
            atom14=False,
            atom14_geometric=False,
            atom37=False,
        ),
        batch_size=1,
        num_workers=0,
        pin_memory=True,
        extra_features=["structure", "tokenized"],
    )
    dataloader = data.predict_dataloader()
    batch = next(iter(dataloader))
    return batch


def test_featurization_IAI():
    batch = get_batch(yaml_path="tests/data/IAI.yaml")
    boltz_model = get_dummy_boltz_model()
    hallucinator = get_dummy_hallucinator(boltz_model, batch, extra_molecules=["IAI"])
    features = hallucinator.get_batch(res_type=hallucinator.get_hard_res_type())
    print(hallucinator.summarize_features(features))

    hard_sequences = hallucinator.get_hard_sequences()
    print(hard_sequences)

    yaml_input = {
        "sequences": [
            {
                "protein": {
                    "sequence": hard_sequences[0],
                    "id": "A",
                },
            },
            {
                "ligand": {
                    "id": "B",
                    "ccd": "IAI",
                },
            },
        ],
    }

    yaml_input_file = tempfile.NamedTemporaryFile(mode="w", delete=True, suffix=".yaml")
    yaml.dump(yaml_input, yaml_input_file)
    gold_loader = FromYamlDataModule(
        cfg=DataConfig(
            tokenizer=AF3Tokenizer(atomize_modified_residues=False),
            featurizer=AF3Featurizer(),
            multiplicity=1,
            moldir=MOLDIR,
            yaml_path=[yaml_input_file.name],
            design=False,
        ),
        batch_size=1,
        num_workers=0,
        pin_memory=True,
        extra_features=["structure", "tokenized"],
    )
    gold_batch = next(iter(gold_loader.predict_dataloader()))
    gold_features = {
        k: v.squeeze(0) for k, v in gold_batch.items() if isinstance(v, torch.Tensor)
    }

    gold_features["res_type"] = gold_features["res_type"].float()
    collated_gold_features = collate([gold_features])
    assert "frame_resolved_mask" not in features
    check_similar(features, collated_gold_features)


def test_featurization_IAI_with_affinity():
    batch = get_batch(yaml_path="tests/data/IAI.yaml")
    boltz_model = get_dummy_boltz_model(
        affinity_prediction=True,
        affinity_ensemble=True,
        affinity_mw_correction=False,
        run_trunk_and_structure=True,
        skip_run_structure=False,
        override_z_feats=False,
        validate_structure=False,
        tau_affinity_score=-1.0,
        alpha_affinity_absolute=0.0,
        alpha_affinity_difference=0.0,
        alpha_affinity_binary=0.0,
        alpha_affinity_score_binder_decoy=0.0,
        alpha_affinity_score_binder_binder=0.0,
        alpha_affinity_alpha_focal=0.8,
        alpha_affinity_gamma_focal=2.0,
        alpha_affinity_focal=0.0,
        affinity_use_mae=False,
        affinity_use_uber=False,
        affinity_model_args1={
            'use_cross_transformer': False,
            'num_dist_bins': 64,
            'max_dist': 22,
            'groups': {0: 1, 1: 4, 2: 6, 3: 4, 4: 1},
            'pairformer_args': {
                'num_blocks': 8,
                'dropout': 0.25,
                'activation_checkpointing': True,
                'use_trifast': True,
            },
            'transformer_args': {
                'num_blocks': 12,
                'num_heads': 8,
                'token_s': 384,
                'activation_checkpointing': True,
            },
        },
        affinity_model_args2={
            'use_cross_transformer': False,
            'num_dist_bins': 64,
            'max_dist': 22,
            'groups': {0: 1, 1: 4, 2: 6, 3: 4, 4: 1},
            'pairformer_args': {
                'num_blocks': 4,
                'dropout': 0.25,
                'activation_checkpointing': True,
                'use_trifast': True,
            },
            'transformer_args': {
                'num_blocks': 12,
                'num_heads': 8,
                'token_s': 384,
                'activation_checkpointing': True,
            },
        },
    )
    hallucinator = get_dummy_hallucinator(boltz_model, batch, extra_molecules=["IAI"])
    features = hallucinator.get_batch(res_type=hallucinator.get_hard_res_type())
    print(hallucinator.summarize_features(features))

    hard_sequences = hallucinator.get_hard_sequences()
    print(hard_sequences)

    yaml_input = {
        "sequences": [
            {
                "protein": {
                    "sequence": hard_sequences[0],
                    "id": "A",
                },
            },
            {
                "ligand": {
                    "id": "B",
                    "ccd": "IAI",
                },
            },
        ],
    }

    yaml_input_file = tempfile.NamedTemporaryFile(mode="w", delete=True, suffix=".yaml")
    yaml.dump(yaml_input, yaml_input_file)
    gold_loader = FromYamlDataModule(
        cfg=DataConfig(
            tokenizer=AF3Tokenizer(atomize_modified_residues=False),
            featurizer=AF3Featurizer(),
            multiplicity=1,
            moldir=MOLDIR,
            yaml_path=[yaml_input_file.name],
            design=False,
            compute_affinity=True,
        ),
        batch_size=1,
        num_workers=0,
        pin_memory=True,
        extra_features=["structure", "tokenized"],
    )
    gold_batch = next(iter(gold_loader.predict_dataloader()))
    gold_features = {
        k: v.squeeze(0) for k, v in gold_batch.items() if isinstance(v, torch.Tensor)
    }
    gold_features["affinity_token_mask"] = (
        gold_features["mol_type"] == const.chain_type_ids["NONPOLYMER"]
    ).to(boltz_model.device)

    gold_features["res_type"] = gold_features["res_type"].float()
    collated_gold_features = collate([gold_features])
    assert "frame_resolved_mask" not in features
    check_similar(features, collated_gold_features)


def test_featurization_protein_target():
    batch = get_batch(yaml_path="tests/data/protpdl1.yaml")
    boltz_model = get_dummy_boltz_model()
    hallucinator = get_dummy_hallucinator(boltz_model, batch)
    features = hallucinator.get_batch(res_type=hallucinator.get_hard_res_type())
    print(hallucinator.summarize_features(features))

    hard_sequences = hallucinator.get_hard_sequences()
    print(hard_sequences)

    yaml_input = {
        "sequences": [
            {
                "protein": {
                    "sequence": hard_sequences[0],
                    "id": "A",
                },
            },
            {
                "protein": {
                    "sequence": hard_sequences[1],
                    "id": "B",
                },
            },
        ],
    }

    with tempfile.TemporaryDirectory(delete=True) as temp_dir:
        # write yaml_input
        yaml_path = Path(temp_dir) / "test.yaml"
        with open(yaml_path, "w") as f:
            yaml.dump(yaml_input, f)
        gold_target = parse_yaml(yaml_path, mols=hallucinator.molecules, mol_dir=MOLDIR)
        gold_structure = gold_target.structure

    # Get features from gold standard Structure
    tokenizer = AF3Tokenizer()
    tokenized = tokenizer.tokenize(gold_structure)
    featurizer = AF3Featurizer()
    input_data = Input(
        tokens=tokenized.tokens,
        bonds=tokenized.bonds,
        token_to_res=tokenized.token_to_res,
        structure=gold_structure,
        msa={},
        templates=None,
    )
    gold_features = featurizer.process(
        input_data,
        molecules=hallucinator.molecules,
        training=False,
        random=np.random.default_rng(0),
        max_seqs=1,
        override_method="X-RAY DIFFRACTION",
    )

    gold_features["res_type"] = gold_features["res_type"].float()
    collated_gold_features = collate([gold_features])

    check_similar(features, collated_gold_features)

def test_featurization_cyclic():
    batch = get_batch(yaml_path="tests/data/cyclic_peptide.yaml")
    boltz_model = get_dummy_boltz_model()
    hallucinator = get_dummy_hallucinator(boltz_model, batch)
    features = hallucinator.get_batch(res_type=hallucinator.get_hard_res_type())
    print(hallucinator.summarize_features(features))

    hard_sequences = hallucinator.get_hard_sequences()
    print(hard_sequences)

    yaml_input = {
        "sequences": [
            {
                "protein": {
                    "sequence": hard_sequences[0],
                    "id": "A",
                    "cyclic": True,
                },
            },
            {
                "protein": {
                    "sequence": hard_sequences[1],
                    "id": "B",
                },
            },
        ],
    }

    with tempfile.TemporaryDirectory(delete=True) as temp_dir:
        # write yaml_input
        yaml_path = Path(temp_dir) / "test.yaml"
        with open(yaml_path, "w") as f:
            yaml.dump(yaml_input, f)
        gold_target = parse_yaml(yaml_path, mols=hallucinator.molecules, mol_dir=MOLDIR)
        gold_structure = gold_target.structure

    # Get features from gold standard Structure
    tokenizer = AF3Tokenizer()
    tokenized = tokenizer.tokenize(gold_structure)
    featurizer = AF3Featurizer()
    input_data = Input(
        tokens=tokenized.tokens,
        bonds=tokenized.bonds,
        token_to_res=tokenized.token_to_res,
        structure=gold_structure,
        msa={},
        templates=None,
    )
    gold_features = featurizer.process(
        input_data,
        molecules=hallucinator.molecules,
        training=False,
        random=np.random.default_rng(0),
        max_seqs=1,
        override_method="X-RAY DIFFRACTION",
    )

    gold_features["res_type"] = gold_features["res_type"].float()
    collated_gold_features = collate([gold_features])

    check_similar(features, collated_gold_features)

ALLOW_VALUES_MISMATCH = [
    "design_mask",
    "coords",
    "atom_resolved_mask",
    "ref_pos",
    "token_resolved_mask",
    "plddt",
]


def decode_ref_atom_name_chars(one_hot_tensor):
    """
    Decode ref_atom_name_chars back to atom name string.

    Parameters:
    -----------
    one_hot_tensor : torch.Tensor
        Shape: (4, 64) - one-hot encoded atom name with 4 character positions

    Returns:
    --------
    str: The decoded atom name
    """
    import torch

    # Find the index of the 1 in each row (character position)
    char_indices = torch.argmax(one_hot_tensor, dim=1)

    # Convert indices back to characters
    chars = []
    for idx in char_indices:
        if idx.item() == 0:  # 0 represents padding/null character
            chars.append("\x00")  # null character
        else:
            chars.append(chr(idx.item() + 32))

    # Join characters and strip null/padding characters
    atom_name = "".join(chars).rstrip("\x00")
    return atom_name


def decode_batch_ref_atom_name_chars(batch_tensor):
    batch_size, num_atoms, four, sixtyfour = batch_tensor.shape
    assert batch_size == 1
    assert four == 4
    assert sixtyfour == 64
    results = []
    for a in range(num_atoms):
        atom_name = decode_ref_atom_name_chars(batch_tensor[0, a])
        results.append(atom_name)
    return results


def check_similar(test_batch, gold_batch, allow_value_mismatch=ALLOW_VALUES_MISMATCH):
    problems_list = []
    problem_feature_names = []

    def problem(feature_name, msg):
        problems_list.append(msg)
        problem_feature_names.append(feature_name)
        print(msg)

    for k, v in gold_batch.items():
        if k not in test_batch:
            print(f"[Not necessarily a problem] missing feature {k}")
        elif test_batch[k] is None:
            print(f"[Not necessarily a problem] feats {k} is None")
        elif isinstance(v, torch.Tensor):
            if test_batch[k].shape != v.shape:
                problem(
                    k, f"feats {k} shape mismatch: {test_batch[k].shape} != {v.shape}"
                )
            elif test_batch[k].dtype != v.dtype:
                problem(
                    k, f"feats {k} dtype mismatch: {test_batch[k].dtype} != {v.dtype}"
                )
            elif k in allow_value_mismatch:
                print(f"feats {k} in value mismatch ignore list")
            elif (test_batch[k] != v).any():
                problem(k, f"feats {k} values mismatch: {test_batch[k]} != {v}")
            else:
                print(f"feats {k} values match.")
        elif k in ["extra_mols"]:
            if test_batch[k] != v:
                problem(k, f"non-tensor feats {k} values mismatch: {test_batch[k]} != {v}")
            else:
                print(f"non-tensor feats {k} values match.")
        else:
            if k not in ["structure_bonds"]:
                problem(k, f"feats {k} is not a tensor, but {type(v)}")

    # Note: we ignore features that are missing in ground truth.
    if len(problems_list) > 0:
        print(
            f"Found {len(problems_list)} problems in features: {problem_feature_names}"
        )
        if os.environ.get("DEBUG", "0") == "1":
            import ipdb; ipdb.set_trace()

    assert len(problems_list) == 0, (
        f"Found {len(problems_list)} problems: {'\n*********\n'.join(problems_list)}"
    )

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


def predict_structure_from_yaml(model, yaml_input, sampling_steps=200, recycling_steps=1, diffusion_samples=1, timings_out=None):
    if timings_out is None:
        timings_out = {}

    yaml_input_file = tempfile.NamedTemporaryFile(mode="w", delete=True, suffix=".yaml")
    yaml.dump(yaml_input, yaml_input_file)

    # Get the gold standard structure prediction
    gold_loader = FromYamlDataModule(
        cfg=DataConfig(
            tokenizer=AF3Tokenizer(atomize_modified_residues=False),
            featurizer=AF3Featurizer(),
            multiplicity=1,
            moldir=MOLDIR,
            yaml_path=[yaml_input_file.name],
            design=False,
            compute_affinity=True,
        ),
        batch_size=1,
        num_workers=0,
        pin_memory=True,
        extra_features=["structure", "tokenized"],
    )
    gold_batch = next(iter(gold_loader.predict_dataloader()))
    gold_structure, = gold_batch.pop("structure")
    gold_batch = {k: v.to(model.device) if isinstance(v, torch.Tensor) else v for k, v in gold_batch.items()}
    gold_batch["affinity_token_mask"] = (
        gold_batch["mol_type"] == const.chain_type_ids["NONPOLYMER"]
    )
    start = time.time()
    gold_prediction = model(
        gold_batch,
        num_sampling_steps=sampling_steps,
        recycling_steps=recycling_steps,
        diffusion_samples=diffusion_samples,
        step_scale=model.structure_module.step_scale,
        noise_scale=model.structure_module.noise_scale)
    timings_out["prediction"] = time.time() - start
    gold_pad_mask = gold_batch["atom_pad_mask"].detach().bool().squeeze().cpu().numpy()
    gold_predicted_coords = (
        gold_prediction["sample_atom_coords"].detach().squeeze().cpu().numpy()
    )
    gold_predicted_coords_unpad = gold_predicted_coords[gold_pad_mask]
    gold_structure.atoms["coords"] = gold_predicted_coords_unpad
    return gold_structure


def compare_pairwise_distances(df: pd.DataFrame, group_a_prefix='gold', group_b_prefix='hallucinator'):
    """
    Compare pairwise distances between and within groups using Mann-Whitney U test.

    Parameters:
        df (pd.DataFrame): square DataFrame with row/col labels corresponding to all samples.
        group_a_prefix (str): prefix identifying group A (default: 'gold')
        group_b_prefix (str): prefix identifying group B (default: 'hallucinator')

    Returns:
        dict: p-values and test statistics for comparisons:
              - group A vs group B
              - group A vs group A
              - group B vs group B
    """
    labels = df.index.tolist()
    group_a = [label for label in labels if label.startswith(group_a_prefix)]
    group_b = [label for label in labels if label.startswith(group_b_prefix)]

    def get_values(rows, cols):
        return [
            df.loc[r, c]
            for r in rows for c in cols
            if r != c  # skip diagonal / self-comparisons
        ]

    a_vs_a = get_values(group_a, group_a)
    b_vs_b = get_values(group_b, group_b)
    a_vs_b = get_values(group_a, group_b)

    results = {}

    # Test A vs B
    stat_ab, p_ab = mannwhitneyu(a_vs_a, a_vs_b, alternative='two-sided')
    results['gold_vs_cross'] = {'U': stat_ab, 'p': p_ab}

    # Test B vs A vs B
    stat_bb, p_bb = mannwhitneyu(b_vs_b, a_vs_b, alternative='two-sided')
    results['hallucinator_vs_cross'] = {'U': stat_bb, 'p': p_bb}

    # Optional: Compare A vs B directly (within-group)
    stat_aa_bb, p_aa_bb = mannwhitneyu(a_vs_a, b_vs_b, alternative='two-sided')
    results['gold_vs_hallucinator'] = {'U': stat_aa_bb, 'p': p_aa_bb}

    return results


def test_structure_prediction():
    # Test that predictions from the hallucinator featurization do not significantly differ from
    # predictions directly from the bolltz model using the standard featurization.
    predict_args = {
        "sampling_steps": 200,
        "recycling_steps": 1,
        "diffusion_samples": 1,
    }

    # De novo designed protein binds poly ADP ribose polymerase inhibitors (PARPi) - holo veliparib
    # see https://www.rcsb.org/sequence/8TND
    seq = "SDAQEILSRLNSVLEAAWKTILNLASATDAAEKAYKEGREEDLATYLDQAASYQSQVDQYAVETVRLLAELKKVFPDEEADRALQIAEKLLKTVQEASKTLDTAVAAAANGDEETFAKAFNQFVSLGNQADTLFTQLQRTLTNLNKK"
    model = get_real_boltz_model(checkpoint=CHECKPOINT_CONF, max_tokens=len(seq) + 18, **predict_args)
    if model is None:
        print("Skipping test.")
        return
    
    # Get the gold standard structure prediction
    yaml_input = {
        "sequences": [
            {
                "protein": {
                    "sequence": seq,
                    "id": "A",
                },
            },
            {
                "ligand": {
                    "id": "B",
                    "ccd": "78P",
                },
            },
        ],
    }

    all_predictions = []
    num_gold_predictions = 3
    timings_df = []
    for i in tqdm.tqdm(range(num_gold_predictions)):
        timings_row = {}
        result = predict_structure_from_yaml(model, yaml_input, timings_out=timings_row)
        all_predictions.append(("gold-%d" % i, result))
        timings_df.append(timings_row)
    timings_df = pd.DataFrame(timings_df)
    timings_df["method"] = "gold"
    print("Timings:")
    print(timings_df)
    print("Average time per prediction: ", timings_df["prediction"].mean())
    print("Standard deviation: ", timings_df["prediction"].std())

    batch = get_batch(yaml_path="tests/data/78P.yaml")

    for k, v in batch.items():
        if isinstance(v, torch.Tensor):
            batch[k] = v.to(model.device)

    hallucinator = get_dummy_hallucinator(model, batch, extra_molecules=["78P"])

    # Assign the sequence to hallucinator.designed_soft_sequence
    with torch.no_grad():
        hallucinator.designed_soft_sequence.zero_()
        for i, res in enumerate(seq):
            canonical_index = const.canonical_tokens.index(const.prot_letter_to_token[res])
            hallucinator.designed_soft_sequence[0, i, canonical_index] = 1.0

    hard_sequences = hallucinator.get_hard_sequences()
    assert hard_sequences[0] == seq

    num_hallucinator_predictions = 3
    timings_df2 = []
    for i in tqdm.tqdm(range(num_hallucinator_predictions)):
        start = time.time()
        prediction = hallucinator.forward()
        timings_row = {}
        hallucinator_structure = prediction.pop("structure")
        timings_row["prediction"] = time.time() - start
        timings_row["method"] = "hallucinator"
        timings_df2.append(timings_row)
        all_predictions.append(("hallucinator-%d" % i, hallucinator_structure))
    timings_df2 = pd.DataFrame(timings_df2)
    timings_df = pd.concat([timings_df, timings_df2], ignore_index=True)
    print("Timings:")
    print(timings_df)
    print("Average time per prediction: ", timings_df["prediction"].mean())

    # Compute all pairs rmsd between all predictions
    all_predictions = pd.Series(
        [p[1] for p in all_predictions],
        index=[p[0] for p in all_predictions],
    )
    rmsd_matrix = pd.DataFrame(columns=all_predictions.index, index=all_predictions.index)
    for i in all_predictions.index:
        for j in all_predictions.index:
            rmsd = compute_rmsd(
                torch.tensor(all_predictions[i].atoms["coords"].copy()).unsqueeze(0),
                torch.tensor(all_predictions[j].atoms["coords"].copy()).unsqueeze(0))
            rmsd = rmsd.item()
            rmsd_matrix.loc[i, j] = rmsd
            rmsd_matrix.loc[j, i] = rmsd
    print("RMSD matrix:")
    print(rmsd_matrix)
    results = compare_pairwise_distances(rmsd_matrix)
    print(results)
    assert rmsd_matrix.max().max() < 2.5
    assert results["gold_vs_cross"]["p"] > 0.01, \
        "gold vs hallucinator predictions are significantly different"
    
def test_avoid_aa():
    batch = get_batch(yaml_path="tests/data/IAI.yaml")
    boltz_model = get_dummy_boltz_model()
    aa = ['A', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'V', 'W', 'Y']
    disallowed_amino_acids = list(aa)
    disallowed_amino_acids.remove("P")
    disallowed_amino_acids.remove("W")
    disallowed_amino_acids.remove("E")

    hallucinator = get_dummy_hallucinator(
        boltz_model,
        batch,
        extra_molecules=["IAI"],
        disallowed_amino_acids=disallowed_amino_acids)
    hard_sequences = hallucinator.get_hard_sequences()
    print("hard_sequences", hard_sequences)
    assert all(s in ("P", "W", "E") for s in hard_sequences[0].upper())

    disallowed_amino_acids = list(aa)
    disallowed_amino_acids.remove("P")

    hallucinator = get_dummy_hallucinator(
        boltz_model,
        batch,
        extra_molecules=["IAI"],
        disallowed_amino_acids=disallowed_amino_acids)
    hard_sequences = hallucinator.get_hard_sequences()
    print("hard_sequences", hard_sequences)
    assert hard_sequences[0] == "P" * 100

    
def test_mmcif_output_cyclic():
    predict_args = {
        "sampling_steps": 20,
        "recycling_steps": 0,
        "diffusion_samples": 1,
    }

    boltz_model = get_real_boltz_model(checkpoint=CHECKPOINT_CONF, max_tokens=100, **predict_args)
    if boltz_model is None:
        print("Skipping test.")
        return
    
    batch = get_batch(yaml_path="tests/data/cyclic_peptide.yaml")
    for k, v in batch.items():
        if isinstance(v, torch.Tensor):
            batch[k] = v.to(torch.device("cuda"))
    hallucinator = get_dummy_hallucinator(boltz_model, batch)
    features = hallucinator.get_batch(res_type=hallucinator.get_hard_res_type())
    print(hallucinator.summarize_features(features))
    hard_sequences = hallucinator.get_hard_sequences()

    final_result = hallucinator.forward(res_type=hallucinator.get_hard_res_type())
    final_structure = final_result.pop("structure")

    mmcif_contents = to_mmcif(final_structure)

    # Load into gemmi and check that the sequence is cyclic with the N covalently attached to the C of the last residue
    cif_doc = gemmi.cif.read_string(mmcif_contents)
    block = cif_doc.sole_block()
    mmcif_structure = gemmi.make_structure_from_block(block)

    # Test bond in the gemmi-loaded mmcif file
    connection = mmcif_structure.connections[0]
    assert connection.partner1.chain_name == "A"
    assert connection.partner2.chain_name == "A"
    assert connection.partner1.res_id.seqid.num == 1
    assert connection.partner2.res_id.seqid.num == len(hard_sequences[0])
    assert connection.partner1.atom_name == "N"
    assert connection.partner2.atom_name == "C"

def print_gpu_memory_usage(stage=""):
    allocated = torch.cuda.memory_allocated(0) / 1024**3
    cached = torch.cuda.memory_reserved(0) / 1024**3
    print(f"GPU Memory {stage}: Allocated={allocated:.2f}GB, Cached={cached:.2f}GB")


def test_prediction_speed_profile(do_second_prediction=True):
    # Reduced parameters to save GPU memory during profiling
    predict_args = {
        "sampling_steps": 200,  # Reduced from 200 to save memory
        "recycling_steps": 1,
        "diffusion_samples": 1,
    }

    # Check available GPU memory before starting
    #torch.cuda.empty_cache()  # Clear any existing cached memory
    #print_gpu_memory_usage("after empty cache")
        
    start = time.time()
    batch = get_batch(yaml_path="tests/data/78P.yaml")
    for k, v in batch.items():
        if isinstance(v, torch.Tensor):
            batch[k] = v.to(torch.device("cuda"))
    print("Batch load time: ", time.time() - start)

    start = time.time()
    model = get_real_boltz_model(checkpoint=CHECKPOINT_CONF, max_tokens=200, **predict_args)
    if model is None:
        print("Skipping test.")
        return
    print("Model load time: ", time.time() - start)
    print_gpu_memory_usage("after model load")

    model.eval()

    start = time.time()
    result = model(
        batch,
        num_sampling_steps=predict_args["sampling_steps"],
        recycling_steps=predict_args["recycling_steps"],
        diffusion_samples=predict_args["diffusion_samples"],
        step_scale=model.structure_module.step_scale,
        noise_scale=model.structure_module.noise_scale)
    torch.cuda.synchronize()
    print("Time for first prediction: ", time.time() - start)
    print_gpu_memory_usage("after first prediction")
    
    # Clear GPU memory after first prediction
    del result
    torch.cuda.empty_cache()
    print_gpu_memory_usage("after first cleanup")

    if do_second_prediction:
        start = time.time()
        result2 = model(
            batch,
            num_sampling_steps=predict_args["sampling_steps"],
            recycling_steps=predict_args["recycling_steps"],
            diffusion_samples=predict_args["diffusion_samples"],
            step_scale=model.structure_module.step_scale,
            noise_scale=model.structure_module.noise_scale)
        torch.cuda.synchronize()
        print("Time for second prediction: ", time.time() - start)
        print_gpu_memory_usage("after second prediction")
        
        # Clear GPU memory after second prediction
        del result2
        torch.cuda.empty_cache()
        print_gpu_memory_usage("after second cleanup")

    if os.environ.get("PROFILER", "") == "torch":
        print("Running with torch profiler")    
        assert torch.cuda.is_available()
        torch.cuda.synchronize()
        torch.cuda.empty_cache()
        
        with torch.profiler.profile(
            activities=[
                torch.profiler.ProfilerActivity.CUDA,
            ],
            record_shapes=False,
            profile_memory=False,
            with_stack=False,
            with_flops=False,
            with_modules=True,
            #schedule=torch.profiler.schedule(wait=0, warmup=0, active=1, repeat=1),
            #on_trace_ready=lambda prof: None  # Disable automatic trace saving
        ) as prof:
            start = time.time()
            result3 = model(
                batch,
                num_sampling_steps=predict_args["sampling_steps"],
                recycling_steps=predict_args["recycling_steps"],
                diffusion_samples=predict_args["diffusion_samples"],
                step_scale=model.structure_module.step_scale,
                noise_scale=model.structure_module.noise_scale)
            torch.cuda.synchronize()
            prof.step()
            print("Time for third prediction: ", time.time() - start)
        
        # Clear GPU memory after profiling
        del result3
        torch.cuda.empty_cache()
        print_gpu_memory_usage("after profiling cleanup")
        
        # Print CPU time usage table (most reliable)
        print("\n=== CPU Time Usage ===")
        print(prof.key_averages().table(sort_by="cpu_time_total", row_limit=10))
        
        # Try GPU-specific sorting, fall back to basic table if unavailable
        print("\n=== GPU Time Usage ===")
        print(prof.key_averages().table(sort_by="device_time_total", row_limit=50))

        trace_file = "trace.json"
        prof.export_chrome_trace(trace_file)
        print("Wrote: ", trace_file)
    else:
        print("Running with standard python profiler")
        pr = cProfile.Profile()
        pr.enable()
        result = model(
            batch,
            num_sampling_steps=predict_args['sampling_steps'],
            recycling_steps=predict_args['recycling_steps'],
            diffusion_samples=predict_args['diffusion_samples'],
            step_scale=model.structure_module.step_scale,
            noise_scale=model.structure_module.noise_scale)
        torch.cuda.synchronize()
        pr.disable()
        s = io.StringIO()
        sortby = SortKey.CUMULATIVE
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()
        print(s.getvalue())

    if os.environ.get("DEBUG", "0") == "1":
        import ipdb; ipdb.set_trace()
    