from math import e

import time
from typing import Any, Dict, Optional, List

import numpy as np
import torch
import torch._dynamo
from pytorch_lightning import Callback, LightningModule
from torch import Tensor, nn
from torchmetrics import MeanMetric

from foldeverything.data.rmsd_computation import get_true_coordinates
import foldeverything.model.layers.initialize as init
from foldeverything.data import const
from foldeverything.data.mol import (
    minimum_lddt_symmetry_dist,
)
from foldeverything.model.layers.miniformer import MiniformerModule
from foldeverything.model.layers.pairformer import PairformerModule
from foldeverything.model.loss.atom_type import atom_type_loss_fn
from foldeverything.model.loss.bfactor import bfactor_loss_fn
from foldeverything.model.loss.confidence import (
    confidence_loss,
    resolved_loss,
)
from foldeverything.model.loss.distogram import distogram_loss
from foldeverything.model.loss.pairtoken import pairwise_token_loss
from foldeverything.model.loss.res_type import res_type_loss_fn
from foldeverything.model.loss.bond_type import bond_type_loss_fn
from foldeverything.model.loss.bond_len import bond_len_loss_fn

from foldeverything.model.modules import inverse_fold
from foldeverything.model.modules.confidence import ConfidenceModule
from foldeverything.model.modules.diffusion import AtomDiffusion
from foldeverything.model.modules.diffusion_conditioning import (
    DiffusionConditioning,
)
from foldeverything.model.modules.encoders import RelativePositionEncoder
from foldeverything.model.modules.affinity import AffinityModule
from foldeverything.model.modules.masker import BoltzMasker
from foldeverything.model.modules.trunk import (
    BFactorModule,
    ContactConditioning,
    DistogramModule,
    PairTokenModule,
    InputEmbedder,
    MSAModule,
    TemplateModule,
    TemplateV2Module,
    TokenDistanceModule,
)
from foldeverything.model.optim.ema import EMA
from foldeverything.model.optim.scheduler import AlphaFoldLRScheduler
from foldeverything.model.validation.monomer_design import RefoldingValidator
from foldeverything.model.validation.validator import Validator
from foldeverything.model.modules.inverse_fold import (
    InverseFoldingEncoder,
    InverseFoldingSimpleDecoder,
    InverseFoldingARDecoder,
)


class Boltz(LightningModule):
    """Boltz Implementation."""

    def __init__(
        self,
        atom_s: int,
        atom_z: int,
        token_s: int,
        token_z: int,
        num_bins: int,
        training_args: Dict[str, Any],
        validation_args: Dict[str, Any],
        embedder_args: Dict[str, Any],
        msa_args: Dict[str, Any],
        pairformer_args: Dict[str, Any],
        score_model_args: Dict[str, Any],
        diffusion_process_args: Dict[str, Any],
        diffusion_loss_args: Dict[str, Any],
        affinity_model_args: Dict[str, Any] = {},
        affinity_mw_correction: bool = True,
        affinity_ensemble: bool = False,
        affinity_model_args1: Dict[str, Any] = {},
        affinity_model_args2: Dict[str, Any] = {},
        confidence_model_args: Optional[Dict[str, Any]] = None,
        validators: Any = None,
        num_affinity_val_datasets: int = 1,
        masker_args: dict[str, Any] = {},
        num_val_datasets: int = 1,
        chain_sampling_args: Optional[Dict[str, Any]] = None,
        atom_feature_dim: int = 128,
        template_args: Optional[Dict] = None,
        use_miniformer: bool = True,
        use_miniformer_plus: bool = False,
        recycling_detach: bool = True,
        confidence_prediction: bool = False,
        affinity_prediction: bool = False,
        token_level_confidence: bool = True,
        confidence_imitate_trunk: bool = False,
        confidence_regression: bool = False,
        alpha_pae: float = 0.0,
        relative_confidence_supervision_weight: float = 0.0,
        structure_prediction_training: bool = True,
        skip_run_structure: bool = False,
        run_trunk_and_structure: bool = True,
        validate_structure: bool = True,
        override_z_feats: bool = False,
        tau_affinity_score: float = -1.0,
        alpha_affinity_absolute: float = 0.0,
        alpha_affinity_difference: float = 0.0,
        alpha_affinity_binary: float = 0.0,
        alpha_affinity_score_binder_decoy: float = 0.0,
        alpha_affinity_score_binder_binder: float = 0.0,
        alpha_affinity_focal: float = 0.0,
        alpha_affinity_alpha_focal: float = 0.8,
        alpha_affinity_gamma_focal: float = 2.0,
        affinity_use_mae: bool = False,
        affinity_use_uber: bool = False,
        atoms_per_window_queries: int = 32,
        atoms_per_window_keys: int = 128,
        compile_pairformer: bool = False,
        compile_structure: bool = False,
        compile_confidence: bool = False,
        compile_affinity: bool = False,
        compile_msa: bool = False,
        representative_lddt: bool = False,
        exclude_ions_from_lddt: bool = False,
        ema: bool = False,
        ema_decay: float = 0.999,
        ignore_ckpt_shape_mismatch: bool = False,
        min_dist: float = 2.0,
        max_dist: float = 22.0,
        maximum_bond_distance: int = 0,
        predict_args: Optional[Dict[str, Any]] = None,
        checkpoints: Optional[Dict[str, Any]] = None,
        step_scale_schedule: Optional[List[Dict[str, float]]] = None,
        noise_scale_schedule: Optional[List[Dict[str, float]]] = None,
        compute_tistogram: bool = False,
        num_tistogram_axis: int = 1,
        symmetry_correction_trunk: bool = False,
        symmetry_correction_denoising: bool = False,
        fix_sym_check: bool = False,
        cyclic_pos_enc: bool = False,
        trunk_resolved_loss: bool = False,
        num_distograms: int = 1,
        aggregate_distogram: bool = True,
        bond_type_feature: bool = False,
        use_no_atom_char: bool = False,
        no_random_recycling_training: bool = False,
        use_atom_backbone_feat: bool = False,
        use_residue_feats_atoms: bool = False,
        conditioning_cutoff_min: float = 4.0,
        conditioning_cutoff_max: float = 20.0,
        use_templates: bool = False,
        use_token_distances: bool = False,
        token_distance_args: Optional[Dict] = None,
        compile_templates: bool = False,
        predict_bfactor: bool = False,
        log_loss_every_steps: int = 50,
        checkpoint_diffusion_conditioning: bool = False,
        all_atom_conditioning: bool = False,
        use_templates_v2: bool = False,
        freeze_template_weights: bool = False,
        refolding_validator: Optional[RefoldingValidator] = None,
        predict_res_type: bool = False,
        predict_atom_type: bool = False,
        predict_bond_type: bool = False,
        predict_bond_len: bool = False,
        inverse_fold: bool = False,
        inverse_fold_noise: float = 0.0,
        inverse_fold_args: Optional[Dict[str, Any]] = None,
        inference_logging: bool = False,
        anchors_on: bool = False,
        always_enable_grad: bool = False,
        restrict_atom_types: bool = False,
        confidence_to_trunk_gradients: bool = False,
        ligand_pct: bool = False,
    ) -> None:
        super().__init__()
        # self.save_hyperparameters(ignore=["validators"])
        self.save_hyperparameters()

        self.inverse_fold = inverse_fold
        self.inference_logging = inference_logging
        self.run_trunk_and_structure = run_trunk_and_structure
        self.ligand_pct = ligand_pct

        # No random recycling
        self.no_random_recycling_training = no_random_recycling_training

        if validate_structure:
            # Late init at setup time
            self.val_group_mapper = {}  # maps a dataset index to a validation group name
            self.validator_mapper = {}  # maps a dataset index to a validator

            # Validators for each dataset keep track of all metrics,
            # compute validation, aggregate results and log
            self.validators = nn.ModuleList(validators)

        self.num_val_datasets = num_val_datasets
        self.ignore_ckpt_shape_mismatch = ignore_ckpt_shape_mismatch
        self.log_loss_every_steps = log_loss_every_steps

        # EMA
        self.use_ema = ema
        self.ema_decay = ema_decay

        # Arguments
        training_args["pairtoken_loss_weight"] = training_args.get(
            "pairtoken_loss_weight", 0.0
        )
        self.training_args = training_args
        self.validation_args = validation_args
        self.diffusion_loss_args = diffusion_loss_args
        self.predict_args = predict_args
        self.refolding_validator = refolding_validator
        self.predict_res_type = predict_res_type
        self.predict_atom_type = predict_atom_type
        self.predict_bond_type = predict_bond_type
        self.predict_bond_len = predict_bond_len
        self.anchors_on = anchors_on

        # Checkpoints
        self.checkpoints = checkpoints
        self.inference_counter = 0

        if checkpoints:
            self.first_checkpoint_num_samples = checkpoints.get(
                "first_checkpoint_num_samples", 1.0
            )
            self.checkpoint_list = checkpoints.get("checkpoint_list", [])
            self.total_samples = None
            self.switch_points = []
            self.checkpoint_paths = []
            self.current_checkpoint_index = -1

        # Noise and step scales
        self.step_scale_schedule = step_scale_schedule
        self.noise_scale_schedule = noise_scale_schedule
        self.step_scale_switch_points = []
        self.step_scale_values = []
        self.noise_scale_switch_points = []
        self.noise_scale_values = []

        # Training metrics
        if validate_structure:
            self.train_confidence_loss_logger = MeanMetric()
            self.train_confidence_loss_dict_logger = nn.ModuleDict()
            for m in [
                "plddt_loss",
                "resolved_loss",
                "pde_loss",
                "pae_loss",
                "rel_plddt_loss",
                "rel_pde_loss",
                "rel_pae_loss",
            ]:
                self.train_confidence_loss_dict_logger[m] = MeanMetric()
        if self.anchors_on:
            self.train_anchors_percentage = MeanMetric()
            self.val_anchors_percentage = MeanMetric()

        # Track ligand percentage only if flag is on
        if self.ligand_pct:
            self.train_ligand_percentage = MeanMetric()
            self.val_ligand_percentage = MeanMetric()

        self.num_affinity_val_datasets = num_affinity_val_datasets
        if "affinity_args" not in affinity_model_args:
            affinity_model_args["affinity_args"] = {}
        if "groups" not in affinity_model_args["affinity_args"]:
            affinity_model_args["affinity_args"]["groups"] = {0: 1}
        if "val_groups" not in affinity_model_args["affinity_args"]:
            affinity_model_args["affinity_args"]["val_groups"] = set([0])
        self.num_affinity_groups = len(affinity_model_args["affinity_args"]["groups"])

        self.affinity_groups = {0: 1.0}
        self.affinity_groups_keys = [0]
        self.afffinity_val_groups = [0]
        self.affinity_groups_weight = {0: 1.0}

        self.chain_sampling_args = chain_sampling_args
        if self.chain_sampling_args is not None:
            boundaries = torch.linspace(
                chain_sampling_args["min_dist"],
                chain_sampling_args["max_dist"],
                chain_sampling_args["num_bins"] - 1,
            )
            self.register_buffer("chain_sampling_boundaries", boundaries)
            self.chain_sampling_pairwise_embed = nn.Embedding(
                chain_sampling_args["num_bins"], token_z
            )
            init.gating_init_(self.chain_sampling_pairwise_embed.weight)

        self.representative_lddt = representative_lddt
        self.exclude_ions_from_lddt = exclude_ions_from_lddt

        # Distogram
        self.num_bins = num_bins
        self.min_dist = min_dist
        self.max_dist = max_dist
        self.num_distograms = num_distograms
        self.aggregate_distogram = aggregate_distogram

        # Trunk
        self.use_miniformer = use_miniformer
        self.use_miniformer_plus = use_miniformer_plus
        self.is_pairformer_compiled = False
        self.is_msa_compiled = False
        self.is_template_compiled = False

        # Masker
        self.masker = BoltzMasker(**masker_args)

        # Input embeddings
        full_embedder_args = {
            "atom_s": atom_s,
            "atom_z": atom_z,
            "token_s": token_s,
            "token_z": token_z,
            "atoms_per_window_queries": atoms_per_window_queries,
            "atoms_per_window_keys": atoms_per_window_keys,
            "atom_feature_dim": atom_feature_dim,
            "use_no_atom_char": use_no_atom_char,
            "use_atom_backbone_feat": use_atom_backbone_feat,
            "use_residue_feats_atoms": use_residue_feats_atoms,
            **embedder_args,
        }
        if not self.inverse_fold:
            self.input_embedder = InputEmbedder(**full_embedder_args)

            self.s_init = nn.Linear(token_s, token_s, bias=False)
            self.z_init_1 = nn.Linear(token_s, token_z, bias=False)
            self.z_init_2 = nn.Linear(token_s, token_z, bias=False)

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

        # Set compile rules
        # Big models hit the default cache limit (8)
        torch._dynamo.config.cache_size_limit = 512  # noqa: SLF001
        torch._dynamo.config.accumulated_cache_size_limit = 512  # noqa: SLF001

        # Pairwise stack
        self.use_token_distances = use_token_distances
        if self.use_token_distances:
            self.token_distance_module = TokenDistanceModule(
                token_z, **token_distance_args
            )

        self.freeze_template_weights = freeze_template_weights
        self.use_templates = use_templates
        if use_templates:
            if use_templates_v2:
                self.template_module = TemplateV2Module(token_z, **template_args)
            else:
                self.template_module = TemplateModule(token_z, **template_args)
            if compile_templates:
                self.is_template_compiled = True
                self.template_module = torch.compile(
                    self.template_module,
                    dynamic=False,
                    fullgraph=False,
                )

        if not self.inverse_fold:
            self.msa_module = MSAModule(
                token_z=token_z,
                token_s=token_s,
                **msa_args,
            )
            if compile_msa:
                self.is_msa_compiled = True
                self.msa_module = torch.compile(
                    self.msa_module,
                    dynamic=False,
                    fullgraph=False,
                )
            pairformer_class = MiniformerModule if use_miniformer else PairformerModule
            self.pairformer_module = pairformer_class(
                token_s, token_z, **pairformer_args
            )
            if compile_pairformer:
                self.is_pairformer_compiled = True
                self.pairformer_module = torch.compile(
                    self.pairformer_module,
                    dynamic=False,
                    fullgraph=False,
                )
            self.recycling_detach = recycling_detach
            self.checkpoint_diffusion_conditioning = checkpoint_diffusion_conditioning
            extra_token_transformer_heads = (
                score_model_args["extra_transformer_args"]["heads"]
                if "extra_transformer_args" in score_model_args is not None
                else None
            )
            extra_token_transformer_depth = (
                score_model_args["extra_transformer_args"]["depth"]
                if "extra_transformer_args" in score_model_args is not None
                else None
            )
            self.diffusion_conditioning = DiffusionConditioning(
                token_s=token_s,
                token_z=token_z,
                atom_s=atom_s,
                atom_z=atom_z,
                atoms_per_window_queries=atoms_per_window_queries,
                atoms_per_window_keys=atoms_per_window_keys,
                atom_encoder_depth=score_model_args["atom_encoder_depth"],
                atom_encoder_heads=score_model_args["atom_encoder_heads"],
                token_transformer_depth=score_model_args["token_transformer_depth"],
                token_transformer_heads=score_model_args["token_transformer_heads"],
                extra_token_transformer_heads=extra_token_transformer_heads,
                extra_token_transformer_depth=extra_token_transformer_depth,
                atom_decoder_depth=score_model_args["atom_decoder_depth"],
                atom_decoder_heads=score_model_args["atom_decoder_heads"],
                all_atom_encoder_prelayer_depth=score_model_args[
                    "all_atom_encoder_prelayer_depth"
                ]
                if "all_atom_encoder_prelayer_depth" in score_model_args
                else 0,
                all_atom_encoder_postlayer_depth=score_model_args[
                    "all_atom_encoder_postlayer_depth"
                ]
                if "all_atom_encoder_postlayer_depth" in score_model_args
                else 0,
                all_atom_decoder_prelayer_depth=score_model_args[
                    "all_atom_decoder_prelayer_depth"
                ]
                if "all_atom_decoder_prelayer_depth" in score_model_args
                else 0,
                all_atom_decoder_postlayer_depth=score_model_args[
                    "all_atom_decoder_postlayer_depth"
                ]
                if "all_atom_decoder_postlayer_depth" in score_model_args
                else 0,
                atom_feature_dim=atom_feature_dim,
                conditioning_transition_layers=score_model_args[
                    "conditioning_transition_layers"
                ],
                use_no_atom_char=use_no_atom_char,
                use_atom_backbone_feat=use_atom_backbone_feat,
                use_residue_feats_atoms=use_residue_feats_atoms,
                all_atom_conditioning=all_atom_conditioning,
            )

            # Output modules
            self.structure_module = AtomDiffusion(
                score_model_args={
                    "token_s": token_s,
                    "atom_s": atom_s,
                    "atoms_per_window_queries": atoms_per_window_queries,
                    "atoms_per_window_keys": atoms_per_window_keys,
                    "predict_res_type": predict_res_type,
                    "predict_atom_type": predict_atom_type,
                    "predict_bond_type": predict_bond_type,
                    "predict_bond_len": predict_bond_len,
                    "inverse_fold": inverse_fold,
                    "restrict_atom_types": restrict_atom_types,
                    **score_model_args,
                },
                compile_score=compile_structure,
                accumulate_token_repr=(confidence_prediction or affinity_prediction)
                and "use_s_diffusion" in confidence_model_args
                and confidence_model_args["use_s_diffusion"],
                inverse_fold=inverse_fold,
                inverse_fold_noise=inverse_fold_noise,
                **diffusion_process_args,
            )
            self.distogram_module = DistogramModule(
                token_z, num_bins, num_distograms=num_distograms
            )
            self.predict_bfactor = predict_bfactor
            if predict_bfactor:
                self.bfactor_module = BFactorModule(token_s, num_bins)

            if self.training_args.pairtoken_loss_weight > 0.0:
                raise Exception(
                    "pairtoken_loss_weight is deprecated and no longer works because we commented out the pairtokens in the featurizer"
                )
                self.pair_token_module = PairTokenModule(
                    token_z, num_tokens=len(const.ref_atoms.keys())
                )

        self.trunk_resolved_loss = trunk_resolved_loss
        if self.trunk_resolved_loss:
            self.to_resolved_logits = nn.Linear(token_s, 2, bias=False)
            assert "trunk_resolved_loss_weight" in self.training_args

        self.compute_tistogram = compute_tistogram
        self.num_tistogram_axis = num_tistogram_axis

        self.confidence_prediction = confidence_prediction
        self.token_level_confidence = token_level_confidence
        self.alpha_pae = alpha_pae
        self.relative_confidence_supervision_weight = (
            relative_confidence_supervision_weight
        )

        self.structure_prediction_training = structure_prediction_training
        self.symmetry_correction_trunk = symmetry_correction_trunk
        self.symmetry_correction_denoising = symmetry_correction_denoising

        ### Affinity ###
        self.affinity_prediction = affinity_prediction
        self.affinity_ensemble = affinity_ensemble
        self.affinity_mw_correction = affinity_mw_correction
        self.run_trunk_and_structure = run_trunk_and_structure
        self.skip_run_structure = skip_run_structure
        self.override_z_feats = override_z_feats
        self.validate_structure = validate_structure
        self.tau_affinity_score = tau_affinity_score
        self.alpha_affinity_absolute = alpha_affinity_absolute
        self.alpha_affinity_difference = alpha_affinity_difference
        self.alpha_affinity_binary = alpha_affinity_binary
        self.alpha_affinity_score_binder_decoy = alpha_affinity_score_binder_decoy
        self.alpha_affinity_score_binder_binder = alpha_affinity_score_binder_binder
        self.alpha_affinity_alpha_focal = alpha_affinity_alpha_focal
        self.alpha_affinity_gamma_focal = alpha_affinity_gamma_focal
        self.alpha_affinity_focal = alpha_affinity_focal
        self.affinity_use_mae = affinity_use_mae
        self.affinity_use_uber = affinity_use_uber

        if self.affinity_prediction:
            if self.affinity_ensemble:
                self.affinity_module1 = AffinityModule(
                    token_s,
                    token_z,
                    **affinity_model_args1,
                )
                self.affinity_module2 = AffinityModule(
                    token_s,
                    token_z,
                    **affinity_model_args2,
                )
                if compile_affinity:
                    self.affinity_module1 = torch.compile(
                        self.affinity_module1, dynamic=False, fullgraph=False
                    )
                    self.affinity_module2 = torch.compile(
                        self.affinity_module2, dynamic=False, fullgraph=False
                    )
            else:
                self.affinity_module = AffinityModule(
                    token_s,
                    token_z,
                    **affinity_model_args,
                )
                if compile_affinity:
                    self.affinity_module = torch.compile(
                        self.affinity_module, dynamic=False, fullgraph=False
                    )

        self.confidence_regression = confidence_regression
        if self.confidence_prediction:
            if confidence_imitate_trunk:
                self.confidence_module = ConfidenceModule(
                    token_s,
                    token_z,
                    token_level_confidence=token_level_confidence,
                    confidence_regression=confidence_regression,
                    compute_pae=alpha_pae > 0,
                    maximum_bond_distance=maximum_bond_distance,
                    bond_type_feature=bond_type_feature,
                    imitate_trunk=True,
                    pairformer_args=pairformer_args,
                    use_miniformer=use_miniformer,
                    full_embedder_args=full_embedder_args,
                    msa_args=msa_args,
                    fix_sym_check=fix_sym_check,
                    cyclic_pos_enc=cyclic_pos_enc,
                    conditioning_cutoff_min=conditioning_cutoff_min,
                    conditioning_cutoff_max=conditioning_cutoff_max,
                    **confidence_model_args,
                )
            else:
                self.confidence_module = ConfidenceModule(
                    token_s,
                    token_z,
                    token_level_confidence=token_level_confidence,
                    confidence_regression=confidence_regression,
                    compute_pae=alpha_pae > 0,
                    maximum_bond_distance=maximum_bond_distance,
                    bond_type_feature=bond_type_feature,
                    fix_sym_check=fix_sym_check,
                    cyclic_pos_enc=cyclic_pos_enc,
                    conditioning_cutoff_min=conditioning_cutoff_min,
                    conditioning_cutoff_max=conditioning_cutoff_max,
                    **confidence_model_args,
                )
            if compile_confidence:
                self.confidence_module = torch.compile(
                    self.confidence_module, dynamic=False, fullgraph=False
                )
        if self.inverse_fold:
            self.enable_if_input_embedder = False
            if inverse_fold_args.get("enable_input_embedder", False):
                self.enable_if_input_embedder = True
                self.input_embedder = InputEmbedder(**full_embedder_args)
            self.run_trunk_and_structure = False
            self.predict_bfactor = False
            self.inverse_folding_encoder = InverseFoldingEncoder(**inverse_fold_args)
            autoregressive = inverse_fold_args.get("autoregressive", False)
            if autoregressive:
                self.structure_module = InverseFoldingARDecoder(**inverse_fold_args)
            else:
                self.structure_module = InverseFoldingSimpleDecoder(**inverse_fold_args)
        # Remove grad from weights they are not trained for ddp
        if not structure_prediction_training:
            for name, param in self.named_parameters():
                if (
                    name.split(".")[0] not in ["confidence_module", "affinity_module"]
                    and "out_token_feat_update" not in name
                ):
                    param.requires_grad = False

        if self.freeze_template_weights:
            for pn, p in self.named_parameters():
                if "template_module" in pn:
                    p.requires_grad = False
        self.timestamp = time.time()

        self.training_args.skip_batch_by_single_rep = getattr(
            self.training_args, "skip_batch_by_single_rep", False
        )
        if self.training_args.skip_batch_by_single_rep:
            self.skip_step_by_single_rep = False
            print(
                "skip_batch_by_single_rep is on. Will skip training step if single representation has unstable magnitude."
            )
        self.always_enable_grad = always_enable_grad
        self.confidence_to_trunk_gradients = confidence_to_trunk_gradients

    def setup(self, stage: str) -> None:
        """Set the model for training, validation."""
        if (
            stage != "predict"
            and hasattr(self.trainer, "datamodule")
            and self.trainer.datamodule
            and self.validate_structure
        ):
            self.val_group_mapper.update(self.trainer.datamodule.val_group_mapper)

            l1 = len(self.val_group_mapper)
            l2 = self.num_val_datasets
            msg = (
                f"Number of validation datasets num_val_datasets={l2} "
                f"does not match the number of val_group_mapper entries={l1}."
            )
            assert l1 == l2, msg

            # Map an index to a validator, and double check val names
            # match from datamodule
            all_validator_names = []
            for validator in self.validators:
                for val_name in validator.val_names:
                    msg = f"Validator {val_name} duplicated in validators."
                    assert val_name not in all_validator_names, msg
                    all_validator_names.append(val_name)
                    for val_idx, val_group in self.val_group_mapper.items():
                        if val_name == val_group["label"]:
                            self.validator_mapper[val_idx] = validator

            msg = "Mismatch between validator names and val_group_mapper values."
            assert set(all_validator_names) == {
                x["label"] for x in self.val_group_mapper.values()
            }, msg

        dataloader = self.trainer.datamodule.predict_dataloader()
        self.total_samples = len(dataloader.dataset)
        if stage == "predict" and self.checkpoints:
            fractions = [self.first_checkpoint_num_samples] + [
                ckpt["checkpoint"]["num_samples"] for ckpt in self.checkpoint_list
            ]
            cumulative_samples = np.cumsum(
                [int(f * self.total_samples) for f in fractions]
            )
            self.switch_points = cumulative_samples.tolist()

            self.checkpoint_paths = [
                ckpt["checkpoint"]["path"] for ckpt in self.checkpoint_list
            ]
            self.next_switch_point = (
                self.switch_points[0] if self.switch_points else None
            )

        # Step scale
        if stage == "predict" and self.step_scale_schedule:
            self.step_scale_values = [
                item["step_scale"] for item in self.step_scale_schedule
            ]
            fractions = [item["period"] for item in self.step_scale_schedule]
            cumulative_samples = np.cumsum(
                [int(f * self.total_samples) for f in fractions]
            )
            self.step_scale_switch_points = cumulative_samples.tolist()
            self.current_step_scale_index = 0
            self.next_step_scale_switch_point = self.step_scale_switch_points[0]
            self.current_step_scale = self.step_scale_values[0]

        # Noise scale
        if stage == "predict" and self.noise_scale_schedule:
            self.noise_scale_values = [
                item["noise_scale"] for item in self.noise_scale_schedule
            ]
            fractions = [item["period"] for item in self.noise_scale_schedule]
            cumulative_samples = np.cumsum(
                [int(f * self.total_samples) for f in fractions]
            )
            self.noise_scale_switch_points = cumulative_samples.tolist()
            self.current_noise_scale_index = 0
            self.next_noise_scale_switch_point = self.noise_scale_switch_points[0]
            self.current_noise_scale = self.noise_scale_values[0]

    def load_checkpoint_weights(self, checkpoint_path):
        checkpoint = torch.load(
            checkpoint_path, map_location=self.device, weights_only=False
        )
        self.load_state_dict(checkpoint["state_dict"], strict=False)
        print(f"Loaded weights from {checkpoint_path}")

    def on_before_optimizer_step(self, optimizer):
        for name, param in self.named_parameters():
            if param.grad is None and not (
                "template_module" in name and self.freeze_template_weights
            ):
                print("Grad is None for:", name)

        if self.training_args.skip_batch_by_single_rep and self.skip_step_by_single_rep:
            print(
                "detected unstable magnitude of single rep. not updating model parameters."
            )
            self.zero_grad()
            self.skip_step_by_single_rep = False

    def forward(
        self,
        feats: Dict[str, Tensor],
        recycling_steps: int = 0,
        num_sampling_steps: Optional[int] = None,
        multiplicity_diffusion_train: int = 1,
        diffusion_samples: int = 1,
        run_confidence_sequentially: bool = False,
        return_z_feats: bool = False,
        step_scale: Optional[float] = None,
        noise_scale: Optional[float] = None,
    ) -> Dict[str, Tensor]:
        dict_out = {}
        if self.inference_logging:
            print("\nRunning Trunk.\n")
        with torch.set_grad_enabled(
            (self.training and self.structure_prediction_training)
            or self.always_enable_grad
        ):
            if self.inverse_fold:
                # mask = feats["token_pad_mask"].float()
                # pair_mask = mask[:, :, None] * mask[:, None, :]
                # z_init = z_init + self.token_distance_module(
                #     z_init, feats, pair_mask, relative_position_encoding
                # )
                if self.enable_if_input_embedder:
                    s_inputs = self.input_embedder(feats)
                    feats["s_inputs"] = s_inputs
                edge_idx, valid_mask, s, z = self.inverse_folding_encoder(feats)
                # Remove s_inputs from feats dictionary
                feats.pop("s_inputs", None)
            else:
                s_inputs = self.input_embedder(feats)

                # Initialize the sequence embeddings
                s_init = self.s_init(s_inputs)

                # Initialize pairwise embeddings
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

                # Perform rounds of the pairwise stack
                s = torch.zeros_like(s_init)
                z = torch.zeros_like(z_init)

                # Compute pairwise mask
                mask = feats["token_pad_mask"].float()
                pair_mask = mask[:, :, None] * mask[:, None, :]
            if self.run_trunk_and_structure:
                for i in range(recycling_steps + 1):
                    with torch.set_grad_enabled(
                        (
                            self.training
                            and self.structure_prediction_training
                            and (i == recycling_steps or not self.recycling_detach)
                        )
                        or self.always_enable_grad
                    ):
                        # Issue with unused parameters in autocast
                        if (
                            self.training
                            and (i == recycling_steps)
                            and torch.is_autocast_enabled()
                        ):
                            torch.clear_autocast_cache()

                        if self.chain_sampling_args is not None:
                            if (
                                i > 0
                                and (i % self.chain_sampling_args["frequency"]) == 0
                            ):
                                with torch.autocast("cuda", enabled=False):
                                    sample_dict = self.structure_module.sample(
                                        s_trunk=s.float(),
                                        z_trunk=z.float(),
                                        s_inputs=s_inputs.float(),
                                        feats=feats,
                                        relative_position_encoding=relative_position_encoding.float(),
                                        num_sampling_steps=num_sampling_steps,
                                        atom_mask=feats["atom_pad_mask"].float(),
                                        multiplicity=self.chain_sampling_args[
                                            "samples"
                                        ],
                                        train_accumulate_token_repr=self.training,
                                    )

                                    x_pred = sample_dict["sample_atom_coords"].float()
                                    # diff_token_repr = sample_dict["diff_token_repr"] TODO potentially add recycling of token repr

                                    token_to_rep_atom = feats["token_to_rep_atom"]
                                    token_to_rep_atom = (
                                        token_to_rep_atom.repeat_interleave(
                                            self.chain_sampling_args["samples"], 0
                                        )
                                    )

                                    x_pred_repr = torch.bmm(
                                        token_to_rep_atom.float(), x_pred
                                    )
                                    d = torch.cdist(x_pred_repr, x_pred_repr)

                                    chain_dist_embed = (
                                        (
                                            d.unsqueeze(-1)
                                            > self.chain_sampling_boundaries
                                        )
                                        .sum(dim=-1)
                                        .long()
                                    )
                                    chain_dist_embed = (
                                        self.chain_sampling_pairwise_embed(
                                            chain_dist_embed
                                        )
                                    )
                                    z_delta = chain_dist_embed.view(
                                        z.shape[0],
                                        self.chain_sampling_args["samples"],
                                        z.shape[1],
                                        z.shape[2],
                                        z.shape[3],
                                    ).mean(dim=1)
                            else:
                                z_delta = (
                                    torch.zeros_like(z)
                                    * self.chain_sampling_pairwise_embed.weight.sum()
                                )
                        else:
                            z_delta = torch.zeros_like(z)

                        # Apply recycling
                        s = s_init + self.s_recycle(self.s_norm(s))
                        z = z_init + self.z_recycle(self.z_norm(z)) + z_delta.to(z)

                        # Compute pairwise stack
                        if self.use_token_distances:
                            z = z + self.token_distance_module(
                                z, feats, pair_mask, relative_position_encoding
                            )

                        # Compute pairwise stack
                        if self.use_templates:
                            if self.is_template_compiled and not self.training:
                                template_module = self.template_module._orig_mod  # noqa: SLF001
                            else:
                                template_module = self.template_module

                            z = z + template_module(z, feats, pair_mask)

                        if not self.inverse_fold:
                            if self.is_msa_compiled and not self.training:
                                msa_module = self.msa_module._orig_mod  # noqa: SLF001
                            else:
                                msa_module = self.msa_module

                            z = z + msa_module(z, s_inputs, feats)

                        # Revert to uncompiled version for validation
                        if self.is_pairformer_compiled and not self.training:
                            pairformer_module = self.pairformer_module._orig_mod  # noqa: SLF001
                        else:
                            pairformer_module = self.pairformer_module

                        s, z = pairformer_module(s, z, mask=mask, pair_mask=pair_mask)

            if self.override_z_feats:
                z_new = []
                for i in range(len(feats["indices_z_feats"])):
                    indices_z_feats = feats["indices_z_feats"][i]
                    z_feats = feats["z_feats"][i]
                    z_new_idx = torch.zeros(
                        z_init.shape[1:], dtype=z_init.dtype, device=z_init.device
                    )
                    z_new_idx[indices_z_feats[:, 0], indices_z_feats[:, 1], :] = z_feats
                    z_new.append(z_new_idx.unsqueeze(0))
                z = torch.cat(z_new, dim=0)

            if not self.inverse_fold:
                pdistogram = self.distogram_module(z)
                if self.training_args.pairtoken_loss_weight > 0.0:
                    ppairtoken = self.pair_token_module(z)
                else:
                    ppairtoken = None

                dict_out["pdistogram"] = pdistogram.float()
                dict_out["ppairtoken"] = ppairtoken

            if self.run_trunk_and_structure and (not self.skip_run_structure):
                if self.checkpoint_diffusion_conditioning:
                    # TODO decide whether this should be with bf16 or not
                    (
                        q,
                        c,
                        to_keys,
                        atom_enc_bias,
                        atom_dec_bias,
                        token_trans_bias,
                        extra_token_trans_bias,
                        all_atom_bias,
                    ) = torch.utils.checkpoint.checkpoint(
                        self.diffusion_conditioning,
                        s,
                        z,
                        relative_position_encoding,
                        feats,
                    )
                else:
                    (
                        q,
                        c,
                        to_keys,
                        atom_enc_bias,
                        atom_dec_bias,
                        token_trans_bias,
                        extra_token_trans_bias,
                        all_atom_bias,
                    ) = self.diffusion_conditioning(
                        s_trunk=s,
                        z_trunk=z,
                        relative_position_encoding=relative_position_encoding,
                        feats=feats,
                    )
                diffusion_conditioning = {
                    "q": q,
                    "c": c,
                    "to_keys": to_keys,
                    "atom_enc_bias": atom_enc_bias,
                    "atom_dec_bias": atom_dec_bias,
                    "token_trans_bias": token_trans_bias,
                    "extra_token_trans_bias": extra_token_trans_bias,
                    "all_atom_bias": all_atom_bias
                }

                if self.predict_bfactor:
                    pbfactor = self.bfactor_module(s)
                    dict_out["pbfactor"] = pbfactor

                if self.trunk_resolved_loss:
                    dict_out["trunk_resolved_logits"] = self.to_resolved_logits(s)

            if (
                (self.inverse_fold or self.run_trunk_and_structure)
                and (
                    (not self.training)
                    or self.confidence_prediction
                    or self.affinity_prediction
                    or self.symmetry_correction_denoising
                )
                and (not self.skip_run_structure)
            ):
                if self.inference_logging:
                    print("\nRunning Structure Module.\n")
                with torch.autocast("cuda", enabled=False):
                    if not self.inverse_fold:
                        struct_out = self.structure_module.sample(
                            s_trunk=s.float(),
                            s_inputs=s_inputs.float(),
                            feats=feats,
                            num_sampling_steps=num_sampling_steps,
                            atom_mask=feats["atom_pad_mask"].float(),
                            multiplicity=diffusion_samples,
                            train_accumulate_token_repr=self.training,
                            diffusion_conditioning=diffusion_conditioning,
                            step_scale=step_scale,
                            noise_scale=noise_scale,
                            inference_logging=self.inference_logging,
                        )
                    else:
                        struct_out = self.structure_module.sample(
                            s=s,
                            z=z,
                            edge_idx=edge_idx,
                            valid_mask=valid_mask,
                            feats=feats,
                        )

                    dict_out.update(struct_out)

                if (
                    self.symmetry_correction_trunk
                    and self.training
                    and self.structure_prediction_training
                ):
                    for idx in range(feats["token_index"].shape[0]):
                        minimum_lddt_symmetry_dist(
                            pred_distogram=pdistogram[idx],
                            feats=feats,
                            index_batch=idx,
                        )

            if self.training and (
                self.confidence_prediction or self.affinity_prediction
            ):
                assert len(feats["coords"].shape) == 4
                assert feats["coords"].shape[1] == 1, (
                    "Only one conformation is supported for confidence"
                )

            # Compute structure module
            if self.training and self.structure_prediction_training:
                atom_coords = feats["coords"]
                B, K, L = atom_coords.shape[0:3]
                assert K in (
                    multiplicity_diffusion_train,
                    1,
                )  # TODO make check somewhere else, expand to m % N == 0, m > N
                atom_coords = atom_coords.reshape(B * K, L, 3)
                atom_coords = atom_coords.repeat_interleave(
                    multiplicity_diffusion_train // K, 0
                )
                feats["coords"] = atom_coords  # (multiplicity, L, 3)
                assert len(feats["coords"].shape) == 3

                with torch.autocast("cuda", enabled=False):
                    if not self.inverse_fold:
                        struct_out = self.structure_module(
                            s_trunk=s.float(),
                            s_inputs=s_inputs.float(),
                            feats=feats,
                            multiplicity=multiplicity_diffusion_train,
                            diffusion_conditioning=diffusion_conditioning,
                        )
                    else:
                        struct_out = self.structure_module(
                            s=s,
                            z=z,
                            edge_idx=edge_idx,
                            valid_mask=valid_mask,
                            feats=feats,
                        )
                    dict_out.update(struct_out)

            elif self.training:
                feats["coords"] = feats["coords"].squeeze(1)
                assert len(feats["coords"].shape) == 3

        if self.confidence_prediction:
            msg_1 = "Confidence not implemented for num_distograms > 1"
            assert self.num_distograms == 1, msg_1
            dict_out.update(
                self.confidence_module(
                    s_inputs=s_inputs.detach()
                    if not self.confidence_to_trunk_gradients
                    else s_inputs,
                    s=(
                        s.detach()
                        if not self.confidence_module.no_trunk_feats
                        else s_init.detach()
                        if not self.confidence_to_trunk_gradients
                        else s_init
                    ),
                    z=(
                        (z.detach() if not self.confidence_to_trunk_gradients else z)
                        if not self.confidence_module.no_trunk_feats
                        else (
                            z_init.detach()
                            if not self.confidence_to_trunk_gradients
                            else z_init
                        )
                    ),
                    s_diffusion=(
                        dict_out["diff_token_repr"]
                        if self.confidence_module.use_s_diffusion
                        else None
                    ),
                    x_pred=(
                        dict_out["sample_atom_coords"].detach()
                        if not self.skip_run_structure
                        else feats["coords"].repeat_interleave(diffusion_samples, 0)
                    ),
                    feats=feats,
                    pred_distogram_logits=(
                        dict_out["pdistogram"][:, :, :, 0].detach()
                        if not self.confidence_to_trunk_gradients
                        else dict_out["pdistogram"][
                            :, :, :, 0
                        ]  # TODO only implemeted for 1 distogram
                    ),
                    multiplicity=diffusion_samples,
                    run_sequentially=run_confidence_sequentially,
                )
            )

        if self.confidence_prediction and self.confidence_module.use_s_diffusion:
            dict_out.pop("diff_token_repr", None)

        if self.affinity_prediction:
            pad_token_mask = feats["token_pad_mask"][0]
            rec_mask = feats["mol_type"][0] == 0
            rec_mask = rec_mask * pad_token_mask
            lig_mask = feats["affinity_token_mask"][0].to(torch.bool)
            lig_mask = lig_mask * pad_token_mask
            cross_pair_mask = (
                lig_mask[:, None] * rec_mask[None, :]
                + rec_mask[:, None] * lig_mask[None, :]
                + lig_mask[:, None] * lig_mask[None, :]
            )
            z_affinity = z * cross_pair_mask[None, :, :, None]

            argsort = torch.argsort(dict_out["iptm"], descending=True)
            best_idx = argsort[0].item()
            coords_affinity = dict_out["sample_atom_coords"].detach()[best_idx][
                None, None
            ]
            s_inputs = self.input_embedder(feats, affinity=True)

            with torch.autocast("cuda", enabled=False):
                if self.affinity_ensemble:
                    dict_out_affinity1 = self.affinity_module1(
                        s_inputs=s_inputs.detach(),
                        z=z_affinity.detach(),
                        x_pred=coords_affinity,
                        feats=feats,
                        multiplicity=1,
                    )

                    dict_out_affinity1["affinity_probability_binary"] = (
                        torch.nn.functional.sigmoid(
                            dict_out_affinity1["affinity_logits_binary"]
                        )
                    )
                    dict_out_affinity2 = self.affinity_module2(
                        s_inputs=s_inputs.detach(),
                        z=z_affinity.detach(),
                        x_pred=coords_affinity,
                        feats=feats,
                        multiplicity=1,
                    )
                    dict_out_affinity2["affinity_probability_binary"] = (
                        torch.nn.functional.sigmoid(
                            dict_out_affinity2["affinity_logits_binary"]
                        )
                    )

                    dict_out_affinity_ensemble = {
                        "affinity_pred_value": (
                            dict_out_affinity1["affinity_pred_value"]
                            + dict_out_affinity2["affinity_pred_value"]
                        )
                        / 2,
                        "affinity_probability_binary": (
                            dict_out_affinity1["affinity_probability_binary"]
                            + dict_out_affinity2["affinity_probability_binary"]
                        )
                        / 2,
                    }

                    dict_out_affinity1 = {
                        "affinity_pred_value1": dict_out_affinity1[
                            "affinity_pred_value"
                        ],
                        "affinity_probability_binary1": dict_out_affinity1[
                            "affinity_probability_binary"
                        ],
                    }
                    dict_out_affinity2 = {
                        "affinity_pred_value2": dict_out_affinity2[
                            "affinity_pred_value"
                        ],
                        "affinity_probability_binary2": dict_out_affinity2[
                            "affinity_probability_binary"
                        ],
                    }

                    if self.affinity_mw_correction:
                        model_coef = 1.03525938
                        mw_coef = -0.59992683
                        bias = 2.83288489
                        mw = feats["affinity_mw"][0] ** 0.3
                        dict_out_affinity_ensemble["affinity_pred_value"] = (
                            model_coef
                            * dict_out_affinity_ensemble["affinity_pred_value"]
                            + mw_coef * mw
                            + bias
                        )

                    dict_out.update(dict_out_affinity_ensemble)
                    dict_out.update(dict_out_affinity1)
                    dict_out.update(dict_out_affinity2)
                else:
                    dict_out_affinity = self.affinity_module(
                        s_inputs=s_inputs.detach(),
                        z=z_affinity.detach(),
                        x_pred=coords_affinity,
                        feats=feats,
                        multiplicity=1,
                    )
                    dict_out.update(
                        {
                            "affinity_pred_value": dict_out_affinity[
                                "affinity_pred_value"
                            ],
                            "affinity_probability_binary": torch.nn.functional.sigmoid(
                                dict_out_affinity["affinity_logits_binary"]
                            ),
                        }
                    )
        if return_z_feats:
            dict_out["z_feats"] = z
        dict_out["s_trunk"] = (
            s  # For stability, https://github.com/IntelliGen-AI/IntFold
        )
        return dict_out

    def training_step(self, batch: Dict[str, Tensor], batch_idx: int) -> Tensor:
        start = time.time()
        # Count datasets with anchor atoms
        if self.anchors_on:
            if batch["is_anchor"].sum() > 0:
                self.train_anchors_percentage.update(1)
            elif batch["is_anchor"].sum() == 0:
                self.train_anchors_percentage.update(0)

        if self.ligand_pct:
            ligand_tokens = (
                batch["mol_type"] == const.chain_type_ids["NONPOLYMER"]
            ).bool() & batch["design_mask"].bool()
            has_ligand = (ligand_tokens.sum(dim=1) > 0).float()
            if has_ligand.sum() > 0:
                self.train_ligand_percentage.update(1)
            else:
                self.train_ligand_percentage.update(0)

        # Sample recycling steps
        if self.no_random_recycling_training:
            recycling_steps = self.training_args.recycling_steps
        else:
            rgn = np.random.default_rng(self.global_step)
            recycling_steps = rgn.integers(
                0, self.training_args.recycling_steps + 1
            ).item()

        if self.training_args.get("sampling_steps_random", None) is not None:
            rgn_samplng_steps = np.random.default_rng(self.global_step)
            sampling_steps = rgn_samplng_steps.choice(
                self.training_args.sampling_steps_random
            )
        else:
            sampling_steps = self.training_args.sampling_steps

        # Mask features for conditioning
        feat_masked = self.masker(batch)

        # Compute the forward pass
        out = self(
            feats=feat_masked,
            recycling_steps=recycling_steps,
            num_sampling_steps=sampling_steps,
            multiplicity_diffusion_train=self.training_args.diffusion_multiplicity,
            diffusion_samples=self.training_args.diffusion_samples,
        )
        sigmas = out["sigmas"]
        pred_mask = (sigmas < self.structure_module.pred_sigma_thresh).float()

        n_pred_true = int(pred_mask.sum().item())
        n_pred_total = pred_mask.numel()
        print(f"[rank {self.global_rank}] n_pred_true={n_pred_true}, n_pred_total={n_pred_total}")
        batch["coords"] = feat_masked["coords"].clone()

        # Compute losses
        if self.structure_prediction_training:
            if not self.inverse_fold:
                disto_loss, _ = distogram_loss(
                    out,
                    batch,
                    aggregate_distogram=self.aggregate_distogram,
                )
                try:
                    diffusion_loss_dict = self.structure_module.compute_loss(
                        batch,
                        out,
                        multiplicity=self.training_args.diffusion_multiplicity,
                        **self.diffusion_loss_args,
                    )
                except Exception as e:
                    print(f"Skipping batch {batch_idx} due to error: {e}")
                    return None
            else:
                disto_loss = 0.0
                diffusion_loss_dict = {"loss": 0.0, "loss_breakdown": {}}

            if self.predict_bfactor:
                bfactor_loss = bfactor_loss_fn(out, batch)
            else:
                bfactor_loss = 0.0

            if self.training_args.pairtoken_loss_weight > 0.0:
                pairtoken_loss, _ = pairwise_token_loss(
                    out,
                    batch,
                )
            else:
                pairtoken_loss = 0.0

            if self.predict_res_type:
                res_type_loss, res_type_acc = res_type_loss_fn(out, batch, pred_mask)
            else:
                res_type_loss, res_type_acc = 0.0, 0.0


            if self.predict_atom_type:
                atom_type_loss = atom_type_loss_fn(out, batch, pred_mask)
                rank = self.global_rank
                loss_val      = atom_type_loss.detach().item()
                design_tokens = batch["design_mask"].sum().item()
                print(f"[rank {rank}] atom_type_loss={loss_val:.4f}, design_tokens={design_tokens}")
            else:
                atom_type_loss = 0.0

            if self.predict_bond_type:
                bond_type_loss = bond_type_loss_fn(out, batch, pred_mask)
                rank = self.global_rank
                loss_val      = bond_type_loss.detach().item()
                design_tokens = batch["design_mask"].sum().item()
                print(f"[rank {rank}] bond_type_loss={loss_val:.4f}, design_tokens={design_tokens}")
            else:
                bond_type_loss = 0.0

            if self.predict_bond_len:
                bond_len_loss = bond_len_loss_fn(out, batch, pred_mask)
                rank = self.global_rank
                loss_val      = bond_len_loss.detach().item()
                design_tokens = batch["design_mask"].sum().item()
                print(f"[rank {rank}] bond_len_loss={loss_val:.4f}, design_tokens={design_tokens}")
            else:
                bond_len_loss = 0.0

        else:
            disto_loss = 0.0
            pairtoken_loss = 0.0
            bfactor_loss = 0.0
            res_type_loss = 0.0
            atom_type_loss = 0.0
            bond_type_loss = 0.0
            bond_len_loss = 0.0
            diffusion_loss_dict = {"loss": 0.0, "loss_breakdown": {}}

        if self.trunk_resolved_loss:
            trunk_resolved_loss = resolved_loss(
                out["trunk_resolved_logits"],
                batch,
                batch["atom_resolved_mask"],
                token_level_confidence=True,
                multiplicity=1,
                mask_loss=(
                    batch["has_structure"].reshape(-1)
                    if "has_structure" in batch
                    else None
                ),
            )
        else:
            trunk_resolved_loss = 0.0

        if self.confidence_prediction:
            try:
                # confidence model symmetry correction
                return_dict = get_true_coordinates(
                    batch,
                    out,
                    diffusion_samples=self.training_args.diffusion_samples,
                    symmetry_correction=self.training_args.symmetry_correction,
                )
            except Exception as e:
                print(f"Skipping batch with id {batch['pdb_id']} due to error: {e}")
                return None

            true_coords = return_dict["true_coords"]
            true_coords_resolved_mask = return_dict["true_coords_resolved_mask"]

            # TODO remove once multiple conformers are supported
            K = true_coords.shape[1]
            assert K == 1, (
                f"Confidence_prediction is not supported for num_ensembles_val={K}."
            )

            # For now, just take the only conformer.
            true_coords = true_coords.squeeze(1)  # (S, L, 3)
            batch["frames_idx"] = batch["frames_idx"].squeeze(1)
            batch["frame_resolved_mask"] = batch["frame_resolved_mask"].squeeze(1)

            try:
                confidence_loss_dict = confidence_loss(
                    out,
                    batch,
                    true_coords,
                    true_coords_resolved_mask,
                    token_level_confidence=self.token_level_confidence,
                    alpha_pae=self.alpha_pae,
                    multiplicity=self.training_args.diffusion_samples,
                    mask_loss=(
                        batch["has_structure"].reshape(-1)
                        if "has_structure" in batch
                        else None
                    ),
                    relative_supervision_weight=self.relative_confidence_supervision_weight,
                )
            except Exception as e:
                raise e
                print(f"Unable to compute loss for id {batch['pdb_id']} due to {e}")
                return None
        else:
            confidence_loss_dict = {
                "loss": torch.tensor(0.0, device=batch["token_index"].device),
                "loss_breakdown": {},
            }

        # Skip step if single representation has unstable magnitude.
        # Reference: https://github.com/IntelliGen-AI/IntFold
        if self.training_args.skip_batch_by_single_rep:
            s_trunk = out["s_trunk"]
            magnitudes = torch.linalg.norm(s_trunk, dim=-1)
            if torch.any(magnitudes > 40000):
                self.skip_step_by_single_rep = True
            self.log("train/single_norm", torch.mean(magnitudes), prog_bar=False)

        # Aggregate losses
        # NOTE: we already have an implicit weight in the losses induced by dataset sampling
        # NOTE: this logic works only for datasets with either affinity or confidence labels
        loss = (
            self.training_args.confidence_loss_weight * confidence_loss_dict["loss"]
            + self.training_args.diffusion_loss_weight * diffusion_loss_dict["loss"]
            + self.training_args.distogram_loss_weight * disto_loss
            + self.training_args.get("pairtoken_loss_weight", 0.0) * pairtoken_loss
            + self.training_args.get("bfactor_loss_weight", 0.0) * bfactor_loss
            + self.training_args.get("res_type_loss_weight", 0.0) * res_type_loss
            + self.training_args.get("atom_type_loss_weight", 0.0) * atom_type_loss
            + self.training_args.get("bond_type_loss_weight", 0.0) * bond_type_loss
            + self.training_args.get("bond_len_loss_weight", 0.0) * bond_len_loss
            + self.training_args.get("trunk_resolved_loss_weight", 0.0)
            * trunk_resolved_loss
        )

        if not (self.global_step % self.log_loss_every_steps):
            # Log losses
            if self.validate_structure:
                self.log("train/distogram_loss", disto_loss)
                self.log("train/pairtoken_loss", pairtoken_loss)
                self.log("train/res_type_loss", res_type_loss)
                self.log("train/res_type_acc", res_type_acc)
                self.log("train/atom_type_loss", atom_type_loss)
                self.log("train/bond_type_loss", bond_type_loss)
                self.log("train/bond_len_loss", bond_len_loss)
                self.log("train/trunk_resolved_loss", trunk_resolved_loss)
                self.log("train/diffusion_loss", diffusion_loss_dict["loss"])
                for k, v in diffusion_loss_dict["loss_breakdown"].items():
                    self.log(f"train/{k}", v)

            if self.confidence_prediction:
                self.train_confidence_loss_logger.update(
                    confidence_loss_dict["loss"].detach(), batch["has_structure"].sum()
                )
                for k in self.train_confidence_loss_dict_logger:
                    self.train_confidence_loss_dict_logger[k].update(
                        (
                            confidence_loss_dict["loss_breakdown"][k].detach()
                            if torch.is_tensor(
                                confidence_loss_dict["loss_breakdown"][k]
                            )
                            else confidence_loss_dict["loss_breakdown"][k]
                        ),
                        batch["has_structure"].sum(),
                    )
            self.log("train/loss", loss)
            self.log("train/forward_dur", time.time() - start)
            self.log("train/step_dur", time.time() - self.timestamp)
            self.timestamp = time.time()
            self.training_log()
        return loss

    def training_log(self):
        self.log("train/grad_norm", self.gradient_norm(self), prog_bar=False)
        if self.confidence_prediction:
            self.log(
                "train/grad_norm_affinity_module",
                self.gradient_norm(self.affinity_module),
                prog_bar=False,
            )

        self.log("train/param_norm", self.parameter_norm(self), prog_bar=False)

        lr = self.trainer.optimizers[0].param_groups[0]["lr"]
        self.log("lr", lr, prog_bar=False)

        if not self.inverse_fold:
            self.log(
                "train/param_norm_msa_module",
                self.parameter_norm(self.msa_module),
                prog_bar=False,
            )

            self.log(
                "train/param_norm_pairformer_module",
                self.parameter_norm(self.pairformer_module),
                prog_bar=False,
            )

            self.log(
                "train/param_norm_structure_module",
                self.parameter_norm(self.structure_module),
                prog_bar=False,
            )

        if self.confidence_prediction:
            self.log(
                "train/grad_norm_confidence_module",
                self.gradient_norm(self.confidence_module),
                prog_bar=False,
            )
            self.log(
                "train/param_norm_confidence_module",
                self.parameter_norm(self.confidence_module),
                prog_bar=False,
            )

    def on_train_epoch_end(self):
        if self.confidence_prediction:
            self.log(
                "train/confidence_loss",
                self.train_confidence_loss_logger,
                prog_bar=False,
                on_step=False,
                on_epoch=True,
            )
            for k, v in self.train_confidence_loss_dict_logger.items():
                self.log(f"train/{k}", v, prog_bar=False, on_step=False, on_epoch=True)
        if self.anchors_on:
            self.train_anchors_percentage = self.train_anchors_percentage.to(
                self.device
            )
            train_anchors_percentage = self.train_anchors_percentage.compute()
            self.log(
                "train/anchors_percentage", train_anchors_percentage, prog_bar=False
            )
            self.train_anchors_percentage.reset()

        if self.ligand_pct:
            self.train_ligand_percentage = self.train_ligand_percentage.to(self.device)
            self.log(
                "train/ligand_percentage",
                self.train_ligand_percentage.compute(),
                prog_bar=False,
                on_step=False,
                on_epoch=True,
            )
            self.train_ligand_percentage.reset()

    def gradient_norm(self, module):
        parameters = [
            p.grad.norm(p=2) ** 2
            for p in module.parameters()
            if p.requires_grad and p.grad is not None
        ]
        if len(parameters) == 0:
            return torch.tensor(
                0.0, device="cuda" if torch.cuda.is_available() else "cpu"
            )
        norm = torch.stack(parameters).sum().sqrt()
        return norm

    def parameter_norm(self, module):
        parameters = [p.norm(p=2) ** 2 for p in module.parameters() if p.requires_grad]
        if len(parameters) == 0:
            return torch.tensor(
                0.0, device="cuda" if torch.cuda.is_available() else "cpu"
            )
        norm = torch.stack(parameters).sum().sqrt()
        return norm

    def validation_step(
        self, batch: Dict[str, Tensor], batch_idx: int, dataloader_idx: int = 0
    ):
        start = time.time()
        if self.validate_structure:
            try:
                msg = "Only batch=1 is supported for validation"
                assert batch["idx_dataset"].shape[0] == 1, msg

                # Select validator based on dataset
                idx_dataset = batch["idx_dataset"][0].item()
                if dataloader_idx > 0:
                    validator = self.refolding_validator
                else:
                    validator = self.validator_mapper[idx_dataset]

                # Mask features
                feat_masked = self.masker(batch)

                # Run forward pass
                out = validator.run_model(
                    model=self, batch=feat_masked, idx_dataset=idx_dataset
                )
                batch["coords"] = feat_masked["coords"].clone()
                out["feat_masked"] = feat_masked

                # Compute validation step

                validator.process(
                    model=self,
                    batch=batch,
                    out=out,
                    idx_dataset=idx_dataset,
                    n_samples=self.validation_args.diffusion_samples,
                    batch_idx=batch_idx,
                    dataloader_idx=dataloader_idx,
                )
            except RuntimeError as e:  # catch out of memory exceptions
                if "out of memory" in str(e):
                    msg = f"| WARNING: ran out of memory, skipping batch, {idx_dataset}"
                    print(
                        msg,
                        "coords =",
                        batch["coords"].shape,
                        "res_type =",
                        batch["res_type"].shape,
                    )
                    torch.cuda.empty_cache()
                    return
                raise e
        else:
            try:
                out = self(
                    batch,
                    recycling_steps=self.validation_args.recycling_steps,
                    num_sampling_steps=self.validation_args.sampling_steps,
                    diffusion_samples=self.validation_args.diffusion_samples,
                    run_confidence_sequentially=self.validation_args.get(
                        "run_confidence_sequentially", False
                    ),
                )
            except RuntimeError as e:  # catch out of memory exceptions
                idx_dataset = batch["idx_dataset"][0].item()
                if "out of memory" in str(e):
                    msg = f"| WARNING: ran out of memory, skipping batch, {idx_dataset}"
                    print(msg)
                    torch.cuda.empty_cache()
                    return
                raise e

        self.log("val/forward_dur", time.time() - start)
        self.log("val/step_dur", time.time() - self.timestamp)
        self.timestamp = time.time()
        if self.anchors_on:
            if batch["is_anchor"].sum() > 0:
                self.val_anchors_percentage.update(1)
            elif batch["is_anchor"].sum() == 0:
                self.val_anchors_percentage.update(0)

        if self.ligand_pct:
            ligand_tokens_val = (
                batch["mol_type"] == const.chain_type_ids["NONPOLYMER"]
            ).bool() & batch["design_mask"].bool()
            has_ligand_val = (ligand_tokens_val.sum(dim=1) > 0).float()
            if has_ligand_val.sum() > 0:
                self.val_ligand_percentage.update(1)
            else:
                self.val_ligand_percentage.update(0)

    def on_validation_epoch_end(self) -> None:
        """Aggregate all metrics for each validator."""
        if self.validate_structure:
            for validator in self.validator_mapper.values():
                # This will aggregate, compute and log all metrics
                validator.on_epoch_end(model=self)

        if self.refolding_validator is not None:
            assert (
                self.trainer.datamodule.monomer_split
                or self.trainer.datamodule.ligand_split
            )
            self.refolding_validator.on_epoch_end(model=self)

        if self.anchors_on:
            self.val_anchors_percentage = self.val_anchors_percentage.to(self.device)
            val_anchors_percentage = self.val_anchors_percentage.compute()
            self.log("val/anchors_percentage", val_anchors_percentage, prog_bar=False)
            self.val_anchors_percentage.reset()

        if self.ligand_pct:
            self.val_ligand_percentage = self.val_ligand_percentage.to(self.device)
            self.log(
                "val/ligand_percentage",
                self.val_ligand_percentage.compute(),
                prog_bar=False,
            )
            self.val_ligand_percentage.reset()

    def predict_step(self, batch: Any, batch_idx: int = 0, dataloader_idx: int = 0) -> Dict:
        # Skip invalid samples
        if "exception" in batch and any(batch["exception"]):
            print(f"WARNING: Skipping batch. Exception for {batch['id'][0]}")
            return {"exception": True}
        if "skip" in batch and any(batch["skip"]):
            print(f"WARNING: Skipping batch. Skip was set true for {batch['id'][0]}")
            return {"skip": True}

        # Checkpoint switching logic
        if self.checkpoints and self.next_switch_point is not None:
            if self.inference_counter == self.next_switch_point:
                self.current_checkpoint_index += 1
                if 0 <= self.current_checkpoint_index < len(self.checkpoint_paths):
                    self.load_checkpoint_weights(
                        self.checkpoint_paths[self.current_checkpoint_index]
                    )
                if self.current_checkpoint_index + 1 < len(self.switch_points):
                    self.next_switch_point = self.switch_points[
                        self.current_checkpoint_index + 1
                    ]
                else:
                    self.next_switch_point = None
                print("switched checkpoint")

        # Temperature switching logic
        if self.step_scale_schedule and self.next_step_scale_switch_point is not None:
            if self.inference_counter == self.next_step_scale_switch_point:
                self.current_step_scale_index += 1
                if self.current_step_scale_index < len(self.step_scale_values):
                    self.current_step_scale = self.step_scale_values[
                        self.current_step_scale_index
                    ]
                    if self.current_step_scale_index + 1 < len(
                        self.step_scale_switch_points
                    ):
                        self.next_step_scale_switch_point = (
                            self.step_scale_switch_points[
                                self.current_step_scale_index + 1
                            ]
                        )
                    else:
                        self.next_step_scale_switch_point = None
                print(f"Switched step_scale to {self.current_step_scale}")

        if self.noise_scale_schedule and self.next_noise_scale_switch_point is not None:
            if self.inference_counter == self.next_noise_scale_switch_point:
                self.current_noise_scale_index += 1
                if self.current_noise_scale_index < len(self.noise_scale_values):
                    self.current_noise_scale = self.noise_scale_values[
                        self.current_noise_scale_index
                    ]
                    if self.current_noise_scale_index + 1 < len(
                        self.noise_scale_switch_points
                    ):
                        self.next_noise_scale_switch_point = (
                            self.noise_scale_switch_points[
                                self.current_noise_scale_index + 1
                            ]
                        )
                    else:
                        self.next_noise_scale_switch_point = None
                print(f"Switched noise_scale to {self.current_noise_scale}")

        step_scale = getattr(self, "current_step_scale", None)
        noise_scale = getattr(self, "current_noise_scale", None)

        try:
            feat_masked = self.masker(batch)
            out = self(
                feat_masked,
                recycling_steps=self.predict_args["recycling_steps"],
                num_sampling_steps=self.predict_args["sampling_steps"],
                diffusion_samples=self.predict_args["diffusion_samples"],
                run_confidence_sequentially=True,
                step_scale=step_scale,
                noise_scale=noise_scale,
                return_z_feats=(
                    self.predict_args["return_z_feats"]
                    if "return_z_feats" in self.predict_args
                    else False
                ),
            )
            pred_dict = {"exception": False}
            pred_dict.update(feat_masked)

            if "keys_dict_batch" in self.predict_args:
                for key in self.predict_args["keys_dict_batch"]:
                    pred_dict[key] = batch[key]
            if (
                "return_z_feats" in self.predict_args
                and self.predict_args["return_z_feats"]
            ):
                pred_dict["z_feats"] = out["z_feats"]
            pred_dict["masks"] = batch["atom_pad_mask"]
            pred_dict["token_masks"] = batch["token_pad_mask"]
            if "keys_dict_out" in self.predict_args:
                for key in self.predict_args["keys_dict_out"]:
                    pred_dict[key] = out[key]
            pred_dict["coords"] = out["sample_atom_coords"]
            if not self.inverse_fold:
                pred_dict["coords_traj"] = out["coords_traj"]
                pred_dict["x0_coords_traj"] = out["x0_coords_traj"]
            if self.confidence_prediction:
                # pred_dict["confidence"] = out.get("ablation_confidence", None)
                pred_dict["pde"] = out["pde"]
                pred_dict["plddt"] = out["plddt"]
                pred_dict["confidence_score"] = (
                    4 * out["complex_plddt"]
                    + (
                        out["iptm"]
                        if not torch.allclose(
                            out["iptm"], torch.zeros_like(out["iptm"])
                        )
                        else out["ptm"]
                    )
                ) / 5

                pred_dict["complex_plddt"] = out["complex_plddt"]
                pred_dict["complex_iplddt"] = out["complex_iplddt"]
                pred_dict["complex_pde"] = out["complex_pde"]
                pred_dict["complex_ipde"] = out["complex_ipde"]
                if self.alpha_pae > 0:
                    pred_dict["pae"] = out["pae"]
                    pred_dict["ptm"] = out["ptm"]
                    pred_dict["iptm"] = out["iptm"]
                    pred_dict["ligand_iptm"] = out["ligand_iptm"]
                    pred_dict["protein_iptm"] = out["protein_iptm"]
                    pred_dict["pair_chains_iptm"] = out["pair_chains_iptm"]

                if self.affinity_prediction:
                    pred_dict["affinity_pred_value"] = out["affinity_pred_value"]
                    pred_dict["affinity_probability_binary"] = out[
                        "affinity_probability_binary"
                    ]
                    if self.affinity_ensemble:
                        pred_dict["affinity_pred_value1"] = out["affinity_pred_value1"]
                        pred_dict["affinity_probability_binary1"] = out[
                            "affinity_probability_binary1"
                        ]
                        pred_dict["affinity_pred_value2"] = out["affinity_pred_value2"]
                        pred_dict["affinity_probability_binary2"] = out[
                            "affinity_probability_binary2"
                        ]
            self.inference_counter += 1
            return pred_dict

        except RuntimeError as e:  # catch out of memory exceptions
            if "out of memory" in str(e):
                print("| WARNING: ran out of memory, skipping batch")
                torch.cuda.empty_cache()
                return {"exception": True}
            else:
                raise e

    def configure_optimizers(self) -> torch.optim.Optimizer:
        """Configure the optimizer."""
        param_dict = dict(self.named_parameters())

        if self.structure_prediction_training:
            all_parameter_names = [
                pn for pn, p in self.named_parameters() if p.requires_grad
            ]
        else:
            all_parameter_names = [
                pn
                for pn, p in self.named_parameters()
                if p.requires_grad
                and ("out_token_feat_update" in pn or "confidence_module" in pn)
            ]

        if self.training_args.get("weight_decay", 0.0) > 0:
            w_decay = self.training_args.get("weight_decay", 0.0)
            if self.training_args.get("weight_decay_exclude", False):
                nodecay_params_names = [
                    pn
                    for pn in all_parameter_names
                    if (
                        "norm" in pn
                        or "rel_pos" in pn
                        or ".s_init" in pn
                        or ".z_init_" in pn
                        or "token_bonds" in pn
                        or "embed_atom_features" in pn
                        or "dist_bin_pairwise_embed" in pn
                    )
                ]
                nodecay_params = [param_dict[pn] for pn in nodecay_params_names]
                decay_params = [
                    param_dict[pn]
                    for pn in all_parameter_names
                    if pn not in nodecay_params_names
                ]
                optim_groups = [
                    {"params": decay_params, "weight_decay": w_decay},
                    {"params": nodecay_params, "weight_decay": 0.0},
                ]
                optimizer = torch.optim.AdamW(
                    optim_groups,
                    betas=(
                        self.training_args.adam_beta_1,
                        self.training_args.adam_beta_2,
                    ),
                    eps=self.training_args.adam_eps,
                    lr=self.training_args.base_lr,
                )

            else:
                optimizer = torch.optim.AdamW(
                    [param_dict[pn] for pn in all_parameter_names],
                    betas=(
                        self.training_args.adam_beta_1,
                        self.training_args.adam_beta_2,
                    ),
                    eps=self.training_args.adam_eps,
                    lr=self.training_args.base_lr,
                    weight_decay=self.training_args.get("weight_decay", 0.0),
                )
        else:
            optimizer = torch.optim.AdamW(
                [param_dict[pn] for pn in all_parameter_names],
                betas=(self.training_args.adam_beta_1, self.training_args.adam_beta_2),
                eps=self.training_args.adam_eps,
                lr=self.training_args.base_lr,
                weight_decay=self.training_args.get("weight_decay", 0.0),
            )

        if self.training_args.lr_scheduler == "af3":
            scheduler = AlphaFoldLRScheduler(
                optimizer,
                base_lr=self.training_args.base_lr,
                max_lr=self.training_args.max_lr,
                warmup_no_steps=self.training_args.lr_warmup_no_steps,
                start_decay_after_n_steps=self.training_args.lr_start_decay_after_n_steps,
                decay_every_n_steps=self.training_args.lr_decay_every_n_steps,
                decay_factor=self.training_args.lr_decay_factor,
            )
            return [optimizer], [
                {"scheduler": scheduler, "interval": "step"}
            ]  # TODO weian: check if this is correct
        elif self.training_args.lr_scheduler == "onecycle":
            scheduler = torch.optim.lr_scheduler.OneCycleLR(
                optimizer,
                max_lr=self.training_args.max_lr,
                total_steps=self.trainer.estimated_stepping_batches,
            )
            # return [optimizer], [{"scheduler": scheduler, "interval": "step"}]
            return {
                "optimizer": optimizer,
                "lr_scheduler": {
                    "scheduler": scheduler,
                    "interval": "step",
                },
            }

        return optimizer

    def log_image(self, name, path):
        if self.logger is not None:
            try:
                self.logger.log_image(name, images=[str(path)])
            except:
                import traceback

                traceback.print_exc()  # noqa: T201
                print(f"Image logging failed for {name} {str(path)}.")  # noqa: T201

    def on_load_checkpoint(self, checkpoint: Dict[str, Any]) -> None:
        # Ignore the lr from the checkpoint
        lr = self.training_args.max_lr
        weight_decay = self.training_args.weight_decay

        if "optimimzer_states" in checkpoint:
            for state in checkpoint["optimizer_states"]:
                for group in state["param_groups"]:
                    group["lr"] = lr
                    group["weight_decay"] = weight_decay
        if "lr_schedulers" in checkpoint:
            for scheduler in checkpoint["lr_schedulers"]:
                scheduler["max_lr"] = lr
                scheduler["base_lrs"] = [lr] * len(scheduler["base_lrs"])
                scheduler["_last_lr"] = [lr] * len(scheduler["_last_lr"])

        # Ignore the training diffusion_multiplicity and recycling steps from the checkpoint
        if "hyper_parameters" in checkpoint:
            checkpoint["hyper_parameters"]["training_args"]["max_lr"] = lr
            checkpoint["hyper_parameters"]["training_args"][
                "diffusion_multiplicity"
            ] = self.training_args.diffusion_multiplicity
            checkpoint["hyper_parameters"]["training_args"]["recycling_steps"] = (
                self.training_args.recycling_steps
            )
            checkpoint["hyper_parameters"]["training_args"]["weight_decay"] = (
                self.training_args.weight_decay
            )

        loaded = {
            k.replace(".token_transformer.", ".token_transformer_layers.0."): v
            for k, v in checkpoint["state_dict"].items()
        }

        checkpoint["state_dict"] = loaded

        # Ignore keys with different shapes
        if self.ignore_ckpt_shape_mismatch:
            state_dict = checkpoint["state_dict"]
            model_state_dict = self.state_dict()
            is_changed = False
            for k in state_dict:
                if k in model_state_dict:
                    if state_dict[k].shape != model_state_dict[k].shape:
                        print(
                            f"Skip loading parameter: {k}, "
                            f"required shape: {model_state_dict[k].shape}, "
                            f"loaded shape: {state_dict[k].shape}"
                        )
                        state_dict[k] = model_state_dict[k]
                        is_changed = True
                else:
                    print(f"Dropping parameter {k}")
                    is_changed = True

            if is_changed:
                checkpoint.pop("optimizer_states", None)

    def configure_callbacks(self) -> List[Callback]:
        """Configure model callbacks.

        Returns
        -------
        List[Callback]
            List of callbacks to be used in the model.

        """
        return [EMA(self.ema_decay)] if self.use_ema else []
