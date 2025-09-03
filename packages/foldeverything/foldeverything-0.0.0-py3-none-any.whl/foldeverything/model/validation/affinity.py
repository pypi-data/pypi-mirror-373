from typing import Dict, List

import torch
import torch._dynamo
from pytorch_lightning import LightningModule
from torch import nn
from torchmetrics import MeanMetric, PearsonCorrCoef
from torchmetrics.classification import BinaryAccuracy

from foldeverything.model.loss.affinity import affinity_loss
from foldeverything.model.loss.metrics import AUROCMetric, TargetMetric
from foldeverything.model.validation.validator import Validator


class AffinityValidator(Validator):
    """Validation step implementation for Affinity."""

    def __init__(
            self,
            val_names: List[str],
            confidence_prediction: bool = False,
            affinity_prediction: bool = False,
            num_affinity_val_datasets: int = 1,
    ) -> None:
        super().__init__(val_names=val_names, confidence_prediction=confidence_prediction)
        # self.val_names = val_names

        self.num_affinity_val_datasets = num_affinity_val_datasets
        if affinity_prediction:
            self.train_affinity_loss_logger = MeanMetric()
            self.train_affinity_mae_logger = MeanMetric()
            self.train_affinity_binary_accuracy_logger = BinaryAccuracy()
            self.train_affinity_binary_binders_accuracy_logger = BinaryAccuracy()
            self.train_affinity_binary_decoys_accuracy_logger = BinaryAccuracy()
            self.train_affinity_difference_mae_logger = MeanMetric()
            self.train_affinity_difference_accuracy_logger = MeanMetric()
            self.train_affinity_difference_binary_accuracy_logger = MeanMetric()

            self.val_affinity_loss_logger = nn.ModuleList(
                [MeanMetric() for _ in range(num_affinity_val_datasets)]
            )
            self.val_affinity_mae_logger = nn.ModuleList(
                [MeanMetric() for _ in range(num_affinity_val_datasets)]
            )

            self.val_affinity_binary_accuracy_value_logger = nn.ModuleList(
                [BinaryAccuracy() for _ in range(num_affinity_val_datasets)]
            )
            self.val_affinity_binary_accuracy_binary_logger = nn.ModuleList(
                [BinaryAccuracy() for _ in range(num_affinity_val_datasets)]
            )

            self.val_affinity_lin_pearson_value_target = nn.ModuleList(
                [
                    TargetMetric(name="pearson", mode="linear")
                    for _ in range(num_affinity_val_datasets)
                ]
            )
            self.val_affinity_lin_pearson_score_target = nn.ModuleList(
                [
                    TargetMetric(name="pearson", mode="linear")
                    for _ in range(num_affinity_val_datasets)
                ]
            )

            self.val_affinity_value_pearson = nn.ModuleList(
                [PearsonCorrCoef() for _ in range(num_affinity_val_datasets)]
            )
            self.val_affinity_score_pearson = nn.ModuleList(
                [PearsonCorrCoef() for _ in range(num_affinity_val_datasets)]
            )

            self.val_affinity_lin_spearman_value_target = nn.ModuleList(
                [
                    TargetMetric(name="spearman", mode="linear")
                    for _ in range(num_affinity_val_datasets)
                ]
            )
            self.val_affinity_lin_spearman_score_target = nn.ModuleList(
                [
                    TargetMetric(name="spearman", mode="linear")
                    for _ in range(num_affinity_val_datasets)
                ]
            )

            self.val_affinity_lin_auroc_value_target = nn.ModuleList(
                [
                    TargetMetric(
                        name="auroc",
                        mode="linear",
                        min_val=-10,
                        max_val=10,
                    )
                    for _ in range(num_affinity_val_datasets)
                ]
            )
            self.val_affinity_lin_auroc_binary_target = nn.ModuleList(
                [
                    TargetMetric(
                        name="auroc",
                        mode="linear",
                        min_val=0,
                        max_val=1,
                    )
                    for _ in range(num_affinity_val_datasets)
                ]
            )
            self.val_affinity_lin_auroc_score_target = nn.ModuleList(
                [
                    TargetMetric(
                        name="auroc",
                        mode="linear",
                        min_val=-100,
                        max_val=100,
                    )
                    for _ in range(num_affinity_val_datasets)
                ]
            )

            self.val_affinity_value_auroc = nn.ModuleList(
                [
                    AUROCMetric(min_val=-10, max_val=10)
                    for _ in range(num_affinity_val_datasets)
                ]
            )
            self.val_affinity_binary_auroc = nn.ModuleList(
                [
                    AUROCMetric(min_val=0, max_val=1)
                    for _ in range(num_affinity_val_datasets)
                ]
            )
            self.val_affinity_score_auroc = nn.ModuleList(
                [
                    AUROCMetric(min_val=-100, max_val=100)
                    for _ in range(num_affinity_val_datasets)
                ]
            )

            self.val_affinity_difference_mae_target = nn.ModuleList(
                [
                    TargetMetric(name="difference_mae", mode="linear")
                    for _ in range(num_affinity_val_datasets)
                ]
            )
            self.val_affinity_difference_accuracy_value_target = nn.ModuleList(
                [
                    TargetMetric(name="difference_accuracy", mode="linear")
                    for _ in range(num_affinity_val_datasets)
                ]
            )
            self.val_affinity_difference_accuracy_score_target = nn.ModuleList(
                [
                    TargetMetric(name="difference_accuracy", mode="linear")
                    for _ in range(num_affinity_val_datasets)
                ]
            )
            self.val_affinity_lin_average_precision_binary_target = nn.ModuleList(
                [
                    TargetMetric(
                        name="average_precision",
                        mode="linear",
                        min_val=0,
                        max_val=1,
                    )
                    for _ in range(num_affinity_val_datasets)
                ]
            )
            self.val_affinity_lin_precision_1_binary_target = nn.ModuleList(
                [
                    TargetMetric(
                        name="precision@1%",
                        mode="linear",
                        min_val=0,
                        max_val=1,
                    )
                    for _ in range(num_affinity_val_datasets)
                ]
            )
            self.val_affinity_lin_precision_2_binary_target = nn.ModuleList(
                [
                    TargetMetric(
                        name="precision@2%",
                        mode="linear",
                        min_val=0,
                        max_val=1,
                    )
                    for _ in range(num_affinity_val_datasets)
                ]
            )
            self.val_affinity_lin_precision_5_binary_target = nn.ModuleList(
                [
                    TargetMetric(
                        name="precision@5%",
                        mode="linear",
                        min_val=0,
                        max_val=1,
                    )
                    for _ in range(num_affinity_val_datasets)
                ]
            )
            self.val_affinity_lin_precision_10_binary_target = nn.ModuleList(
                [
                    TargetMetric(
                        name="precision@10%",
                        mode="linear",
                        min_val=0,
                        max_val=1,
                    )
                    for _ in range(num_affinity_val_datasets)
                ]
            )
            self.val_affinity_lin_precision_20_binary_target = nn.ModuleList(
                [
                    TargetMetric(
                        name="precision@20%",
                        mode="linear",
                        min_val=0,
                        max_val=1,
                    )
                    for _ in range(num_affinity_val_datasets)
                ]
            )
            self.val_affinity_lin_enrichment_1_binary_target = nn.ModuleList(
                [
                    TargetMetric(
                        name="enrichment@1%",
                        mode="linear",
                        min_val=0,
                        max_val=1,
                    )
                    for _ in range(num_affinity_val_datasets)
                ]
            )
            self.val_affinity_lin_enrichment_2_binary_target = nn.ModuleList(
                [
                    TargetMetric(
                        name="enrichment@2%",
                        mode="linear",
                        min_val=0,
                        max_val=1,
                    )
                    for _ in range(num_affinity_val_datasets)
                ]
            )
            self.val_affinity_lin_enrichment_5_binary_target = nn.ModuleList(
                [
                    TargetMetric(
                        name="enrichment@5%",
                        mode="linear",
                        min_val=0,
                        max_val=1,
                    )
                    for _ in range(num_affinity_val_datasets)
                ]
            )
            self.val_affinity_lin_enrichment_10_binary_target = nn.ModuleList(
                [
                    TargetMetric(
                        name="enrichment@10%",
                        mode="linear",
                        min_val=0,
                        max_val=1,
                    )
                    for _ in range(num_affinity_val_datasets)
                ]
            )
            self.val_affinity_lin_enrichment_20_binary_target = nn.ModuleList(
                [
                    TargetMetric(
                        name="enrichment@20%",
                        mode="linear",
                        min_val=0,
                        max_val=1,
                    )
                    for _ in range(num_affinity_val_datasets)
                ]
            )

    def process(
        self,
        model: LightningModule,
        batch: Dict[str, torch.Tensor],
        out: Dict[str, torch.Tensor],
        idx_dataset: int,
        dataloader_idx: int,
    ) -> None:
        # Take common step for folding and confidence
        self.common_val_step(model, batch, out, idx_dataset)

        # Take the affinity specific step
        self.process_affinity(model, batch, out, idx_dataset)

    def process_affinity(
        self,
        model: LightningModule,
        batch: Dict[str, torch.Tensor],
        out: Dict[str, torch.Tensor],
        idx_dataset: int
    ) -> None:
        """Run a validation step.

        Parameters
        ----------
        model : LightningModule
            The LightningModule model.
        batch : Dict[str, torch.Tensor]
            The batch input.
        out : Dict[str, torch.Tensor]
            The output of the model.

        """
        # Affinity uses another method to deal with multiple datasets
        # Get the local validation index from the global index
        # idx_dataset = self.get_local_val_index(model, idx_dataset)


        # Affinity logging
        if model.affinity_prediction:

            msg = "Affinity prediction not supported for num_ensembles_val > 1"
            assert batch["coords"].shape[1] == 1, msg

            affinity_loss_dict = affinity_loss(
                out,
                batch,
                multiplicity=1,
                # mask_loss=(
                #     batch["has_affinity"].reshape(-1)
                #     if "has_affinity" in batch
                #     else None
                # ),
                tau_affinity_score=model.tau_affinity_score,
                alpha_affinity_absolute=model.alpha_affinity_absolute,
                alpha_affinity_difference=model.alpha_affinity_difference,
                alpha_affinity_binary=model.alpha_affinity_binary,
                alpha_affinity_score_binder_decoy=model.alpha_affinity_score_binder_decoy,
                alpha_affinity_score_binder_binder=model.alpha_affinity_score_binder_binder,
                alpha_affinity_focal=model.alpha_affinity_focal,
            )

            if "idx_dataset" in batch:
                assert (
                    batch["idx_dataset"].shape[0] == 1
                    or model.num_affinity_val_datasets == 1
                )
                idx_dataset = batch["idx_dataset"][0].item()
            else:
                idx_dataset = 0

            self.val_affinity_loss_logger[idx_dataset].update(
                affinity_loss_dict["loss"],
                batch["has_affinity"].sum(),
            )
            self.val_affinity_binary_accuracy_value_logger[idx_dataset].update(
                (affinity_loss_dict["affinity_avg_pred_value"] < 1.0).long()[
                    batch["has_affinity"].bool().squeeze(1)
                ],
                batch["outcome"][batch["has_affinity"].bool()],
            )
            self.val_affinity_binary_accuracy_binary_logger[idx_dataset].update(
                (affinity_loss_dict["affinity_avg_pred_binary"] > 0.5).long()[
                    batch["has_affinity"].bool().squeeze(1)
                ],
                batch["outcome"][batch["has_affinity"].bool()],
            )
            # NOTE: we compute pearson linear, spearman linear, mae and pearson only on actives!
            self.val_affinity_mae_logger[idx_dataset].update(
                affinity_loss_dict["mae"],
                (batch["has_affinity"] * batch["outcome"]).sum(),
            )
            self.val_affinity_lin_pearson_value_target[idx_dataset].update(
                affinity_loss_dict["affinity_avg_pred_value"],
                batch["affinity"],
                batch["aid"],
                batch["has_affinity"] * batch["outcome"],
            )
            self.val_affinity_lin_pearson_score_target[idx_dataset].update(
                affinity_loss_dict["affinity_avg_pred_score"],
                batch["affinity"],
                batch["aid"],
                batch["has_affinity"] * batch["outcome"],
            )
            self.val_affinity_lin_spearman_value_target[idx_dataset].update(
                affinity_loss_dict["affinity_avg_pred_value"],
                batch["affinity"],
                batch["aid"],
                batch["has_affinity"] * batch["outcome"],
            )
            self.val_affinity_lin_spearman_score_target[idx_dataset].update(
                affinity_loss_dict["affinity_avg_pred_score"],
                batch["affinity"],
                batch["aid"],
                batch["has_affinity"] * batch["outcome"],
            )
            if (batch["has_affinity"] * batch["outcome"]).sum() > 0:
                mask_pearson = (
                    (batch["has_affinity"] * batch["outcome"]).reshape(-1).bool()
                )
                self.val_affinity_value_pearson[idx_dataset].update(
                    affinity_loss_dict["affinity_avg_pred_value"].reshape(-1)[
                        mask_pearson
                    ],
                    batch["affinity"].reshape(-1)[mask_pearson],
                )
                self.val_affinity_score_pearson[idx_dataset].update(
                    affinity_loss_dict["affinity_avg_pred_score"].reshape(-1)[
                        mask_pearson
                    ],
                    batch["affinity"].reshape(-1)[mask_pearson],
                )
            self.val_affinity_lin_auroc_value_target[idx_dataset].update(
                -affinity_loss_dict["affinity_avg_pred_value"],
                batch["outcome"],
                batch["aid"],
                batch["has_affinity"],
            )
            self.val_affinity_lin_auroc_binary_target[idx_dataset].update(
                affinity_loss_dict["affinity_avg_pred_binary"],
                batch["outcome"],
                batch["aid"],
                batch["has_affinity"],
            )
            self.val_affinity_lin_auroc_score_target[idx_dataset].update(
                -affinity_loss_dict["affinity_avg_pred_score"],
                batch["outcome"],
                batch["aid"],
                batch["has_affinity"],
            )
            self.val_affinity_difference_mae_target[idx_dataset].update(
                affinity_loss_dict["affinity_avg_pred_value"],
                batch["affinity"],
                batch["aid"],
                batch["has_affinity"] * batch["outcome"],
            )
            self.val_affinity_difference_accuracy_value_target[idx_dataset].update(
                affinity_loss_dict["affinity_avg_pred_value"],
                batch["affinity"],
                batch["aid"],
                batch["has_affinity"] * batch["outcome"],
            )
            self.val_affinity_difference_accuracy_score_target[idx_dataset].update(
                affinity_loss_dict["affinity_avg_pred_score"],
                batch["affinity"],
                batch["aid"],
                batch["has_affinity"] * batch["outcome"],
            )
            self.val_affinity_value_auroc[idx_dataset].update(
                -affinity_loss_dict["affinity_avg_pred_value"],
                batch["outcome"],
                batch["has_affinity"],
            )
            self.val_affinity_binary_auroc[idx_dataset].update(
                affinity_loss_dict["affinity_avg_pred_binary"],
                batch["outcome"],
                batch["has_affinity"],
            )
            self.val_affinity_score_auroc[idx_dataset].update(
                -affinity_loss_dict["affinity_avg_pred_score"],
                batch["outcome"],
                batch["has_affinity"],
            )
            self.val_affinity_lin_average_precision_binary_target[idx_dataset].update(
                affinity_loss_dict["affinity_avg_pred_binary"],
                batch["outcome"].long(),
                batch["aid"],
                batch["has_affinity"],
            )
            self.val_affinity_lin_precision_1_binary_target[idx_dataset].update(
                affinity_loss_dict["affinity_avg_pred_binary"],
                batch["outcome"],
                batch["aid"],
                batch["has_affinity"],
            )
            self.val_affinity_lin_precision_2_binary_target[idx_dataset].update(
                affinity_loss_dict["affinity_avg_pred_binary"],
                batch["outcome"],
                batch["aid"],
                batch["has_affinity"],
            )
            self.val_affinity_lin_precision_5_binary_target[idx_dataset].update(
                affinity_loss_dict["affinity_avg_pred_binary"],
                batch["outcome"],
                batch["aid"],
                batch["has_affinity"],
            )
            self.val_affinity_lin_precision_10_binary_target[idx_dataset].update(
                affinity_loss_dict["affinity_avg_pred_binary"],
                batch["outcome"],
                batch["aid"],
                batch["has_affinity"],
            )
            self.val_affinity_lin_precision_20_binary_target[idx_dataset].update(
                affinity_loss_dict["affinity_avg_pred_binary"],
                batch["outcome"],
                batch["aid"],
                batch["has_affinity"],
            )
            self.val_affinity_lin_enrichment_1_binary_target[idx_dataset].update(
                affinity_loss_dict["affinity_avg_pred_binary"],
                batch["outcome"],
                batch["aid"],
                batch["has_affinity"],
            )
            self.val_affinity_lin_enrichment_2_binary_target[idx_dataset].update(
                affinity_loss_dict["affinity_avg_pred_binary"],
                batch["outcome"],
                batch["aid"],
                batch["has_affinity"],
            )
            self.val_affinity_lin_enrichment_5_binary_target[idx_dataset].update(
                affinity_loss_dict["affinity_avg_pred_binary"],
                batch["outcome"],
                batch["aid"],
                batch["has_affinity"],
            )
            self.val_affinity_lin_enrichment_10_binary_target[idx_dataset].update(
                affinity_loss_dict["affinity_avg_pred_binary"],
                batch["outcome"],
                batch["aid"],
                batch["has_affinity"],
            )
            self.val_affinity_lin_enrichment_20_binary_target[idx_dataset].update(
                affinity_loss_dict["affinity_avg_pred_binary"],
                batch["outcome"],
                batch["aid"],
                batch["has_affinity"],
            )

    def on_epoch_end(self, model):
        # Take the common epoch end for folding and affinity
        self.common_on_epoch_end(model)

        # Take the affinity specific epoch end
        self.on_epoch_end_affinity(model)


    def on_epoch_end_affinity(self, model):
        if model.affinity_prediction:
            for i in range(self.num_affinity_val_datasets):
                name_idx = "" if i == 0 else "_" + str(i)
                model.log(
                    f"val/affinity_loss{name_idx}",
                    self.val_affinity_loss_logger[i].compute(),
                    prog_bar=True,
                    rank_zero_only=True,
                )
                self.val_affinity_loss_logger[i].reset()
                model.log(
                    f"val/affinity_binary_accuracy_value{name_idx}",
                    self.val_affinity_binary_accuracy_value_logger[i].compute(),
                    prog_bar=True,
                    rank_zero_only=True,
                )
                self.val_affinity_binary_accuracy_value_logger[i].reset()
                model.log(
                    f"val/affinity_binary_accuracy_binary{name_idx}",
                    self.val_affinity_binary_accuracy_binary_logger[i].compute(),
                    prog_bar=True,
                    rank_zero_only=True,
                )
                self.val_affinity_binary_accuracy_binary_logger[i].reset()

                model.log(
                    f"val/affinity_mae{name_idx}",
                    self.val_affinity_mae_logger[i].compute(),
                    prog_bar=True,
                    rank_zero_only=True,
                )
                self.val_affinity_mae_logger[i].reset()
                model.log(
                    f"val/affinity_target_pearson_value{name_idx}",
                    self.val_affinity_lin_pearson_value_target[i].compute(),
                    prog_bar=True,
                    rank_zero_only=True,
                )
                self.val_affinity_lin_pearson_value_target[i].reset()
                model.log(
                    f"val/affinity_target_pearson_score{name_idx}",
                    self.val_affinity_lin_pearson_score_target[i].compute(),
                    prog_bar=True,
                    rank_zero_only=True,
                )
                self.val_affinity_lin_pearson_score_target[i].reset()
                model.log(
                    f"val/affinity_target_spearman_value{name_idx}",
                    self.val_affinity_lin_spearman_value_target[i].compute(),
                    prog_bar=True,
                    rank_zero_only=True,
                )
                self.val_affinity_lin_spearman_value_target[i].reset()
                model.log(
                    f"val/affinity_target_spearman_score{name_idx}",
                    self.val_affinity_lin_spearman_score_target[i].compute(),
                    prog_bar=True,
                    rank_zero_only=True,
                )
                self.val_affinity_lin_spearman_score_target[i].reset()
                model.log(
                    f"val/affinity_pearson_value{name_idx}",
                    self.val_affinity_value_pearson[i].compute(),
                    prog_bar=True,
                    rank_zero_only=True,
                )
                self.val_affinity_value_pearson[i].reset()
                model.log(
                    f"val/affinity_pearson_score{name_idx}",
                    self.val_affinity_score_pearson[i].compute(),
                    prog_bar=True,
                    rank_zero_only=True,
                )
                self.val_affinity_score_pearson[i].reset()
                model.log(
                    f"val/affinity_target_auroc_value{name_idx}",
                    self.val_affinity_lin_auroc_value_target[i].compute(),
                    prog_bar=True,
                    rank_zero_only=True,
                )
                self.val_affinity_lin_auroc_value_target[i].reset()
                model.log(
                    f"val/affinity_target_auroc_binary{name_idx}",
                    self.val_affinity_lin_auroc_binary_target[i].compute(),
                    prog_bar=True,
                    rank_zero_only=True,
                )
                self.val_affinity_lin_auroc_binary_target[i].reset()
                model.log(
                    f"val/affinity_target_auroc_score{name_idx}",
                    self.val_affinity_lin_auroc_score_target[i].compute(),
                    prog_bar=True,
                    rank_zero_only=True,
                )
                self.val_affinity_lin_auroc_score_target[i].reset()
                model.log(
                    f"val/affinity_target_difference_mae{name_idx}",
                    self.val_affinity_difference_mae_target[i].compute(),
                    prog_bar=True,
                    rank_zero_only=True,
                )
                self.val_affinity_difference_mae_target[i].reset()
                model.log(
                    f"val/affinity_target_difference_accuracy_value{name_idx}",
                    self.val_affinity_difference_accuracy_value_target[i].compute(),
                    prog_bar=True,
                    rank_zero_only=True,
                )
                self.val_affinity_difference_accuracy_value_target[i].reset()
                model.log(
                    f"val/affinity_target_difference_accuracy_score{name_idx}",
                    self.val_affinity_difference_accuracy_score_target[i].compute(),
                    prog_bar=True,
                    rank_zero_only=True,
                )
                self.val_affinity_difference_accuracy_score_target[i].reset()
                model.log(
                    f"val/affinity_auroc_value{name_idx}",
                    self.val_affinity_value_auroc[i].compute(),
                    prog_bar=True,
                    rank_zero_only=True,
                )
                self.val_affinity_value_auroc[i].reset()
                model.log(
                    f"val/affinity_auroc_binary{name_idx}",
                    self.val_affinity_binary_auroc[i].compute(),
                    prog_bar=True,
                    rank_zero_only=True,
                )
                self.val_affinity_binary_auroc[i].reset()
                model.log(
                    f"val/affinity_auroc_score{name_idx}",
                    self.val_affinity_score_auroc[i].compute(),
                    prog_bar=True,
                    rank_zero_only=True,
                )
                self.val_affinity_score_auroc[i].reset()
                model.log(
                    f"val/affinity_target_average_precision_binary{name_idx}",
                    self.val_affinity_lin_average_precision_binary_target[i].compute(),
                    prog_bar=True,
                    rank_zero_only=True,
                )
                self.val_affinity_lin_average_precision_binary_target[i].reset()
                model.log(
                    f"val/affinity_target_precision_at_1_binary{name_idx}",
                    self.val_affinity_lin_precision_1_binary_target[i].compute(),
                    prog_bar=True,
                    rank_zero_only=True,
                )
                self.val_affinity_lin_precision_1_binary_target[i].reset()
                model.log(
                    f"val/affinity_target_precision_at_2_binary{name_idx}",
                    self.val_affinity_lin_precision_2_binary_target[i].compute(),
                    prog_bar=True,
                    rank_zero_only=True,
                )
                self.val_affinity_lin_precision_2_binary_target[i].reset()
                model.log(
                    f"val/affinity_target_precision_at_5_binary{name_idx}",
                    self.val_affinity_lin_precision_5_binary_target[i].compute(),
                    prog_bar=True,
                    rank_zero_only=True,
                )
                self.val_affinity_lin_precision_5_binary_target[i].reset()
                model.log(
                    f"val/affinity_target_precision_at_10_binary{name_idx}",
                    self.val_affinity_lin_precision_10_binary_target[i].compute(),
                    prog_bar=True,
                    rank_zero_only=True,
                )
                self.val_affinity_lin_precision_10_binary_target[i].reset()
                model.log(
                    f"val/affinity_target_precision_at_20_binary{name_idx}",
                    self.val_affinity_lin_precision_20_binary_target[i].compute(),
                    prog_bar=True,
                    rank_zero_only=True,
                )
                self.val_affinity_lin_precision_20_binary_target[i].reset()
                model.log(
                    f"val/affinity_target_enrichment_at_1_binary{name_idx}",
                    self.val_affinity_lin_enrichment_1_binary_target[i].compute(),
                    prog_bar=True,
                    rank_zero_only=True,
                )
                self.val_affinity_lin_enrichment_1_binary_target[i].reset()
                model.log(
                    f"val/affinity_target_enrichment_at_2_binary{name_idx}",
                    self.val_affinity_lin_enrichment_2_binary_target[i].compute(),
                    prog_bar=True,
                    rank_zero_only=True,
                )
                self.val_affinity_lin_enrichment_2_binary_target[i].reset()
                model.log(
                    f"val/affinity_target_enrichment_at_5_binary{name_idx}",
                    self.val_affinity_lin_enrichment_5_binary_target[i].compute(),
                    prog_bar=True,
                    rank_zero_only=True,
                )
                self.val_affinity_lin_enrichment_5_binary_target[i].reset()
                model.log(
                    f"val/affinity_target_enrichment_at_10_binary{name_idx}",
                    self.val_affinity_lin_enrichment_10_binary_target[i].compute(),
                    prog_bar=True,
                    rank_zero_only=True,
                )
                self.val_affinity_lin_enrichment_10_binary_target[i].reset()
                model.log(
                    f"val/affinity_target_enrichment_at_20_binary{name_idx}",
                    self.val_affinity_lin_enrichment_20_binary_target[i].compute(),
                    prog_bar=True,
                    rank_zero_only=True,
                )
                self.val_affinity_lin_enrichment_20_binary_target[i].reset()

