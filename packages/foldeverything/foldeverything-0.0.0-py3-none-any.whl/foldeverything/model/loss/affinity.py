import torch
from torch import nn
from foldeverything.model.loss.focal import binary_focal_loss_with_logits


def affinity_loss(
    model_out,
    feats,
    multiplicity=1,
    tau_affinity_score=-1.0,
    alpha_affinity_absolute=0.0,
    alpha_affinity_difference=0.0,
    alpha_affinity_binary=0.0,
    alpha_affinity_score_binder_decoy=0.0,
    alpha_affinity_score_binder_binder=0.0,
    alpha_affinity_focal=1.0,
    alpha_affinity_alpha_focal=0.8,
    alpha_affinity_gamma_focal=2.0,
    use_mae=False,
    use_uber=False,
    affinity_groups={},
    is_training=True,
):
    if is_training:
        tot_groups = int(sum(affinity_groups.values()))
        multiplicity_binary = multiplicity
        multiplicity = multiplicity * tot_groups
        affinity_groups_list = list(affinity_groups.keys())
    else:
        multiplicity_binary = 1
        multiplicity = 1
        mask_unknown = (1 - feats["affinity_template_mask"]).bool()
        affinity_groups_list = affinity_groups

    # extract necessary features
    affinity_pred_value = model_out["affinity_pred_value"].reshape(-1, multiplicity)
    affinity_pred_score = model_out["affinity_pred_score"].reshape(
        -1, multiplicity_binary
    )
    affinity_logits_binary = model_out["affinity_logits_binary"].reshape(
        -1, multiplicity_binary
    )
    if is_training:
        affinity_value = (
            feats["affinity"]
            .repeat_interleave(multiplicity, 0)
            .reshape(-1, multiplicity)
        )
        affinity_outcome = (
            feats["outcome"]
            .repeat_interleave(multiplicity_binary, 0)
            .reshape(-1, multiplicity_binary)
        )
        affinity_binary_mask = (
            feats["activity_binary_mask"]
            .repeat_interleave(multiplicity_binary, 0)
            .reshape(-1, multiplicity_binary)
        )
        affinity_value_mask = (
            feats["activity_value_mask"]
            .repeat_interleave(multiplicity, 0)
            .reshape(-1, multiplicity)
        )
        affinity_qualifier_mask = (
            feats["activity_qualifier_mask"]
            .repeat_interleave(multiplicity, 0)
            .reshape(-1, multiplicity)
        )
        aids = feats["aid"].repeat_interleave(multiplicity, 0).reshape(-1, multiplicity)
        dataset_ids = (
            feats["idx_dataset"]
            .repeat_interleave(multiplicity, 0)
            .reshape(-1, multiplicity)
        )
        aids_binary = (
            feats["aid"]
            .repeat_interleave(multiplicity_binary, 0)
            .reshape(-1, multiplicity_binary)
        )
        dataset_ids_binary = (
            feats["idx_dataset"]
            .repeat_interleave(multiplicity_binary, 0)
            .reshape(-1, multiplicity_binary)
        )
        affinity_group_mask = feats["affinity_group"].reshape(-1, multiplicity)
    else:
        affinity_value = feats["affinity"][mask_unknown].reshape(-1, 1)
        affinity_outcome = feats["outcome"][mask_unknown].reshape(-1, 1)
        affinity_value_mask = feats["activity_value_mask"][mask_unknown].reshape(-1, 1)
        affinity_binary_mask = feats["activity_binary_mask"][mask_unknown].reshape(
            -1, 1
        )
        affinity_qualifier_mask = feats["activity_qualifier_mask"][
            mask_unknown
        ].reshape(-1, 1)
        aids = feats["aid"][mask_unknown].reshape(-1, 1)
        dataset_ids = feats["idx_dataset"][mask_unknown].reshape(-1, 1)
        aids_binary = feats["aid"][mask_unknown].reshape(-1, 1)
        dataset_ids_binary = feats["idx_dataset"][mask_unknown].reshape(-1, 1)
        affinity_group_mask = feats["affinity_group"][mask_unknown].reshape(-1, 1)

    dict_out_groups = {}
    for group in affinity_groups_list:
        affinity_group_mask_idx = (affinity_group_mask == group).float()
        # Compute affinity absolute loss
        if use_mae:
            mse_loss_binders = torch.sum(
                torch.abs(affinity_pred_value - affinity_value)
                * affinity_value_mask
                * affinity_qualifier_mask
                * affinity_group_mask_idx
            )
            mse_loss_decoys = torch.sum(
                torch.abs(affinity_pred_value - affinity_value)
                * affinity_value_mask
                * (1 - affinity_qualifier_mask)
                * (affinity_pred_value.detach() < affinity_value).float()
                * affinity_group_mask_idx
            )
            mse_loss = (mse_loss_binders + mse_loss_decoys) / torch.sum(
                affinity_value_mask * affinity_qualifier_mask * affinity_group_mask_idx
                + affinity_value_mask
                * (1 - affinity_qualifier_mask)
                * (affinity_pred_value.detach() < affinity_value).float()
                * affinity_group_mask_idx
                + 1e-7
            )
        elif use_uber:
            mse_loss_binders = torch.sum(
                torch.nn.functional.huber_loss(
                    affinity_pred_value, affinity_value, reduction="none", delta=0.5
                )
                * affinity_value_mask
                * affinity_qualifier_mask
                * affinity_group_mask_idx
            )
            mse_loss_decoys = torch.sum(
                torch.nn.functional.huber_loss(
                    affinity_pred_value, affinity_value, reduction="none", delta=0.5
                )
                * affinity_value_mask
                * (1 - affinity_qualifier_mask)
                * (affinity_pred_value.detach() < affinity_value).float()
                * affinity_group_mask_idx
            )
            mse_loss = (mse_loss_binders + mse_loss_decoys) / torch.sum(
                affinity_value_mask * affinity_qualifier_mask * affinity_group_mask_idx
                + affinity_value_mask
                * (1 - affinity_qualifier_mask)
                * (affinity_pred_value.detach() < affinity_value).float()
                * affinity_group_mask_idx
                + 1e-7
            )
        else:
            mse_loss_binders = torch.sum(
                (affinity_pred_value - affinity_value) ** 2
                * affinity_value_mask
                * affinity_qualifier_mask
                * affinity_group_mask_idx
            )
            mse_loss_decoys = torch.sum(
                (affinity_pred_value - affinity_value) ** 2
                * affinity_value_mask
                * (1 - affinity_qualifier_mask)
                * (affinity_pred_value.detach() < affinity_value).float()
                * affinity_group_mask_idx
            )
            mse_loss = (mse_loss_binders + mse_loss_decoys) / torch.sum(
                affinity_value_mask * affinity_qualifier_mask * affinity_group_mask_idx
                + affinity_value_mask
                * (1 - affinity_qualifier_mask)
                * (affinity_pred_value.detach() < affinity_value).float()
                * affinity_group_mask_idx
                + 1e-7
            )

        # Compute affinity relative loss
        mask_same_aid = (
            (aids[:, None, :] == aids[None, :, :])
            * (dataset_ids[:, None, :] == dataset_ids[None, :, :])
        ).bool()
        mask_same_aid = (
            ~torch.eye(
                mask_same_aid.shape[0],
                device=mask_same_aid.device,
                dtype=mask_same_aid.dtype,
            )[:, :, None]
        ) * mask_same_aid
        mask_same_aid_and_binder_and_qualifier = (
            mask_same_aid
            * affinity_value_mask[:, None, :]
            * affinity_value_mask[None, :, :]
            * affinity_qualifier_mask[:, None, :]
            * affinity_qualifier_mask[None, :, :]
            * affinity_group_mask_idx[:, None, :]
            * affinity_group_mask_idx[None, :, :]
        )
        mask_same_aid_and_binder_and_not_qualifier = (
            mask_same_aid
            * affinity_value_mask[:, None, :]
            * affinity_value_mask[None, :, :]
            * affinity_qualifier_mask[:, None, :]
            * (1 - affinity_qualifier_mask[None, :, :])
            * affinity_group_mask_idx[:, None, :]
            * affinity_group_mask_idx[None, :, :]
        )

        affinity_difference_pred_value = (
            affinity_pred_value[:, None, :] - affinity_pred_value[None, :, :]
        )
        affinity_difference = affinity_value[:, None, :] - affinity_value[None, :, :]
        if use_mae:
            mse_difference_loss_binders = torch.sum(
                torch.abs(affinity_difference_pred_value - affinity_difference)
                * mask_same_aid_and_binder_and_qualifier
            )
            mse_difference_loss_decoys = torch.sum(
                torch.abs(affinity_difference_pred_value - affinity_difference)
                * mask_same_aid_and_binder_and_not_qualifier
                * (
                    affinity_difference_pred_value.detach() > affinity_difference
                ).float()
            )
            mse_difference_loss = (
                mse_difference_loss_binders + 2 * mse_difference_loss_decoys
            ) / (
                torch.sum(mask_same_aid_and_binder_and_qualifier)
                + 2
                * torch.sum(
                    mask_same_aid_and_binder_and_not_qualifier
                    * (
                        affinity_difference_pred_value.detach() > affinity_difference
                    ).float()
                )
                + 1e-7
            )
        elif use_uber:
            mse_difference_loss_binders = torch.sum(
                torch.nn.functional.huber_loss(
                    affinity_difference_pred_value,
                    affinity_difference,
                    reduction="none",
                    delta=0.5,
                )
                * mask_same_aid_and_binder_and_qualifier
            )
            mse_difference_loss_decoys = torch.sum(
                torch.nn.functional.huber_loss(
                    affinity_difference_pred_value,
                    affinity_difference,
                    reduction="none",
                    delta=0.5,
                )
                * mask_same_aid_and_binder_and_not_qualifier
                * (
                    affinity_difference_pred_value.detach() > affinity_difference
                ).float()
            )
            mse_difference_loss = (
                mse_difference_loss_binders + 2 * mse_difference_loss_decoys
            ) / (
                torch.sum(mask_same_aid_and_binder_and_qualifier)
                + 2
                * torch.sum(
                    mask_same_aid_and_binder_and_not_qualifier
                    * (
                        affinity_difference_pred_value.detach() > affinity_difference
                    ).float()
                )
                + 1e-7
            )
        else:
            mse_difference_loss_binders = torch.sum(
                (affinity_difference_pred_value - affinity_difference) ** 2
                * mask_same_aid_and_binder_and_qualifier
            )
            mse_difference_loss_decoys = torch.sum(
                (affinity_difference_pred_value - affinity_difference) ** 2
                * mask_same_aid_and_binder_and_not_qualifier
                * (
                    affinity_difference_pred_value.detach() > affinity_difference
                ).float()
            )
            mse_difference_loss = (
                mse_difference_loss_binders + 2 * mse_difference_loss_decoys
            ) / (
                torch.sum(mask_same_aid_and_binder_and_qualifier)
                + 2
                * torch.sum(
                    mask_same_aid_and_binder_and_not_qualifier
                    * (
                        affinity_difference_pred_value.detach() > affinity_difference
                    ).float()
                )
                + 1e-7
            )

        if group == 0:
            # TODO: change this with mask from features
            mask_binary_group_0 = affinity_binary_mask * affinity_group_mask_idx
            mask_same_aid_binary = (
                (aids_binary[:, None, :] == aids_binary[None, :, :])
                * (dataset_ids_binary[:, None, :] == dataset_ids_binary[None, :, :])
                * mask_binary_group_0[:, None, :]
                * mask_binary_group_0[None, :, :]
            ).bool()
            mask_same_aid_binary = (
                ~torch.eye(
                    mask_same_aid_binary.shape[0],
                    device=mask_same_aid_binary.device,
                    dtype=mask_same_aid_binary.dtype,
                )[:, :, None]
            ) * mask_same_aid_binary

            mask_same_aid_and_binder = (
                mask_same_aid_binary
                * affinity_outcome[:, None, :]
                * affinity_outcome[None, :, :]
            )
            mask_same_aid_and_binder_decoy = (
                mask_same_aid_binary
                * affinity_outcome[:, None, :]
                * (1 - affinity_outcome[None, :, :])
            )

            # Compute affinity binary loss
            binary_loss = torch.sum(
                torch.nn.functional.binary_cross_entropy_with_logits(
                    affinity_logits_binary, affinity_outcome, reduction="none"
                )
                * mask_binary_group_0
            ) / (torch.sum(mask_binary_group_0) + 1e-7)

            # Compute affinity score loss
            affinity_difference_score = (
                affinity_pred_score[:, None, :] - affinity_pred_score[None, :, :]
            )
            # binder, decoy loss
            affinity_target_score = torch.ones_like(affinity_difference_score)
            unreduced_score_loss_binder_decoy = (
                torch.nn.functional.binary_cross_entropy_with_logits(
                    affinity_difference_score, affinity_target_score, reduction="none"
                )
            )
            score_loss_binder_decoy = torch.sum(
                unreduced_score_loss_binder_decoy * mask_same_aid_and_binder_decoy
            ) / (torch.sum(mask_same_aid_and_binder_decoy) + 1e-7)

            # # binder, binder loss
            # affinity_target_score = nn.functional.sigmoid(
            #     affinity_difference / tau_affinity_score
            # )
            # unreduced_score_loss_binder_binder = (
            #     torch.nn.functional.binary_cross_entropy_with_logits(
            #         affinity_difference_score, affinity_target_score, reduction="none"
            #     )
            # )
            # score_loss_binder_binder = torch.sum(
            #     unreduced_score_loss_binder_binder * mask_same_aid_and_binder
            # ) / (torch.sum(mask_same_aid_and_binder) + 1e-7)

            # Compute affinity focal loss
            if alpha_affinity_focal > 0:
                focal_loss = torch.sum(
                    binary_focal_loss_with_logits(
                        affinity_logits_binary,
                        affinity_outcome,
                        alpha=alpha_affinity_alpha_focal,
                        gamma=alpha_affinity_gamma_focal,
                        reduction="none",
                    )
                    * mask_binary_group_0
                ) / (torch.sum(mask_binary_group_0) + 1e-7)
            else:
                focal_loss = 0.0

        # Compute loss affinity values
        if group == 0:
            loss_affinity_value = (
                mse_loss * alpha_affinity_absolute
                + mse_difference_loss * alpha_affinity_difference
            )
            loss_hit = (
                binary_loss * alpha_affinity_binary
                + score_loss_binder_decoy * alpha_affinity_score_binder_decoy
                # + score_loss_binder_binder * alpha_affinity_score_binder_binder
                + focal_loss * alpha_affinity_focal
            )

        else:
            loss_affinity_value = mse_loss * (
                alpha_affinity_absolute + alpha_affinity_difference
            )
            loss_hit = 0.0

        # Compute affinity loss
        loss = loss_affinity_value + loss_hit

        # Compute affinity difference metrics
        affinity_difference_mae = torch.sum(
            torch.abs(affinity_difference_pred_value - affinity_difference)
            * mask_same_aid_and_binder_and_qualifier
        ) / (torch.sum(mask_same_aid_and_binder_and_qualifier) + 1e-7)
        affinity_difference_accuracy = torch.sum(
            (
                torch.sign(affinity_difference_pred_value)
                == torch.sign(affinity_difference)
            ).float()
            * mask_same_aid_and_binder_and_qualifier
        ) / (torch.sum(mask_same_aid_and_binder_and_qualifier) + 1e-7)

        # Compute affinity avg value
        affinity_avg_pred_value = torch.mean(
            affinity_pred_value.reshape(-1, multiplicity), dim=1
        )

        # Compute affinity mae
        affinity_mae = torch.sum(
            torch.abs(affinity_pred_value - affinity_value.reshape(-1, multiplicity))
            * affinity_value_mask
            * affinity_group_mask_idx
        ) / (1e-7 + torch.sum(affinity_value_mask * affinity_group_mask_idx))

        dict_out = {
            "loss": loss,
            "affinity_pred_value": affinity_pred_value,
            "affinity_avg_pred_value": affinity_avg_pred_value,
            "mae": affinity_mae,
            "affinity_difference_mae": affinity_difference_mae,
            "affinity_difference_accuracy": affinity_difference_accuracy,
        }

        if group == 0:
            # Compute affinity difference binary accuracy metric
            affinity_difference_pred_binary = (
                affinity_logits_binary[:, None, :] - affinity_logits_binary[None, :, :]
            )
            affinity_difference_binary_accuracy = torch.sum(
                (
                    torch.sign(affinity_difference_pred_binary)
                    == torch.ones_like(affinity_difference_pred_binary)
                ).float()
                * mask_same_aid_and_binder_decoy
            ) / (torch.sum(mask_same_aid_and_binder_decoy) + 1e-7)

            # Compute binary prediction
            pred_binary = torch.nn.functional.sigmoid(affinity_logits_binary)
            pred_avg_binary = torch.mean(
                pred_binary.reshape(-1, multiplicity_binary), dim=1
            )

            # Compute affinity avg score
            affinity_avg_pred_score = tau_affinity_score * torch.mean(
                affinity_pred_score.reshape(-1, multiplicity_binary), dim=1
            )
            dict_out["affinity_difference_binary_accuracy"] = (
                affinity_difference_binary_accuracy
            )
            dict_out["affinity_avg_pred_binary"] = pred_avg_binary
            dict_out["affinity_avg_pred_score"] = affinity_avg_pred_score

        dict_out_groups[group] = dict_out

    return dict_out_groups
