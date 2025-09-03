import multiprocessing
from pathlib import Path
from typing import Optional, Dict, Any, List
import re


from matplotlib import pyplot as plt
import rdkit

from foldeverything.task.predict.data_eval import EvalDataModule

import torch
import numpy as np
import pandas as pd
from tqdm import tqdm
import wandb

from foldeverything.data import const
from foldeverything.task.task import Task
from foldeverything.model.loss.validation import compute_subset_rmsd


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


class EvaluateFolding(Task):
    """BoltzGen evaluation pipeline."""

    def __init__(
        self,
        name: str,
        data: EvalDataModule,
        design_dir: str = None,
        num_processes: int = 1,
        native: bool = False,
        native_rmsd: bool = False,
        debug: bool = False,
        wandb: Optional[Dict[str, Any]] = None,
        all_bb_rmsd: bool = False,
        skip_specific_ids: List[str] = None,
    ) -> None:
        """Initialize the task.

        Parameters
        ----------
        use_prefolded_dir : bool,
            Compute folding metrics and assume that the folding directory exists even if predict_staks is None.
            This is not needed if the predict tasks is not None.
        """
        super().__init__()
        self.name = name
        self.num_processes = num_processes
        self.skip_specific_ids = set(skip_specific_ids or [])
        self.data = data
        self.native = native
        self.native_rmsd = native_rmsd
        self.debug = debug
        self.wandb = wandb
        self.all_bb_rmsd = all_bb_rmsd

        if design_dir is not None:
            self.init_datasets(design_dir)

        # Check that native structure is available if native metrics are desired
        if self.native and not self.data.return_native:
            raise ValueError("native=True requires return_native=True in data config.")
        if self.native_rmsd and not self.native:
            raise ValueError(
                "native_rmsd=True requires native structure (native=True)."
            )

    def init_datasets(self, design_dir):
        self.design_dir = Path(design_dir)

        self.data.init_dataset(design_dir, skip_specific_ids=self.skip_specific_ids)

        self.distogram_dir = Path(design_dir) / "distograms"
        self.distogram_dir.mkdir(exist_ok=True, parents=True)

    def compute_metrics_from_feat(self, feat, suffix=None):
        sample_id = feat["id"]
        metrics = {"id": sample_id}
        target_id = re.search(rf"{self.data.cfg.target_id_regex}", sample_id).group(1)

        # protein size (number of residues)
        metrics["prot_residues"] = (
            (feat["mol_type"] == const.chain_type_ids["PROTEIN"]).sum().item()
        )

        # density (number of atoms around each token)
        density_radii = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
        all_coords = feat["coords"][0]
        pres_coords = all_coords[feat["atom_resolved_mask"].bool()]
        center = feat["center_coords"]
        dists = torch.cdist(center, pres_coords, p=2).squeeze()
        for r in density_radii:
            counts = (dists < r).sum(1).float().mean().item()
            metrics[f"density_{r}A"] = round(counts, 3)

        # Compute RMSD between native (input) and generated conditioning structures.

        # conditioning structure does not have fake atoms, just parse the coordinates and compute rmsd.
        metrics["native_rmsd"] = 0.0
        metrics["native_rmsd_bb"] = 0.0
        if self.native_rmsd:
            cond_coords = feat["coords"]
            native_cond_coords = feat["native_coords"]
            cond_rmsd = compute_rmsd(native_cond_coords, cond_coords)

            bb_cond_coords = feat["coords"]
            bb_native_cond_coords = feat["native_coords"]
            bb_cond_rmsd = compute_rmsd(bb_native_cond_coords, bb_cond_coords)

            metrics["native_rmsd"] = cond_rmsd.item()
            metrics["native_rmsd_bb"] = bb_cond_rmsd.item()

        data = {
            "target_id": target_id,
            "sample_id": sample_id,
        }
        return metrics, data

    def compute_metrics_from_path(
        self, metadata_path, generated_path, native_path, suffix=None
    ):
        feat = self.data.predict_set.getitem_from_paths(
            metadata_path, generated_path, native_path
        )
        metrics = self.compute_metrics_from_feat(feat, suffix=suffix)
        (self.design_dir / const.folding_dirname / f"{feat['id']}.npz").unlink(
            missing_ok=True
        )
        return metrics

    def compute_metrics(self, idx, suffix=None):
        feat = self.data.predict_set[idx]
        return self.compute_metrics_from_feat(feat, suffix=suffix)

    @torch.no_grad()
    def run(self, config=None) -> tuple[Dict, Dict]:
        # Compute per instance metrics and gather predicted coordinates
        all_metrics = []
        all_data = []
        failures = 0
        # The rdkit thing is necessary to make multiprocessing with the rdkit molecules work.
        rdkit.Chem.SetDefaultPickleProperties(rdkit.Chem.PropertyPickleOptions.AllProps)
        num_processes = min(self.num_processes, multiprocessing.cpu_count())
        if num_processes == 1:
            for idx in tqdm(range(len(self.data.predict_set))):
                metrics, data = self.compute_metrics(idx)
                if metrics is not None:
                    all_metrics.append(metrics)
                    all_data.append(data)
                else:
                    failures += 1
        else:
            with multiprocessing.Pool(num_processes) as pool:  # noqa: SIM117
                with tqdm(total=len(self.data.predict_set)) as pbar:
                    for metrics, data in pool.imap_unordered(
                        self.compute_metrics, list(range(len(self.data.predict_set)))
                    ):
                        if metrics is not None:
                            all_metrics.append(metrics)
                            all_data.append(data)
                        else:
                            failures += 1
        print(f"Compute metrics failures {failures}. Successes {len(all_metrics)}")

        # Write individual metrics to disc.
        df = pd.DataFrame(all_metrics)

        csv_name = "eval_folding_metrics"
        csv_path = Path(self.design_dir) / f"{csv_name}.csv"
        df.to_csv(csv_path, float_format="%.5f", index=False)

        avg_metrics = df.mean(numeric_only=True).round(5).to_dict()
        avg_metrics["num_targets"] = len(all_metrics)

        # Log to Wandb
        if self.wandb is not None and not self.debug:
            print("\nOverall average metrics:", avg_metrics)

            wandb.init(name=self.name, **self.wandb)
            wandb.log(avg_metrics)

        return avg_metrics
