import os
from pathlib import Path
from typing import Dict, List

from matplotlib import pyplot as plt
import numpy as np
import pickle
import pydssp
import torch
from pytorch_lightning import LightningModule
from torch import nn
from torchmetrics import MeanMetric

from foldeverything.data import const
from foldeverything.data.data import Structure, convert_ccd
from foldeverything.data.bond_inference import (
    infer_ligand_token_bonds,
    infer_bonds,
    rdkit_from_prediction,
    check_stability,
    check_stability_from_bonds,
)
from rdkit import Chem

from foldeverything.data.feature.af3 import (
    repopulate_res_type,
    res_from_atom14,
    res_from_atom37,
    update_ligand_atom_types_from_atom_type,
)
from foldeverything.data.write.mmcif import to_mmcif
from foldeverything.model.validation.validator import Validator
from foldeverything.model.loss.diffusion import (
    weighted_rigid_centering,
    weighted_rigid_align,
)
from foldeverything.data.pad import pad_dim
import random
import string


class DesignValidator(Validator):
    """Validation step implementation for Design."""

    def __init__(
        self,
        val_names: List[str],
        confidence_prediction: bool = False,
        atom14: bool = True,
        atom37: bool = False,
        backbone_only: bool = False,
        inverse_fold: bool = False,
        anchors_on: bool = False,
    ) -> None:
        super().__init__(
            val_names=val_names, confidence_prediction=confidence_prediction
        )
        self.backbone_only = backbone_only
        self.inverse_fold = inverse_fold
        self.anchors_on = anchors_on
        # Design Metrics
        self.seq_metric = nn.ModuleDict()
        for t in const.fake_atom_placements.keys():
            self.seq_metric[f"design_{t}"] = MeanMetric()
            self.seq_metric[f"data_{t}"] = MeanMetric()
        self.seq_metric["design_seq_recovery"] = MeanMetric()

        self.ss_metric = nn.ModuleDict()
        self.ss_metric["loop"] = MeanMetric()
        self.ss_metric["helix"] = MeanMetric()
        self.ss_metric["sheet"] = MeanMetric()

        self.ss_metric["loop_native"] = MeanMetric()
        self.ss_metric["helix_native"] = MeanMetric()
        self.ss_metric["sheet_native"] = MeanMetric()

        if self.anchors_on:
            self.anchor_metrics = {"val": nn.ModuleDict()}
            self.anchor_metrics["val"]["where_is_anchor"] = MeanMetric()
            self.anchor_metrics["val"]["well_anchored_ss"] = MeanMetric()
            self.anchor_metrics["val"]["well_anchored_ns"] = MeanMetric()
            self.anchor_metrics["val"]["anchors_percentage"] = MeanMetric()

        self.atom14 = atom14
        self.atom37 = atom37
        self.used_stems = set()

    def process(
        self,
        model: LightningModule,
        batch: Dict[str, torch.Tensor],
        out: Dict[str, torch.Tensor],
        idx_dataset: int,
        dataloader_idx: int,
        n_samples: int,
        batch_idx,
    ) -> None:
        # Take common step for folding and confidence

        if not self.inverse_fold:
            self.common_val_step(model, batch, out, idx_dataset)

        feat_masked = out["feat_masked"]

        generated_dir = f"{model.trainer.default_root_dir}/generated/epoch{model.current_epoch}_step{model.global_step}"

        self.design_val_step(
            model, batch, feat_masked, out, n_samples, batch_idx, generated_dir
        )

    def on_epoch_end(self, model):
        # Take the common epoch end for folding and affinity
        self.common_on_epoch_end(model)

        # Take the affinity specific epoch end
        self.on_epoch_end_design(model)
        self.on_epoch_end_design_anchor_log(model)

    def on_epoch_end_design_anchor_log(self, model, logname: str = "val"):
        # call with ligand too.
        if self.anchors_on:
            self.anchor_metrics[logname]["where_is_anchor"] = self.anchor_metrics[
                logname
            ]["where_is_anchor"].to(model.device)
            self.anchor_metrics[logname]["well_anchored_ss"] = self.anchor_metrics[
                logname
            ]["well_anchored_ss"].to(model.device)
            self.anchor_metrics[logname]["well_anchored_ns"] = self.anchor_metrics[
                logname
            ]["well_anchored_ns"].to(model.device)
            self.anchor_metrics[logname]["anchors_percentage"] = self.anchor_metrics[
                logname
            ]["anchors_percentage"].to(model.device)
            where_is_anchor_metrics = self.anchor_metrics[logname][
                "where_is_anchor"
            ].compute()
            model.log(
                f"{logname}/where_is_anchor", where_is_anchor_metrics, prog_bar=False
            )
            self.anchor_metrics[logname]["where_is_anchor"].reset()
            well_anchored_ss_metric = self.anchor_metrics[logname][
                "well_anchored_ss"
            ].compute()
            model.log(
                f"{logname}/well_anchored_ss",
                well_anchored_ss_metric,
                prog_bar=False,
            )
            self.anchor_metrics[logname]["well_anchored_ss"].reset()
            well_anchored_ns_metric = self.anchor_metrics[logname][
                "well_anchored_ns"
            ].compute()
            model.log(
                f"{logname}/well_anchored_ns",
                well_anchored_ns_metric,
                prog_bar=False,
            )
            self.anchor_metrics[logname]["well_anchored_ns"].reset()
            anchors_percentage_metric = self.anchor_metrics[logname][
                "anchors_percentage"
            ].compute()
            model.log(
                f"{logname}/anchors_percentage",
                anchors_percentage_metric,
                prog_bar=False,
            )
            self.anchor_metrics[logname]["anchors_percentage"].reset()

    def design_val_step(
        self,
        model: LightningModule,
        batch: Dict[str, torch.Tensor],
        feat_masked: Dict[str, torch.Tensor],
        out: Dict[str, torch.Tensor],
        n_samples: int,
        batch_idx: int,
        generated_dir: str = "generated",
        invalid_token: str = "UNK",
        logname: str = "val",
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
        for n in range(n_samples):
            # get structure for all generated coords
            sample, native = {}, {}
            for k in feat_masked.keys():
                if k == "coords":
                    sample[k] = out["sample_atom_coords"][n]
                    native[k] = batch[k][0]
                else:
                    sample[k] = feat_masked[k][0]
                    native[k] = batch[k][0]

            # Design metrics and sample writing
            try:
                atom_is_anchor = torch.matmul(
                    native["atom_to_token"].float(),
                    native["is_anchor"].float().unsqueeze(-1),
                ).squeeze(-1)
                is_anchor = atom_is_anchor[native["atom_pad_mask"].bool()]

                if self.atom14:
                    sample = res_from_atom14(sample, invalid_token=invalid_token)
                elif self.atom37:
                    sample = res_from_atom37(sample, invalid_token=invalid_token)

                # Update ligand atom types from predicted atom_type logits if available
                if "atom_type" in out and out["atom_type"] is not None:
                    atom_type_logits = out["atom_type"][n] if out["atom_type"].dim() > 2 else out["atom_type"]
                    sample = update_ligand_atom_types_from_atom_type(
                        sample, atom_type_logits
                    )

                if self.backbone_only and not self.inverse_fold:
                    sample = repopulate_res_type(sample)
                    native = repopulate_res_type(native)

                design_mask = batch["design_mask"][0].bool()
                assert design_mask.sum() == sample["design_mask"].sum()

                if self.inverse_fold:
                    token_ids = torch.argmax(sample["res_type"], dim=-1)
                    tokens = [const.tokens[i] for i in token_ids]
                    ccds = [convert_ccd(token) for token in tokens]

                    ccds = torch.tensor(ccds).to(sample["res_type"])
                    sample["ccd"][design_mask] = ccds[design_mask]

                try:
                    ligand_tokens = torch.nonzero(
                        (sample["mol_type"] == const.chain_type_ids["NONPOLYMER"])
                        & sample["design_mask"].bool()
                    ).squeeze(-1)

                    if ligand_tokens.numel() > 0:
                        infer_ligand_token_bonds(sample, update=True)
                        # single 4-letter stem for this file, unique per design dir
                        while True:
                            rand4 = "".join(random.choices(string.ascii_uppercase, k=4))
                            if rand4 not in self.used_stems:
                                self.used_stems.add(rand4)
                                break

                        atom_to_tok = torch.argmax(sample["atom_to_token"].int(), dim=-1)
                        ligand_chain_ids = torch.unique(sample["asym_id"][ligand_tokens])
                        if batch["extra_mols"] is None:
                            batch["extra_mols"] = [dict()]
                        extra_mols = batch["extra_mols"][0]

                        mol_dir = Path(generated_dir) / const.molecules_dirname
                        mol_dir.mkdir(parents=True, exist_ok=True)

                        for chain_id in ligand_chain_ids.tolist():
                            chain_letter = string.ascii_uppercase[chain_id % 26]
                            ccd = f"{rand4}{chain_letter}"
                            token_mask = (
                                (sample["asym_id"] == chain_id)
                                & (sample["mol_type"] == const.chain_type_ids["NONPOLYMER"])
                                & sample["design_mask"].bool()
                            )
                            chain_tokens = torch.nonzero(token_mask).squeeze(-1)
                            atom_mask = torch.isin(atom_to_tok, chain_tokens)

                            if atom_mask.sum() < 3:
                                print(f"Skipping chain {ccd} because it has less than 3 atoms")
                                continue
                            # build mol
                            coords_chain = sample["coords"][atom_mask]
                            elems_chain = torch.argmax(sample["ref_element"], dim=-1)[atom_mask]

                            bonds_chain = infer_bonds(coords_chain, elems_chain)
                            mol = rdkit_from_prediction(coords_chain, elems_chain, bonds_chain)

                            # ---- Ligand validity metrics ----
                            if Chem is not None and mol is not None:
                                try:
                                    Chem.SanitizeMol(mol)
                                    rdkit_valid = True
                                except Exception:
                                    rdkit_valid = False
                            else:
                                rdkit_valid = False

                            model.log(
                                "val/ligand_rdkit_valid",
                                float(rdkit_valid),
                                prog_bar=False,
                                sync_dist=True,
                            )

                            if bonds_chain.numel() > 0:
                                mol_ok, n_ok, n_atoms = check_stability_from_bonds(
                                    elems_chain, bonds_chain
                                )
                            else:
                                mol_ok, n_ok, n_atoms = False, 0, elems_chain.numel()

                            model.log(
                                "val/ligand_mol_stable",
                                float(mol_ok),
                                prog_bar=False,
                                sync_dist=True,
                            )
                            model.log(
                                "val/ligand_atom_stable",
                                n_ok / max(n_atoms, 1),
                                prog_bar=False,
                                sync_dist=True,
                            )

                            # Write CCD back into sample so it ends up in the mmCIF
                            sample["ccd"][chain_tokens] = torch.tensor(
                                convert_ccd(ccd), device=sample["ccd"].device
                            )

                            extra_mols[ccd] = mol
                            with open(mol_dir / f"{ccd}.pkl", "wb") as fh:
                                pickle.dump(mol, fh)
                except Exception as e:
                    print(f"[design_val_step] RDKit mol generation failed: {e}")

                structure, _, _ = Structure.from_feat(sample)
                str_native, _, _ = Structure.from_feat(native)
                nonanchor_sample = Structure.extract_atoms(
                    structure, is_anchor.cpu() == 0
                )
                nonanchor_native = Structure.extract_atoms(
                    str_native, is_anchor.cpu() == 0
                )

                if (nonanchor_sample.residues["name"] == "").any():
                    msg = f"{nonanchor_sample.residues}\n\nThere were residues with empty residue names when writing mmcif files. Are you sure that any of the atom14, atom37, backbone_only, or inverse_fold are set?"
                    raise Exception(msg)

                # Write structure to cif
                os.makedirs(generated_dir, exist_ok=True)
                basename = f"{generated_dir}/sample{n}_batch{batch_idx}_rank{model.trainer.global_rank}_{batch['id'][0]}"
                gen_path = f"{basename}_gen.cif"
                native_path = f"{basename}_native.cif"

                atom_design_mask = (
                    sample["atom_to_token"].float()
                    @ sample["design_mask"].unsqueeze(-1).float()
                )
                atom_design_mask = atom_design_mask.squeeze().bool()
                bfactor = atom_design_mask[
                    (atom_is_anchor == 0) & sample["atom_pad_mask"].bool()
                ].float()
                nonanchor_sample.atoms["bfactor"] = bfactor.cpu().numpy()
                nonanchor_native.atoms["bfactor"] = bfactor.cpu().numpy()

                # Add dummy (0-coord) design side chains if inverse fold
                if self.inverse_fold:
                    atom_design_mask_no_pad = atom_design_mask[
                        native["atom_pad_mask"].bool()
                    ]
                    res_design_mask = np.array(
                        [
                            all(
                                atom_design_mask_no_pad[
                                    res["atom_idx"] : res["atom_idx"] + res["atom_num"]
                                ]
                            )
                            for res in structure.residues
                        ]
                    )
                    structure = Structure.add_side_chains(
                        structure, residue_mask=res_design_mask
                    )
                open(gen_path, "w").write(to_mmcif(nonanchor_sample))
                open(native_path, "w").write(to_mmcif(nonanchor_native))

                # Write metadata
                metadata_path = f"{basename}_metadata.npz"
                np.savez_compressed(
                    metadata_path,
                    design_mask=design_mask[
                        sample["token_pad_mask"].bool() & ~sample["is_anchor"].bool()
                    ]
                    .cpu()
                    .numpy(),
                    mol_type=sample["mol_type"][
                        sample["token_pad_mask"].bool() & ~sample["is_anchor"].bool()
                    ]
                    .cpu()
                    .numpy(),
                    native_atom_design_mask=atom_design_mask[
                        ~native["fake_atom_mask"].bool() & (atom_is_anchor == 0)
                    ]
                    .cpu()
                    .numpy(),
                    design_atom_design_mask=atom_design_mask[
                        ~sample["fake_atom_mask"].bool() & (atom_is_anchor == 0)
                    ]
                    .cpu()
                    .numpy(),
                )

                # Compute metrics
                design_mask = sample["design_mask"].bool()
                if design_mask.sum() > 5:
                    # Compute res type distribution
                    design_seq = torch.argmax(sample["res_type"], dim=-1)[design_mask]
                    true_seq = torch.argmax(native["res_type"], dim=-1)[design_mask]
                    self.seq_metric["design_seq_recovery"].update(
                        (design_seq == true_seq).float().mean()
                    )
                    for t in const.fake_atom_placements.keys():
                        self.seq_metric[f"design_{t}"].update(
                            (design_seq == const.token_ids[t]).float().mean()
                        )
                        self.seq_metric[f"data_{t}"].update(
                            (true_seq == const.token_ids[t]).float().mean()
                        )

                    # Compute secondary structure distribution. First get backbone then use pydssp to compute.
                    bb_design_mask = (
                        sample["atom_pad_mask"].bool()
                        & atom_design_mask
                        & sample["backbone_mask"].bool()
                    )
                    bb = sample["coords"][bb_design_mask].reshape(-1, 4, 3)
                    bb_native = native["coords"][0][bb_design_mask].reshape(-1, 4, 3)

                    # Run DSSP only if at least two backbone residues are present

                    if bb.shape[0] >= 2:
                        # 0: loop,  1: alpha-helix,  2: beta-strand
                        dssp = pydssp.assign(bb, out_type="index")
                        self.ss_metric["loop"].update((dssp == 0).float().mean())
                        self.ss_metric["helix"].update((dssp == 1).float().mean())
                        self.ss_metric["sheet"].update((dssp == 2).float().mean())

                        dssp_native = pydssp.assign(bb_native, out_type="index")
                        self.ss_metric["loop_native"].update(
                            (dssp_native == 0).float().mean()
                        )
                        self.ss_metric["helix_native"].update(
                            (dssp_native == 1).float().mean()
                        )
                        self.ss_metric["sheet_native"].update(
                            (dssp_native == 2).float().mean()
                        )

                    # Compute anchored metric
                    if self.anchors_on and logname != "val_monomer":
                        if sample["is_anchor"].sum() > 0:
                            self.anchor_metrics[logname]["where_is_anchor"] = (
                                self.anchor_metrics[logname]["where_is_anchor"].to(
                                    model.device
                                )
                            )
                            self.anchor_metrics[logname]["well_anchored_ns"] = (
                                self.anchor_metrics[logname]["well_anchored_ns"].to(
                                    model.device
                                )
                            )
                            self.anchor_metrics[logname]["well_anchored_ss"] = (
                                self.anchor_metrics[logname]["well_anchored_ss"].to(
                                    model.device
                                )
                            )
                            self.anchor_metrics[logname]["anchors_percentage"] = (
                                self.anchor_metrics[logname]["anchors_percentage"].to(
                                    model.device
                                )
                            )
                            anchor_dev = 0
                            well_anchor_dist_ss = 0
                            well_anchor_dist_ns = 0
                            align_with_anchor = (
                                native["structure_group"]
                                == native["structure_group"][native["is_anchor"] == 1][
                                    0
                                ]
                            )
                            atom_align_mask = (
                                torch.matmul(
                                    native["atom_to_token"].float(),
                                    align_with_anchor.int().float().unsqueeze(-1),
                                )
                                .squeeze(-1)
                                .bool()
                            )
                            atom_align_mask = atom_align_mask.bool() & ~(
                                native["fake_atom_mask"].bool()
                            )
                            native["coords"] = weighted_rigid_align(
                                native["coords"],
                                sample["coords"].unsqueeze(0),
                                torch.ones(
                                    sample["coords"].shape[0],
                                    device=sample["coords"].device,
                                ).unsqueeze(0),
                                atom_align_mask.unsqueeze(0),
                            )
                            for i in range(len(native["is_anchor"])):
                                if native["is_anchor"][i] == 0:
                                    continue
                                anchor_idx = torch.argmax(
                                    native["token_to_rep_atom"][i].int()
                                )
                                anchor_coords_native = native["coords"][0][anchor_idx]
                                anchor_coords_sample = sample["coords"][anchor_idx]
                                anchor_dev_inc = torch.cdist(
                                    anchor_coords_native.unsqueeze(0),
                                    anchor_coords_sample.unsqueeze(0),
                                ).min()
                                anchor_charge = native["ref_charge"][anchor_idx]
                                anchor_element = torch.argmax(
                                    native["ref_element"][anchor_idx]
                                )
                                sample_real_atom_mask = (
                                    sample["is_anchor"][
                                        torch.where(sample["atom_to_token"])[1]
                                    ]
                                    == 0
                                )
                                sample_real_atom_mask = pad_dim(
                                    sample_real_atom_mask,
                                    False,
                                    len(sample["coords"]) - len(sample_real_atom_mask),
                                )
                                sample_same_element_mask = (
                                    torch.argmax(sample["ref_element"], dim=-1)
                                    == anchor_element
                                )
                                sample_same_charge_mask = (
                                    sample["ref_charge"] == anchor_charge
                                )
                                sample_same_mask = (
                                    sample_same_element_mask
                                    & sample_same_charge_mask
                                    & sample_real_atom_mask
                                )
                                sample_same_coords = sample["coords"][sample_same_mask]
                                anchor_dev += anchor_dev_inc
                                if sample_same_coords.shape[0] == 0:
                                    continue
                                min_dist_ss = torch.cdist(
                                    sample_same_coords,
                                    anchor_coords_sample.unsqueeze(0),
                                ).min()
                                min_dist_ns = torch.cdist(
                                    sample_same_coords,
                                    anchor_coords_native.unsqueeze(0),
                                ).min()
                                well_anchor_dist_ss += min_dist_ss
                                well_anchor_dist_ns += min_dist_ns

                            anchor_dev /= native["is_anchor"].sum()
                            well_anchor_dist_ss /= native["is_anchor"].sum()
                            well_anchor_dist_ns /= native["is_anchor"].sum()
                            self.anchor_metrics[logname]["where_is_anchor"].update(
                                anchor_dev
                            )
                            self.anchor_metrics[logname]["well_anchored_ss"].update(
                                well_anchor_dist_ss
                            )
                            self.anchor_metrics[logname]["well_anchored_ns"].update(
                                well_anchor_dist_ns
                            )
                            self.anchor_metrics[logname]["anchors_percentage"].update(1)
                        else:
                            self.anchor_metrics[logname]["anchors_percentage"].update(0)



                return True
            except Exception as e:  # noqa: BLE001
                import traceback

                traceback.print_exc()  # noqa: T201
                print(
                    f"Validation structure writing failed on {batch['id'][0]} with error {e}. Skipping."
                )  # noqa: T201
                return False

    def on_epoch_end_design(self, model, logname: str = "val"):
        # Design Metrics
        # compute residue distribution metrics
        design_freqs = []
        data_freqs = []
        for t in const.fake_atom_placements.keys():
            design_freqs.append(self.seq_metric[f"design_{t}"].compute().cpu())
            data_freqs.append(self.seq_metric[f"data_{t}"].compute().cpu())
            model.log(
                f"{logname}/design_seq_recovery",
                self.seq_metric["design_seq_recovery"].compute(),
                prog_bar=False,
            )
        for v in self.seq_metric.values():
            v.reset()

        # Make residue distribution plot
        x = np.arange(len(const.fake_atom_placements.keys()))
        width = 0.15
        _, ax = plt.subplots(figsize=(12, 6))
        ax.bar(x - width / 2, design_freqs, width, label="Design frequency")
        ax.bar(x + width / 2, data_freqs, width, label="Data frequency")
        ax.set_xlabel("Res Type")
        ax.set_ylabel("Probability")
        ax.set_title("Res Type distributions")
        ax.set_xticks(x)
        ax.set_xticklabels(const.fake_atom_placements.keys())
        ax.legend()
        ax.grid(True, which="both", axis="y", linestyle="--", linewidth=0.5)
        plt.tight_layout()

        img_dir = Path(f"{model.trainer.default_root_dir}/images")
        img_dir.mkdir(exist_ok=True)
        plt.savefig(img_dir / f"res_dist{model.current_epoch}.png")
        plt.close()
        model.log_image(
            f"{logname}/res_dist", img_dir / f"res_dist{model.current_epoch}.png"
        )

        # Compute secondary structure distribution and log
        ss_dist = []
        ss_dist_native = []
        for k, v in self.ss_metric.items():
            metric = v.compute().cpu()
            model.log(f"{logname}/{k}", metric, prog_bar=False)
            if "_native" in k:
                ss_dist_native.append(metric)
            else:
                ss_dist.append(metric)
        for v in self.ss_metric.values():
            v.reset()

        # Make secondary structure distribution plot
        x = np.arange(3)
        width = 0.15
        _, ax = plt.subplots(figsize=(12, 6))
        ax.bar(x - width / 2, ss_dist, width, label="Designed")
        ax.bar(x + width / 2, ss_dist_native, width, label="Native data")
        ax.set_xlabel("Secondary Structure type")
        ax.set_ylabel("Frequency")
        ax.set_title("Secondary Structure distributions")
        ax.set_xticks(x)
        ax.set_xticklabels(["loop", "helix", "sheet"])
        ax.legend()
        ax.grid(True, which="both", axis="y", linestyle="--", linewidth=0.5)
        plt.tight_layout()

        img_dir = Path(f"{model.trainer.default_root_dir}/images")
        img_dir.mkdir(exist_ok=True)
        plt.savefig(img_dir / f"ss_dist{model.current_epoch}.png")
        plt.close()
        self.log_image(
            f"{logname}/ss_dist", img_dir / f"ss_dist{model.current_epoch}.png", model
        )

    def log_image(self, name, path, model):
        if model.logger is not None:
            try:
                model.logger.log_image(name, images=[str(path)])
            except:
                import traceback

                traceback.print_exc()  # noqa: T201
                print(f"Image logging failed for {name} {str(path)}.")  # noqa: T201
