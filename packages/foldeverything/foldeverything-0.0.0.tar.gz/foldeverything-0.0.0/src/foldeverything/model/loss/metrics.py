import torch
import torch.distributed as dist
from torchmetrics.classification import AUROC, BinaryAveragePrecision
from torchmetrics.metric import Metric
from torchmetrics.regression import PearsonCorrCoef, SpearmanCorrCoef
from torchmetrics.classification import AUROC
from torchmetrics.classification import BinaryAveragePrecision
from torchmetrics.classification import BinaryAccuracy


def dim_zero_cat(x):
    """Concatenation along the zero dimension."""
    if isinstance(x, torch.Tensor):
        return x
    x = [y.unsqueeze(0) if y.numel() == 1 and y.ndim == 0 else y for y in x]
    if not x:  # empty list
        msg = "No samples to concatenate"
        raise ValueError(msg)
    return torch.cat(x, dim=0)


class TargetMetric(Metric):
    def __init__(
        self,
        name,
        mode="linear",
        ignore_single=True,
        ignore_nan=True,
        min_val=0,
        max_val=1,
    ):
        super().__init__()

        self.mode = mode
        self.ignore_single = ignore_single
        self.ignore_nan = ignore_nan
        self.name = name
        self.min_val = min_val
        self.max_val = max_val
        if name == "pearson":
            self.metric_fn = PearsonCorrCoef()
        elif name == "spearman":
            self.metric_fn = SpearmanCorrCoef()
        elif name == "auroc":
            self.metric_fn = AUROC(task="binary")
        elif name == "average_precision":
            self.metric_fn = BinaryAveragePrecision(thresholds=None)
        elif name == "precision@1%":
            self.metric_fn = lambda x, y: precision_at_k(x, y, 1)
        elif name == "precision@2%":
            self.metric_fn = lambda x, y: precision_at_k(x, y, 2)
        elif name == "precision@5%":
            self.metric_fn = lambda x, y: precision_at_k(x, y, 5)
        elif name == "precision@10%":
            self.metric_fn = lambda x, y: precision_at_k(x, y, 10)
        elif name == "precision@20%":
            self.metric_fn = lambda x, y: precision_at_k(x, y, 20)
        elif name == "enrichment@1%":
            self.metric_fn = lambda x, y: enrichment_at_k(x, y, 1)
        elif name == "enrichment@2%":
            self.metric_fn = lambda x, y: enrichment_at_k(x, y, 2)
        elif name == "enrichment@5%":
            self.metric_fn = lambda x, y: enrichment_at_k(x, y, 5)
        elif name == "enrichment@10%":
            self.metric_fn = lambda x, y: enrichment_at_k(x, y, 10)
        elif name == "enrichment@20%":
            self.metric_fn = lambda x, y: enrichment_at_k(x, y, 20)
        elif name == "difference_mae":
            self.metric_fn = lambda x, y: torch.sum(
                torch.abs(
                    (x.unsqueeze(0) - x.unsqueeze(1))
                    - (y.unsqueeze(0) - y.unsqueeze(1))
                )
                * (1 - torch.eye(x.shape[0], device=x.device, dtype=x.dtype))
            ) / torch.sum(1 - torch.eye(x.shape[0], device=x.device, dtype=x.dtype))
        elif name == "difference_accuracy_activity_cliffs@0.5":
            self.metric_fn = lambda x, y: torch.sum(
                (
                    torch.sign(x.unsqueeze(0) - x.unsqueeze(1))
                    == torch.sign(y.unsqueeze(0) - y.unsqueeze(1))
                ).float()
                * (1 - torch.eye(x.shape[0], device=x.device, dtype=x.dtype))
                * (torch.abs(x.unsqueeze(0) - x.unsqueeze(1)) > 0.5)
            ) / torch.sum(
                (1 - torch.eye(x.shape[0], device=x.device, dtype=x.dtype))
                * (torch.abs(x.unsqueeze(0) - x.unsqueeze(1)) > 0.5)
            )
            self.mask_fn = lambda x: torch.sum(
                (1 - torch.eye(x.shape[0], device=x.device, dtype=x.dtype))
                * (torch.abs(x.unsqueeze(0) - x.unsqueeze(1)) > 0.5)
            )
        elif name == "difference_accuracy_activity_cliffs@1.0":
            self.metric_fn = lambda x, y: torch.sum(
                (
                    torch.sign(x.unsqueeze(0) - x.unsqueeze(1))
                    == torch.sign(y.unsqueeze(0) - y.unsqueeze(1))
                ).float()
                * (1 - torch.eye(x.shape[0], device=x.device, dtype=x.dtype))
                * (torch.abs(x.unsqueeze(0) - x.unsqueeze(1)) > 1.0)
            ) / torch.sum(
                (1 - torch.eye(x.shape[0], device=x.device, dtype=x.dtype))
                * (torch.abs(x.unsqueeze(0) - x.unsqueeze(1)) > 1.0)
            )
            self.mask_fn = lambda x: torch.sum(
                (1 - torch.eye(x.shape[0], device=x.device, dtype=x.dtype))
                * (torch.abs(x.unsqueeze(0) - x.unsqueeze(1)) > 1.0)
            )
        elif name == "difference_accuracy_activity_cliffs@1.5":
            self.metric_fn = lambda x, y: torch.sum(
                (
                    torch.sign(x.unsqueeze(0) - x.unsqueeze(1))
                    == torch.sign(y.unsqueeze(0) - y.unsqueeze(1))
                ).float()
                * (1 - torch.eye(x.shape[0], device=x.device, dtype=x.dtype))
                * (torch.abs(x.unsqueeze(0) - x.unsqueeze(1)) > 1.5)
            ) / torch.sum(
                (1 - torch.eye(x.shape[0], device=x.device, dtype=x.dtype))
                * (torch.abs(x.unsqueeze(0) - x.unsqueeze(1)) > 1.5)
            )
            self.mask_fn = lambda x: torch.sum(
                (1 - torch.eye(x.shape[0], device=x.device, dtype=x.dtype))
                * (torch.abs(x.unsqueeze(0) - x.unsqueeze(1)) > 1.5)
            )
        elif name == "difference_accuracy_activity_cliffs@2.0":
            self.metric_fn = lambda x, y: torch.sum(
                (
                    torch.sign(x.unsqueeze(0) - x.unsqueeze(1))
                    == torch.sign(y.unsqueeze(0) - y.unsqueeze(1))
                ).float()
                * (1 - torch.eye(x.shape[0], device=x.device, dtype=x.dtype))
                * (torch.abs(x.unsqueeze(0) - x.unsqueeze(1)) > 2.0)
            ) / torch.sum(
                (1 - torch.eye(x.shape[0], device=x.device, dtype=x.dtype))
                * (torch.abs(x.unsqueeze(0) - x.unsqueeze(1)) > 2.0)
            )
            self.mask_fn = lambda x: torch.sum(
                (1 - torch.eye(x.shape[0], device=x.device, dtype=x.dtype))
                * (torch.abs(x.unsqueeze(0) - x.unsqueeze(1)) > 2.0)
            )
        elif name == "difference_accuracy":
            self.metric_fn = lambda x, y: torch.sum(
                (
                    torch.sign(x.unsqueeze(0) - x.unsqueeze(1))
                    == torch.sign(y.unsqueeze(0) - y.unsqueeze(1))
                ).float()
                * (1 - torch.eye(x.shape[0], device=x.device, dtype=x.dtype))
            ) / torch.sum(1 - torch.eye(x.shape[0], device=x.device, dtype=x.dtype))
        elif name == "difference_tolerance_score":
            self.metric_fn = lambda x, y: torch.mean(
                torch.tensor(
                    [
                        torch.sum(
                            (
                                torch.abs(
                                    (x.unsqueeze(0) - x.unsqueeze(1))
                                    - (y.unsqueeze(0) - y.unsqueeze(1))
                                )
                                < cutoff
                            ).float()
                            * (
                                1
                                - torch.eye(x.shape[0], device=x.device, dtype=x.dtype)
                            )
                        )
                        for cutoff in [0.25, 0.5, 0.75, 1.0]
                    ],
                    dtype=x.dtype,
                    device=x.device,
                )
            ) / torch.sum(1 - torch.eye(x.shape[0], device=x.device, dtype=x.dtype))
        else:
            raise NotImplementedError(f"Metric {name} not implemented")

        self.add_state("preds", default=[], dist_reduce_fx="cat")
        self.add_state("targets", default=[], dist_reduce_fx="cat")
        self.add_state("masks", default=[], dist_reduce_fx="cat")
        self.add_state("aids", default=[], dist_reduce_fx="cat")

    def update(self, preds, targets, aids, mask):
        mask = mask.reshape(-1).to(torch.bool)
        preds = preds.reshape(-1)
        # Normalize the predictions to the [0, 1] range for AUROC
        preds = (preds - self.min_val) / (self.max_val - self.min_val)
        targets = targets.reshape(-1)
        self.preds.append(preds.detach())
        self.targets.append(targets.detach())
        self.masks.append(mask)
        self.aids.append(aids.reshape(-1))

    def compute(self):
        if len(self.preds) == 0:
            return 0.0
        # Aggregate aids ids
        masks = dim_zero_cat(self.masks)
        preds = dim_zero_cat(self.preds)[masks]
        targets = dim_zero_cat(self.targets)[masks]
        aids = dim_zero_cat(self.aids)[masks]
        unique_aids = list(set(aids.tolist()))
        totals = []
        values = []
        for idx in unique_aids:
            mask = aids == idx
            if (
                self.name in ["auroc", "precision"]
                and torch.unique(targets[mask]).shape[0] == 1
            ):
                continue
            if self.name in ["auroc", "precision"] and (targets[mask] == 0).sum() < 6:
                continue
            value = self.metric_fn(preds[mask], targets[mask])
            values.append(value)
            if self.name[:35] == "difference_accuracy_activity_cliffs":
                totals.append(self.mask_fn(targets[mask]))
            else:
                totals.append(mask.sum())

        if len(totals) == 0:
            totals = torch.tensor(totals).to(preds.device)
            values = torch.tensor(values).to(preds.device)
        else:
            totals = torch.stack(totals)
            values = torch.stack(values)

        if self.ignore_single:
            mask = totals > 1
            totals = totals[mask]
            values = values[mask]
        if self.ignore_nan:
            mask = torch.isnan(values)
            totals = totals[~mask]
            values = values[~mask]

        if len(unique_aids) == 0:
            print("Warning: No value to use.")
        if len(unique_aids) > 0 and values.shape[0] / len(unique_aids) < 0.9:
            print(
                "Warning: more than 10 per cent of values in TargetMetric are NaNs or singletons."
            )
        corr = self.aggregate(values, totals, self.mode)
        return corr

    def aggregate(self, values, weights=None, mode="linear"):
        if mode == "constant":
            return values.sum() / len(values)
        if mode == "linear":
            return (values * weights).sum() / weights.sum()
        else:
            raise NotImplementedError(f"Aggregation {mode} not implemented")


class GeneralMetric(Metric):
    def __init__(self, name):
        super().__init__()

        self.name = name
        if name == "pearson":
            self.metric_fn = PearsonCorrCoef()
        elif name == "spearman":
            self.metric_fn = SpearmanCorrCoef()
        elif name == "auroc":
            self.metric_fn = AUROC(task="binary")
        elif name == "binary_accuracy":
            self.metric_fn = BinaryAccuracy()
        elif name == "average_precision":
            self.metric_fn = BinaryAveragePrecision(thresholds=None)
        else:
            raise NotImplementedError(f"Metric {name} not implemented")

        self.add_state("preds", default=[], dist_reduce_fx="cat")
        self.add_state("targets", default=[], dist_reduce_fx="cat")
        self.add_state("masks", default=[], dist_reduce_fx="cat")

    def update(self, preds, targets, mask):
        mask = mask.reshape(-1).to(torch.bool)
        preds = preds.reshape(-1)
        targets = targets.reshape(-1)
        self.preds.append(preds.detach())
        self.targets.append(targets.detach())
        self.masks.append(mask)

    def compute(self):
        if len(self.preds) == 0:
            return 0.0
        # Aggregate aids ids
        masks = dim_zero_cat(self.masks)
        if masks.sum().item() == 0:
            return 0.0
        preds = dim_zero_cat(self.preds)[masks]
        targets = dim_zero_cat(self.targets)[masks]

        return self.metric_fn(preds, targets)


class AUROCMetric(Metric):
    def __init__(self, min_val: float = 0.0, max_val: float = 1.0):
        super().__init__()

        # Save min and max values for normalization
        self.min_val = min_val
        self.max_val = max_val

        self.metric_fn = AUROC(task="binary")
        # Create states for storing predictions and true labels
        self.add_state("preds", default=[], dist_reduce_fx="cat")
        self.add_state("targets", default=[], dist_reduce_fx="cat")
        self.add_state("masks", default=[], dist_reduce_fx="cat")

    def update(self, preds: torch.Tensor, targets: torch.Tensor, masks: torch.Tensor):
        # Normalize the predictions to the [0, 1] range
        normalized_preds = (preds - self.min_val) / (self.max_val - self.min_val)

        # Ensure preds and targets are stored as lists of tensors
        self.preds.append(normalized_preds)
        self.targets.append(targets)
        self.masks.append(masks.reshape(-1).to(torch.bool))

    def compute(self):
        # Concatenate the stored lists of tensors
        if len(self.preds) == 0:
            return 0.5
        masks = dim_zero_cat(self.masks)
        if masks.sum().item() == 0:
            return 0.0
        preds = dim_zero_cat(self.preds)[masks]
        targets = dim_zero_cat(self.targets)[masks]

        # Calculate and return the AUROC
        return self.metric_fn(preds, targets)


def precision_at_k(preds, targets, k):
    """Calculate precision at k."""
    shape = preds.shape[0]
    size_subset = int(shape * k / 100)
    _, indices = torch.topk(preds, size_subset)
    return (targets[indices] == 1).sum() / size_subset


def enrichment_at_k(preds, targets, k):
    """Calculate precision at k."""
    shape = preds.shape[0]
    precision_at_k_val = precision_at_k(preds, targets, k)
    random_baseline = (targets == 1).sum() / shape
    return precision_at_k_val / random_baseline
