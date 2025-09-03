import json
import pickle
from dataclasses import asdict, replace
from pathlib import Path
from typing import Dict, List, Literal, Union

import numpy as np
import torch
from pytorch_lightning import LightningModule, Trainer
from pytorch_lightning.callbacks import BasePredictionWriter
from sklearn.neighbors import KDTree
from torch import Tensor
from tqdm import tqdm
import random
import string

from foldeverything.data import const
from foldeverything.data.data import (
    Atom,
    Bond,
    Chain,
    ConfidenceInfo,
    Coords,
    Ensemble,
    Interface,
    InterfaceInfo,
    Record,
    Residue,
    Structure,
    StructureInfo,
    convert_ccd,
)
from foldeverything.data.feature.af3 import (
    res_from_atom14,
    res_from_atom37,
    update_ligand_atom_types_from_atom_type,
)
from foldeverything.data.write.mmcif import to_mmcif
from foldeverything.data.write.pdb import to_pdb
from foldeverything.model.loss.diffusion import weighted_rigid_align
from foldeverything.model.modules.masker import BoltzMasker
from foldeverything.data.write.utils import generate_tags
from foldeverything.data.bond_inference import (
    infer_ligand_token_bonds,
    infer_bonds,
    rdkit_from_prediction,
)


def remove_masked_and_expand_assembly(
    structure: Structure,
) -> Structure:  # noqa: C901, PLR0915
    """Remove masked chains and expand the assembly.

    Parameters
    ----------
    structure : Structure
        The structure to process.

    Returns
    -------
    Structure
        The structure with masked chains removed.

    """
    entity_counter = {}
    atom_idx, res_idx, chain_idx = 0, 0, 0
    atoms, residues, chains = [], [], []
    atom_map, res_map, chain_map = {}, {}, {}
    for i, chain in enumerate(structure.chains):
        # Skip masked chains
        if not structure.mask[i]:
            continue

        # Update entity counter
        entity_id = chain["entity_id"]
        if entity_id not in entity_counter:
            entity_counter[entity_id] = 0
        else:
            entity_counter[entity_id] += 1

        # Update the chain
        new_chain = chain.copy()
        new_chain["atom_idx"] = atom_idx
        new_chain["res_idx"] = res_idx
        new_chain["asym_id"] = chain_idx
        new_chain["sym_id"] = entity_counter[entity_id]

        chains.append(
            (
                str(chain_idx),
                chain["mol_type"].copy(),
                chain["entity_id"].copy(),
                entity_counter[entity_id],
                chain_idx,
                atom_idx,
                chain["atom_num"].copy(),
                res_idx,
                chain["res_num"].copy(),
            )
        )
        chain_map[i] = chain_idx
        chain_idx += 1

        # Add the chain residues
        res_start = chain["res_idx"]
        res_end = chain["res_idx"] + chain["res_num"]
        for j, res in enumerate(structure.residues[res_start:res_end]):
            # Update the residue
            new_res = res.copy()
            new_res["atom_idx"] = atom_idx
            new_res["atom_center"] = atom_idx + new_res["atom_center"] - res["atom_idx"]
            new_res["atom_disto"] = atom_idx + new_res["atom_disto"] - res["atom_idx"]
            residues.append(new_res)
            res_map[res_start + j] = res_idx
            res_idx += 1

            # Update the atoms
            start = res["atom_idx"]
            end = res["atom_idx"] + res["atom_num"]
            atoms.append(structure.atoms[start:end])
            atom_map.update({k: atom_idx + k - start for k in range(start, end)})
            atom_idx += res["atom_num"]

    # Concatenate the tables
    atoms = np.concatenate(atoms, dtype=Atom)
    residues = np.array(residues, dtype=Residue)
    chains = np.array(chains, dtype=Chain)

    # Update connections
    bonds = []
    for bond in structure.bonds:
        chain_1 = bond["chain_1"]
        chain_2 = bond["chain_2"]
        res_1 = bond["res_1"]
        res_2 = bond["res_2"]
        atom_1 = bond["atom_1"]
        atom_2 = bond["atom_2"]
        if (atom_1 in atom_map) and (atom_2 in atom_map):
            new_bond = bond.copy()
            new_bond["chain_1"] = chain_map[chain_1]
            new_bond["chain_2"] = chain_map[chain_2]
            new_bond["res_1"] = res_map[res_1]
            new_bond["res_2"] = res_map[res_2]
            new_bond["atom_1"] = atom_map[atom_1]
            new_bond["atom_2"] = atom_map[atom_2]
            bonds.append(new_bond)

    # Update interfaces
    interfaces = []
    for interface in structure.interfaces:
        chain_1 = interface["chain_1"]
        chain_2 = interface["chain_2"]
        if (chain_1 in chain_map) and (chain_2 in chain_map):
            new_interface = interface.copy()
            new_interface["chain_1"] = chain_map[chain_1]
            new_interface["chain_2"] = chain_map[chain_2]
            interfaces.append(new_interface)

    # Create arrays
    bonds = np.array(bonds, dtype=Bond)
    interfaces = np.array(interfaces, dtype=Interface)

    # Update ensemble atoms["coords"]
    coordinates = np.array(atoms["coords"][:, None], dtype=Coords)
    ensemble = np.array([(0, len(atoms["coords"]))], dtype=Ensemble)

    return Structure(
        atoms=atoms,
        bonds=bonds,
        residues=residues,
        chains=chains,
        interfaces=interfaces,
        mask=np.ones(len(chains), dtype=bool),
        coords=coordinates,
        ensemble=ensemble,
    )


def compute_interfaces(atom_data: np.ndarray, chain_data: np.ndarray) -> np.ndarray:
    """Compute the chain-chain interfaces from a gemmi structure.

    Parameters
    ----------
    atom_data : List[Tuple]
        The atom data.
    chain_data : List[Tuple]
        The chain data.

    Returns
    -------
    List[Tuple[int, int]]
        The interfaces.

    """
    # Compute chain_id per atom
    chain_ids = []
    for idx, chain in enumerate(chain_data):
        chain_ids.extend([idx] * chain["atom_num"])
    chain_ids = np.array(chain_ids)

    # Filte to present atoms
    coords = atom_data["coords"]
    mask = atom_data["is_present"]

    coords = coords[mask]
    chain_ids = chain_ids[mask]

    # Compute the distance matrix
    tree = KDTree(coords, metric="euclidean")
    query = tree.query_radius(coords, const.atom_interface_cutoff)

    # Get unique chain pairs
    interfaces = set()
    for c1, pairs in zip(chain_ids, query):
        chains = np.unique(chain_ids[pairs])
        chains = chains[chains != c1]
        interfaces.update((c1, c2) for c2 in chains)

    # Get unique chain pairs
    interfaces = [(min(i, j), max(i, j)) for i, j in interfaces]
    interfaces = list({(int(i), int(j)) for i, j in interfaces})
    interfaces = np.array(interfaces, dtype=Interface)
    return interfaces


class FoldEverythingWriter(BasePredictionWriter):
    """Custom writer for predictions."""

    def __init__(
        self,
        data_dir: str,
        output_dir: str,
        compute_interfaces: bool = False,
        output_format: Union[
            Literal["pdb", "mmcif", "custom", "dict"], List
        ] = "custom",
        ignore_covalent: bool = False,
    ) -> None:
        """Initialize the writer.

        Parameters
        ----------
        output_dir : str
            The directory to save the predictions.

        """
        super().__init__(write_interval="batch")
        if isinstance(output_format, str):
            if output_format not in ["pdb", "mmcif", "custom", "dict"]:
                msg = f"Invalid output format: {output_format}"
                raise ValueError(msg)
            else:
                output_format = [output_format]
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.output_format = output_format
        self.structure_dir = self.output_dir / "structures"
        self.record_dir = self.output_dir / "records"
        self.dict_dir = self.output_dir / "dicts"
        self.compute_interfaces = compute_interfaces
        self.ignore_covalent = ignore_covalent
        self.failed = 0

        # Create the output directories
        self.output_dir.mkdir(parents=True, exist_ok=True)
        if "dict" in self.output_format:
            self.dict_dir.mkdir(parents=True, exist_ok=True)
        else:
            self.structure_dir.mkdir(parents=True, exist_ok=True)
            self.record_dir.mkdir(parents=True, exist_ok=True)

    def write_on_batch_end(  # noqa: PLR0915
        self,
        trainer: Trainer,  # noqa: ARG002
        pl_module: LightningModule,  # noqa: ARG002
        prediction: Dict[str, Tensor],
        batch_indices: List[int],  # noqa: ARG002
        batch: Dict[str, Tensor],
        batch_idx: int,  # noqa: ARG002
        dataloader_idx: int,  # noqa: ARG002
    ) -> None:
        """Write the predictions to disk."""
        # Check for exceptions
        if "dict" in self.output_format:
            for i, record in enumerate(batch["record"]):
                pred_dict = {}
                for key, value in prediction.items():
                    # check object is tensor
                    if key == "exception":
                        pass
                    elif isinstance(value, Tensor):
                        pred_dict[key] = value[i].cpu().numpy()
                    else:
                        pred_dict[key] = value[i]
                with open(self.output_dir / "dicts" / f"{record.id}.pkl", "wb") as f:
                    pickle.dump(pred_dict, f)

        if prediction["exception"]:
            self.failed += 1
            return

        # Get the records
        records: List[Record] = batch["record"]

        # Get the predictions
        coords = prediction["coords"]
        pad_masks = prediction["atom_pad_mask"]

        # TODO: coords should have shape (BATCH_SIZE, NUM_SAMPLES, NUM_ATOMS, 3)
        # but currently has shape (BATCH_SIZE * NUM_SAMPLES, NUM_ATOMS, 3)
        # temp fix just to get this running but needs to be properly fixed.
        coords = coords.unsqueeze(0)

        # Iterate over the records
        for record, coord, pad_mask in zip(records, coords, pad_masks):
            # Load the structure
            path = self.data_dir / f"structures/{record.id}.npz"
            structure: Structure = Structure.load(path)

            # Mask glycans
            if self.ignore_covalent:
                for i, chain in enumerate(structure.chains):
                    if (
                        chain["mol_type"] == const.chain_type_ids["NONPOLYMER"]
                    ) and chain["res_num"] > 1:
                        structure.mask[i] = False

            # Compute chain map with masked removed, to be used later
            chain_map = {}
            for i, mask in enumerate(structure.mask):
                if mask:
                    chain_map[len(chain_map)] = i

            # Remove masked chains completely
            structure = remove_masked_and_expand_assembly(structure)

            # Get ranking
            # NOTE: we do not support batch_size > 1
            if "confidence_score" in prediction:
                argsort = torch.argsort(prediction["confidence_score"], descending=True)
                idx_to_rank = {idx.item(): rank for rank, idx in enumerate(argsort)}
            else:
                print("Warning: running without confidence prediction.")
                idx_to_rank = {i: i for i in range(coord.shape[0])}

            for model_idx in range(coord.shape[0]):
                # Get model coord
                model_coord = coord[model_idx]
                # Unpad
                coord_unpad = model_coord[pad_mask.bool()]
                coord_unpad = coord_unpad.cpu().numpy()

                # New atom table
                atoms = structure.atoms
                atoms["coords"] = coord_unpad
                atoms["is_present"] = True

                # Mew residue table
                residues = structure.residues
                residues["is_present"] = True

                # New ensemble tables
                coordinates = np.array(
                    [(coord,) for coord in coord_unpad.tolist()], dtype=Coords
                )
                ensemble = np.array([(0, len(atoms["coords"]))], dtype=Ensemble)

                # Update the structure
                interfaces = np.array([], dtype=Interface)
                new_structure: Structure = replace(
                    structure,
                    atoms=atoms,
                    residues=residues,
                    interfaces=interfaces,
                    coords=coordinates,
                    ensemble=ensemble,
                )

                # Compute the interfaces
                if self.compute_interfaces:
                    interfaces = compute_interfaces(
                        new_structure.atoms,
                        new_structure.chains,
                    )
                    new_structure = replace(new_structure, interfaces=interfaces)

                # Update structure info
                structure_info = StructureInfo(
                    resolution=0.0,
                    method="prediction",
                    num_chains=len(new_structure.chains),
                    num_interfaces=len(interfaces),
                )

                # Update chain info
                chain_info = []
                for chain in new_structure.chains:
                    old_chain_idx = chain_map[chain["asym_id"]]
                    old_chain_info = record.chains[old_chain_idx]
                    new_chain_info = replace(
                        old_chain_info,
                        chain_id=int(chain["asym_id"]),
                        valid=True,
                    )
                    chain_info.append(new_chain_info)

                # Update interface info
                interface_info = []
                for i, j in interfaces:
                    new_interface_info = InterfaceInfo(i.item(), j.item(), valid=True)
                    interface_info.append(new_interface_info)

                # Replace confidence info
                # TODO: we do not support batch_size > 1
                if "confidence_score" in prediction:
                    pair_chains_iptm = {
                        idx1: {
                            idx2: prediction["pair_chains_iptm"][idx1][idx2][
                                model_idx
                            ].item()
                            for idx2 in prediction["pair_chains_iptm"][idx1]
                        }
                        for idx1 in prediction["pair_chains_iptm"]
                    }
                    chains_ptm = {
                        idx: prediction["pair_chains_iptm"][idx][idx][model_idx].item()
                        for idx in prediction["pair_chains_iptm"]
                    }
                    confidence_info = ConfidenceInfo(
                        confidence_score=prediction["confidence_score"][
                            model_idx
                        ].item(),
                        ptm=prediction["ptm"][model_idx].item(),
                        iptm=prediction["iptm"][model_idx].item(),
                        ligand_iptm=prediction["ligand_iptm"][model_idx].item(),
                        protein_iptm=prediction["protein_iptm"][model_idx].item(),
                        complex_plddt=prediction["complex_plddt"][model_idx].item(),
                        complex_iplddt=prediction["complex_iplddt"][model_idx].item(),
                        complex_pde=prediction["complex_pde"][model_idx].item(),
                        complex_ipde=prediction["complex_ipde"][model_idx].item(),
                        chains_ptm=chains_ptm,
                        pair_chains_iptm=pair_chains_iptm,
                    )
                else:
                    confidence_info = ConfidenceInfo()

                # Update the record
                new_record: Record = replace(
                    record,
                    structure=structure_info,
                    chains=chain_info,
                    interfaces=interface_info,
                    confidence=confidence_info,
                )
                # Save the structure and records
                record_dir = self.output_dir / "records" / record.id
                struct_dir = self.output_dir / "structures" / record.id

                record_dir.mkdir(exist_ok=True)
                struct_dir.mkdir(exist_ok=True)

                record_path = (
                    record_dir / f"{record.id}_model_{idx_to_rank[model_idx]}.json"
                )  # noqa: E501
                with record_path.open("w") as f:
                    json.dump(asdict(new_record), f)

                if "pdb" in self.output_format:
                    path = (
                        struct_dir / f"{record.id}_model_{idx_to_rank[model_idx]}.pdb"
                    )  # noqa: E501
                    with path.open("w") as f:
                        f.write(to_pdb(new_structure))
                if "mmcif" in self.output_format:
                    path = (
                        struct_dir / f"{record.id}_model_{idx_to_rank[model_idx]}.cif"
                    )  # noqa: E501
                    with path.open("w") as f:
                        f.write(to_mmcif(new_structure))
                if "custom" in self.output_format:
                    path = (
                        struct_dir / f"{record.id}_model_{idx_to_rank[model_idx]}.npz"
                    )  # noqa: E501
                    np.savez_compressed(path, **asdict(new_structure))

    def on_predict_epoch_end(
        self,
        trainer: Trainer,  # noqa: ARG002
        pl_module: LightningModule,  # noqa: ARG002
    ) -> None:
        print(f"Number of failed structure predictions: {self.failed}")  # noqa: T201


class SimpleWriter(BasePredictionWriter):
    """Custom writer for predictions."""

    def __init__(
        self,
        design_dir: str,
        affinity: bool = False,
    ) -> None:
        super().__init__(write_interval="batch")
        self.affinity = affinity
        if design_dir is not None:
            self.init_outdir(design_dir)

    def init_outdir(self, design_dir):
        if self.affinity:
            self.outdir = Path(design_dir) / const.affinity_dirname
        else:
            self.outdir = Path(design_dir) / const.folding_dirname

        self.outdir.mkdir(exist_ok=True, parents=True)
        self.failed = 0

    def write_on_batch_end(  # noqa: PLR0915
        self,
        trainer: Trainer = None,  # noqa: ARG002
        pl_module: LightningModule = None,  # noqa: ARG002
        prediction: Dict[str, Tensor] = None,
        batch_indices: List[int] = None,  # noqa: ARG002
        batch: Dict[str, Tensor] = None,
        batch_idx: int = None,  # noqa: ARG002
        dataloader_idx: int = 0,  # noqa: ARG002
        sample_id: str = None,
    ) -> None:
        """Write the predictions to disk."""
        pred_dict = {}
        for key, value in prediction.items():
            # check object is tensor
            if key in const.eval_keys:
                pred_dict[key] = value.cpu().numpy()
        np.savez_compressed(self.outdir / f"{batch['id'][0]}.npz", **pred_dict)
        if isinstance(prediction["exception"], bool):
            if prediction["exception"]:
                self.failed += 1
        elif isinstance(prediction["exception"], list):
            if prediction["exception"][0]:
                self.failed += 1

    def on_predict_epoch_end(
        self,
        trainer: Trainer,  # noqa: ARG002
        pl_module: LightningModule,  # noqa: ARG002
    ) -> None:
        print(f"Number of failed structure predictions: {self.failed}")  # noqa: T201


class DesignWriter(BasePredictionWriter):
    """Custom writer for predictions."""

    def __init__(
        self,
        output_dir: str,
        res_atoms_only: bool,
        save_traj: bool = False,
        save_x0_traj: bool = False,
        atom14: bool = True,
        atom37: bool = False,
        inverse_fold: bool = False,
        file_suffix: str = "",
    ) -> None:
        """Initialize the writer.

        Parameters
        ----------
        output_dir : str
            The directory to save the predictions.

        """
        super().__init__(write_interval="batch")
        self.mol_dir = Path(output_dir) / const.molecules_dirname
        self.mol_dir.mkdir(parents=True, exist_ok=True)
        self.save_traj = save_traj
        self.save_x0_traj = save_x0_traj
        self.res_atoms_only = res_atoms_only
        self.file_suffix = file_suffix
        self.failed = 0

        # Create the output directories
        self.atom14 = atom14
        self.atom37 = atom37
        self.inverse_fold = inverse_fold
        self.used_stems = set()
        self.init_outdir(output_dir)

    def init_outdir(self, outdir):
        self.outdir = Path(outdir)
        self.outdir.mkdir(parents=True, exist_ok=True)


    def write_on_batch_end(  # noqa: PLR0915
        self,
        trainer: Trainer = None,  # noqa: ARG002
        pl_module: LightningModule = None,  # noqa: ARG002
        prediction: Dict[str, Tensor] = None,
        batch_indices: List[int] = None,  # noqa: ARG002
        batch: Dict[str, Tensor] = None,
        batch_idx: int = None,  # noqa: ARG002
        dataloader_idx: int = 0,  # noqa: ARG002
        sample_id: str = None,
    ) -> None:
        if prediction["exception"]:
            self.failed += 1
            return
        n_samples, _, _ = prediction["coords"].shape

        # TODO: remove this which is only here for temporary backward compatibility
        masker = BoltzMasker(mask=True, mask_backbone=False)
        feat_masked = masker(batch)
        prediction["ref_element"] = feat_masked["ref_element"]
        prediction["ref_atom_name_chars"] = feat_masked["ref_atom_name_chars"]
        """Write the predictions to disk."""
        # Check for extra molecules
        if batch["extra_mols"] is not None:
            extra_mols = batch["extra_mols"][0]
            for k, v in extra_mols.items():
                with open(self.mol_dir / f"{k}.pkl", "wb") as f:
                    pickle.dump(v, f)
        # write samples to disk
        for n in range(n_samples):
            # get structure for all generated coords
            sample, native = {}, {}
            anchor_sample, anchor_native = {}, {}
            atom_is_anchor = torch.matmul(
                batch["atom_to_token"][0].float(),
                batch["is_anchor"][0].float().unsqueeze(-1),
            ).squeeze(-1)

            for k in set(prediction.keys()) & set(batch.keys()):
                if k in const.token_features:
                    if k == "is_anchor":
                        continue
                    anchor_sample[k] = prediction[k][0][
                        prediction["is_anchor"][0].bool()
                    ]
                    anchor_native[k] = batch[k][0][batch["is_anchor"][0].bool()]
                    sample[k] = prediction[k][0][~prediction["is_anchor"][0].bool()]
                    native[k] = batch[k][0][~batch["is_anchor"][0].bool()]
                elif k in const.atom_features:
                    if k == "coords":
                        anchor_native[k] = batch[k][0][0][
                            atom_is_anchor.bool()
                        ].unsqueeze(0)
                        native[k] = batch[k][0][0][~atom_is_anchor.bool()].unsqueeze(0)
                        anchor_sample[k] = prediction[k][n][atom_is_anchor.bool()]
                        sample[k] = prediction[k][n][~atom_is_anchor.bool()]
                    else:
                        anchor_native[k] = batch[k][0][atom_is_anchor.bool()]
                        native[k] = batch[k][0][~atom_is_anchor.bool()]
                        anchor_sample[k] = prediction[k][0][atom_is_anchor.bool()]
                        sample[k] = prediction[k][0][~atom_is_anchor.bool()]
                elif k == "exception":
                    sample[k] = prediction[k]
                    native[k] = batch[k]

                else:
                    sample[k] = prediction[k][0]
                    native[k] = batch[k][0]
                    anchor_sample[k] = prediction[k][0]
                    anchor_native[k] = batch[k][0]

            anchor_sample["is_anchor"] = prediction["is_anchor"][0][
                prediction["is_anchor"][0].bool()
            ]
            anchor_native["is_anchor"] = batch["is_anchor"][0][
                batch["is_anchor"][0].bool()
            ]
            sample["is_anchor"] = prediction["is_anchor"][0][
                ~prediction["is_anchor"][0].bool()
            ]
            native["is_anchor"] = batch["is_anchor"][0][~batch["is_anchor"][0].bool()]
            if self.atom14:
                sample = res_from_atom14(sample)
            elif self.atom37:
                sample = res_from_atom37(sample)
            # Update ligand atom types from predicted atom_type logits if available
            if "atom_type" in prediction and prediction["atom_type"] is not None:
                atom_type_logits = (
                    prediction["atom_type"][n]
                    if prediction["atom_type"].dim() > 2
                    else prediction["atom_type"]
                )
                sample = update_ligand_atom_types_from_atom_type(
                    sample, atom_type_logits
                )

            design_mask = batch["design_mask"][0].bool()
            assert design_mask.sum() == sample["design_mask"].sum()

            if self.inverse_fold:
                token_ids = torch.argmax(sample["res_type"], dim=-1)
                tokens = [const.tokens[i] for i in token_ids]
                ccds = [convert_ccd(token) for token in tokens]

                ccds = torch.tensor(ccds).to(sample["res_type"])
                sample["ccd"][design_mask] = ccds[design_mask]

            try:
                try:
                    ligand_tokens = torch.nonzero(
                        (sample["mol_type"] == const.chain_type_ids["NONPOLYMER"])
                        & sample["design_mask"].bool()
                    ).squeeze(-1)

                    if ligand_tokens.numel() > 0:
                        infer_ligand_token_bonds(sample, update=True)

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

                        self.mol_dir.mkdir(parents=True, exist_ok=True)

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
                                print(
                                    f"Skipping chain {ccd} because it has less than 3 atoms"
                                )
                                continue

                            # build mol
                            coords_chain = sample["coords"][atom_mask]
                            elems_chain = torch.argmax(sample["ref_element"], dim=-1)[
                                atom_mask
                            ]

                            bonds_chain = infer_bonds(coords_chain, elems_chain)

                            mol = rdkit_from_prediction(
                                coords_chain, elems_chain, bonds_chain
                            )

                            # Write CCD back into sample so it ends up in the mmCIF
                            sample["ccd"][chain_tokens] = torch.tensor(
                                convert_ccd(ccd), device=sample["ccd"].device
                            )

                            extra_mols[ccd] = mol
                            with open(self.mol_dir / f"{ccd}.pkl", "wb") as fh:
                                pickle.dump(mol, fh)
                except Exception as e:
                    print(f"[DesignWriter] RDKit mol generation failed: {e}")

                structure, _, _ = Structure.from_feat(sample)
                str_native, _, _ = Structure.from_feat(native)

                # write structure to cif
                if sample_id is not None:
                    file_name = f"{sample_id}_{n}{self.file_suffix}"
                else:
                    file_name = f"batch{batch_idx}_sample{n}_rank{trainer.global_rank}_{batch['id'][0]}{self.file_suffix}"
                native_path = f"{self.outdir}/{file_name}_native.cif"
                gen_path = f"{self.outdir}/{file_name}_gen.cif"
                anchor_path = f"{self.outdir}/{file_name}_anchor.cif"

                # design mask bfactor

                design_mask = batch["design_mask"][0].float()
                atom_design_mask = (
                    sample["atom_to_token"].float() @ design_mask.unsqueeze(-1).float()
                )
                design_mask = (
                    native["design_mask"].float()
                )  # changing to native to matach dimensions when anchor atoms are on
                atom_design_mask = atom_design_mask.squeeze().bool()
                bfactor = atom_design_mask * 100

                # binding type bfactor
                binding_type = batch["binding_type"][0].float()
                atom_binding_type = (
                    sample["atom_to_token"].float() @ binding_type.unsqueeze(-1).float()
                )
                atom_binding_type = atom_binding_type.squeeze().bool()
                binding_type = (
                    native["binding_type"].float()
                )  # changing to native to matach dimensions when anchor atoms are on
                bfactor[atom_binding_type == const.binding_type_ids["BINDING"]] = 60
                bfactor = atom_design_mask[sample["atom_pad_mask"].bool()].float()
                str_native.atoms["bfactor"] = bfactor.cpu().numpy()
                structure.atoms["bfactor"] = bfactor.cpu().numpy()
                bfactor = atom_design_mask[sample["atom_pad_mask"].bool()].float()

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

                open(native_path, "w").write(to_mmcif(str_native))
                open(gen_path, "w").write(to_mmcif(structure))

                if anchor_sample["is_anchor"].sum() > 0:
                    pred_anchors = {
                        k: v[0]
                        for k, v in prediction.items()
                        if k != "exception" and k != "coords"
                    }
                    pred_anchors["exception"] = prediction["exception"]
                    pred_anchors["coords"] = prediction["coords"][n]
                    pred_anchors_str, _, _ = Structure.from_feat(pred_anchors)

                    anchor_structure = Structure.extract_atoms(
                        pred_anchors_str,
                        atom_is_anchor[prediction["atom_resolved_mask"][0].bool()]
                        .bool()
                        .cpu()
                        .numpy(),
                    )
                    structure_with_anchors = Structure.concatenate(
                        structure, anchor_structure
                    )
                    open(anchor_path, "w").write(to_mmcif(structure_with_anchors))

                    anchor_sample_element = anchor_sample["ref_element"]
                    anchor_sample_charge = anchor_sample["ref_charge"]
                    anchor_sample_coords = anchor_sample["coords"]
                    anchor_native_element = anchor_native["ref_element"]
                    anchor_native_charge = anchor_native["ref_charge"]
                    anchor_native_coords = anchor_native["coords"]

                # Write metadata
                metadata_path = f"{self.outdir}/{file_name}_metadata.npz"
                np.savez_compressed(
                    metadata_path,
                    design_mask=design_mask[sample["token_pad_mask"].bool()]
                    .cpu()
                    .numpy(),
                    inverse_fold_design_mask=sample["inverse_fold_design_mask"][
                        sample["token_pad_mask"].bool()
                    ].cpu().numpy()
                    if "inverse_fold_design_mask" in sample
                    else None,
                    mol_type=sample["mol_type"][sample["token_pad_mask"].bool()]
                    .cpu()
                    .numpy(),
                    ss_type=sample["ss_type"][sample["token_pad_mask"].bool()]
                    .cpu()
                    .numpy(),
                    token_resolved_mask=sample["token_resolved_mask"][
                        sample["token_pad_mask"].bool()
                    ]
                    .cpu()
                    .numpy(),
                    binding_type=binding_type[sample["token_pad_mask"].bool()]
                    .cpu()
                    .numpy(),
                    anchor_element=anchor_sample_element.cpu().numpy()
                    if anchor_sample["is_anchor"].sum() > 0
                    else np.array([]),
                    anchor_charge=anchor_sample_charge.cpu().numpy()
                    if anchor_sample["is_anchor"].sum() > 0
                    else np.array([]),
                    anchor_coords=anchor_sample_coords.cpu().numpy()
                    if anchor_sample["is_anchor"].sum() > 0
                    else np.array([]),
                    anchor_native_element=anchor_native_element.cpu().numpy()
                    if anchor_sample["is_anchor"].sum() > 0
                    else np.array([]),
                    anchor_native_charge=anchor_native_charge.cpu().numpy()
                    if anchor_sample["is_anchor"].sum() > 0
                    else np.array([]),
                    anchor_native_coords=anchor_native_coords.cpu().numpy()
                    if anchor_sample["is_anchor"].sum() > 0
                    else np.array([]),
                )

                # Write trajectories
                if self.save_traj:
                    trajs = torch.stack(prediction["coords_traj"], dim=1)
                    traj = trajs[n]
                    aligned = [traj[0]]
                    for frame in traj[1:]:
                        with torch.autocast("cuda", enabled=False):
                            aligned.append(
                                weighted_rigid_align(
                                    frame.float().unsqueeze(0),
                                    aligned[-1].float().unsqueeze(0),
                                    sample["atom_pad_mask"].float().unsqueeze(0),
                                    sample["atom_pad_mask"].float().unsqueeze(0),
                                )
                                .to(frame)
                                .squeeze()
                            )

                    pdbs = []
                    all_coords = []
                    ensemble = []
                    atom_idx = 0
                    for idx, frame in tqdm(
                        enumerate(aligned), desc="Writing traj.", total=len(aligned)
                    ):
                        sample["coords"] = frame
                        if self.atom14:
                            sample = res_from_atom14(sample)
                        elif self.atom37:
                            sample = res_from_atom37(sample)
                        else:
                            raise ValueError("Either atom14 or atom37 must be true")

                        str_frame, _, _ = Structure.from_feat(sample)
                        pdbs.append(to_pdb(str_frame))
                        all_coords.append(str_frame.coords)
                        ensemble.append(
                            (
                                atom_idx,
                                len(str_frame.coords),
                            )
                        )
                        atom_idx += len(str_frame.coords)

                    open(self.outdir / f"{file_name}_traj.pdb", "w").write(
                        self.combine_pdb_models(pdbs)
                    )

                # Write x0 trajectories
                if self.save_x0_traj:
                    trajs = torch.stack(prediction["x0_coords_traj"], dim=1)
                    traj = trajs[n]
                    aligned = [traj[0]]
                    for frame in traj[1:]:
                        with torch.autocast("cuda", enabled=False):
                            aligned.append(
                                weighted_rigid_align(
                                    frame.float().unsqueeze(0),
                                    aligned[-1].float().unsqueeze(0),
                                    sample["atom_pad_mask"].float().unsqueeze(0),
                                    sample["atom_pad_mask"].float().unsqueeze(0),
                                )
                                .to(frame)
                                .squeeze()
                            )

                    pdbs = []
                    all_coords = []
                    ensemble = []
                    atom_idx = 0
                    for idx, frame in tqdm(
                        enumerate(aligned), desc="Writing x0 traj.", total=len(aligned)
                    ):
                        sample["coords"] = frame
                        if self.atom14:
                            sample = res_from_atom14(sample)
                        elif self.atom37:
                            sample = res_from_atom37(sample)
                        else:
                            raise ValueError("Either atom14 or atom37 must be true")

                        str_frame, _, _ = Structure.from_feat(sample)
                        pdbs.append(to_pdb(str_frame))
                        all_coords.append(str_frame.coords)
                        ensemble.append(
                            (
                                atom_idx,
                                len(str_frame.coords),
                            )
                        )
                        atom_idx += len(str_frame.coords)

                    open(self.outdir / f"{file_name}_x0_traj.pdb", "w").write(
                        self.combine_pdb_models(pdbs)
                    )

            except Exception as e:  # noqa: BLE001
                import traceback

                traceback.print_exc()  # noqa: T201
                print(
                    f"predict/writer.py: Validation structure writing failed on {batch['id'][0]} with error {e}. Skipping."
                )  # noqa: T201

    def combine_pdb_models(self, pdb_strings):
        combined_pdb = ""
        model_number = 1

        for pdb in pdb_strings:
            # Add a model number at the start of each model
            combined_pdb += f"MODEL     {model_number}\n"
            combined_pdb += pdb.split("\nEND")[0]
            combined_pdb += "\nENDMDL\n"  # End of model marker
            model_number += 1

        return combined_pdb

    def on_predict_epoch_end(
        self,
        trainer: Trainer,  # noqa: ARG002
        pl_module: LightningModule,  # noqa: ARG002
    ) -> None:
        """Print the number of failed examples."""
        print(f"Number of failed examples: {self.failed}")  # noqa: T201
