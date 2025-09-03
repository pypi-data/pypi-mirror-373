from dataclasses import dataclass
from pathlib import Path
import random
import re
from typing import Dict, List, Optional
from collections import defaultdict
from rdkit.Chem import Mol
import pickle

import numpy as np
import pytorch_lightning as pl
import torch
from torch import Tensor
from torch.utils.data import DataLoader

from foldeverything.data import const
from foldeverything.data.data import Input, Structure, Tokenized
from foldeverything.data.feature.featurizer import Featurizer
from foldeverything.data.mol import load_canonicals, load_molecules
from foldeverything.data.pad import pad_to_max
from foldeverything.data.parse import mmcif
from foldeverything.data.parse.pdb_parser import parse_pdb
from foldeverything.data.template.features import (
    load_dummy_templates_v2,
)
from foldeverything.data.parse.schema import parse_redesign_yaml
from foldeverything.data.tokenize.tokenizer import Tokenizer


class EvalDatafetchException(Exception):
    pass


@dataclass
class DataConfig:
    """Data configuration."""

    num_targets: int
    samples_per_target: int
    moldir: str
    suffix: str
    suffix_native: str
    suffix_metadata: str
    tokenizer: Tokenizer
    featurizer: Featurizer
    batch_size: int
    num_workers: int
    pin_memory: bool
    target_id_regex: str = r"rank\d+_(.*?)_"
    design: bool = False
    # Featurizer args (if design is True these should match with training config):
    backbone_only: bool = False
    atom14: bool = True
    atom14_geometric: bool = True
    max_seqs: int = 1
    inverse_fold: bool = False
    extra_mol_dir: Optional[str] = None
    anchors_on: bool = False
    disulfide_prob: float = 1.0
    disulfide_on: bool = False
    design_mask_override: Optional[str] = None


def collate(data: List[Dict[str, Tensor]]) -> Dict[str, Tensor]:
    """Collate the data.

    Parameters
    ----------
    data : List[Dict[str, Tensor]]
        The data to collate.

    Returns
    -------
    Dict[str, Tensor]
        The collated data.

    """
    # Get the keys
    keys = data[0].keys()

    # Collate the data
    collated = {}
    for key in keys:
        values = [d[key] for d in data]

        if key not in [
            "metadata",
            "str_gen",
            "id",
            "path",
            "native_metadata",
            "native_str_gen",
            "native_id",
            "native_path",
            "exception",
            "native_exception",
            "skip",
            "native_skip",
            "structure_bonds",
            "native_structure_bonds",
            "extra_mols",
            "native_extra_mols",
            "structure",
            "tokenized",
        ]:
            # Check if all have the same shape
            shape = values[0].shape
            if not all(v.shape == shape for v in values):
                values = pad_to_max(values, 0)
            else:
                values = torch.stack(values, dim=0)

        # Stack the values
        collated[key] = values

    return collated


@dataclass(frozen=True)
class TemplateInfo:
    """TemplateInfo datatype."""

    name: str
    query_chain: str
    query_st: int
    query_en: int
    template_chain: str
    template_st: int
    template_en: int


def template_from_tokens(
    tokenized: Tokenized,
    token_mask: np.ndarray[bool],
    tdim: int = 1,
) -> dict[str, torch.Tensor]:
    """Get template features where the tokens specified in token_mask have their structure specified."""
    # Get num token
    num_tokens = len(tokenized.tokens)

    # Allocate features
    res_type = np.zeros((tdim, num_tokens), dtype=np.int64)
    frame_rot = np.zeros((tdim, num_tokens, 3, 3), dtype=np.float32)
    frame_t = np.zeros((tdim, num_tokens, 3), dtype=np.float32)
    cb_coords = np.zeros((tdim, num_tokens, 3), dtype=np.float32)
    ca_coords = np.zeros((tdim, num_tokens, 3), dtype=np.float32)
    frame_mask = np.zeros((tdim, num_tokens), dtype=np.float32)
    cb_mask = np.zeros((tdim, num_tokens), dtype=np.float32)
    template_mask = np.zeros((tdim, num_tokens), dtype=np.float32)
    query_to_template = np.zeros((tdim, num_tokens), dtype=np.int64)
    visibility_ids = np.zeros((tdim, num_tokens), dtype=np.float32)

    # Now create features per token
    template_indices = np.where(token_mask)[0]
    for token_idx in template_indices:
        token = tokenized.tokens[token_idx]
        res_type[:, token_idx] = token["res_type"]
        frame_rot[:, token_idx] = token["frame_rot"].reshape(3, 3)
        frame_t[:, token_idx] = token["frame_t"]
        cb_coords[:, token_idx] = token["disto_coords"]
        ca_coords[:, token_idx] = token["center_coords"]
        cb_mask[:, token_idx] = token["disto_mask"]
        frame_mask[:, token_idx] = token["frame_mask"]
        template_mask[:, token_idx] = 1.0
        visibility_ids[:, token_idx] = 1

    # Convert to one-hot
    res_type = torch.from_numpy(res_type)
    res_type = torch.nn.functional.one_hot(res_type, num_classes=const.num_tokens)

    return {
        "template_restype": res_type,
        "template_frame_rot": torch.from_numpy(frame_rot),
        "template_frame_t": torch.from_numpy(frame_t),
        "template_cb": torch.from_numpy(cb_coords),
        "template_ca": torch.from_numpy(ca_coords),
        "template_mask_cb": torch.from_numpy(cb_mask),
        "template_mask_frame": torch.from_numpy(frame_mask),
        "template_mask": torch.from_numpy(template_mask),
        "query_to_template": torch.from_numpy(query_to_template),
        "visibility_ids": torch.from_numpy(visibility_ids),
    }


class EvalDataset(torch.utils.data.Dataset):
    def __init__(
        self,
        generated_paths: List[Path],
        metadata_paths: List[Path],
        native_paths: List[Path],
        moldir: Path,
        canonicals: dict[str, Mol],
        tokenizer: Tokenizer,
        featurizer: Featurizer,
        return_native: bool = False,
        reference_metadata_dir: Optional[Path] = None,
        target_templates: bool = False,
        skip_existing: bool = False,
        compute_affinity: bool = False,
        design: bool = False,
        backbone_only: bool = False,
        atom14: bool = True,
        atom14_geometric: bool = True,
        max_seqs: int = 1,
        inverse_fold: bool = False,
        extra_mol_dir: Optional[Path] = None,
        extra_features: Optional[List[str]] = None,
        anchors_on: bool = False,
        disulfide_prob: float = 1.0,
        disulfide_on: bool = False,
        design_mask_override: Optional[str] = None,
        use_new_design_mask: bool = False,
    ) -> None:
        """
        Parameters
        ----------
        design : bool
            Set to True if this dataset is used to make predictions over (i.e. design some parts
            of the structure). Set to False if this dataset is used to only evaluate the predictions
            under the paths (i.e. no design is done).
        """
        super().__init__()
        self.tokenizer = tokenizer
        self.moldir = moldir
        self.canonicals = canonicals
        self.featurizer = featurizer
        self.metadata_paths = metadata_paths
        self.generated_paths = generated_paths
        self.native_paths = native_paths
        self.return_native = return_native
        self.reference_metadata_dir = reference_metadata_dir
        self.target_templates = target_templates
        self.skip_existing = skip_existing
        self.compute_affinity = compute_affinity
        self.design = design
        self.backbone_only = backbone_only
        self.atom14 = atom14
        self.atom14_geometric = atom14_geometric
        self.max_seqs = max_seqs
        self.inverse_fold = inverse_fold
        self.extra_mol_dir = extra_mol_dir
        self.extra_features = (
            set(extra_features) if extra_features is not None else set()
        )
        self.anchors_on = anchors_on
        self.disulfide_prob = disulfide_prob
        self.disulfide_on = disulfide_on
        self.design_mask_override = design_mask_override
        self.use_new_design_mask = use_new_design_mask

    def __getitem__(self, idx: int) -> Dict:
        """Get an item from the dataset.

        Returns
        -------
        Dict[str, Tensor]

        """
        # if sample id is given the nconstruct the paths from that. otherwise use hte function below

        try:
            return self.getitem_from_paths(
                self.metadata_paths[idx],
                self.generated_paths[idx],
                self.native_paths[idx],
            )
        except EvalDatafetchException:
            idx = random.randint(0, len(self) - 1)
            return self.getitem_from_paths(
                self.metadata_paths[idx],
                self.generated_paths[idx],
                self.native_paths[idx],
            )

    def get_sample(self, design_dir: Path, sample_id: Optional[str] = None) -> Dict:
        metadata_path = design_dir/f"{sample_id}_metadata.npz"
        generated_path = design_dir/f"{sample_id}_gen.cif"
        
        return self.getitem_from_paths(metadata_path, generated_path, None)


    def getitem_from_paths(
        self,
        metadata_path,
        generated_path,
        native_path,
    ) -> Dict:
        """Get an item from the dataset.

        Returns
        -------
        Dict[str, Tensor]

        """
        # Get metadata
        if self.reference_metadata_dir:
            reference_metadata_path = self.reference_metadata_dir / metadata_path.name
            metadata = np.load(reference_metadata_path)
        else:
            metadata = np.load(metadata_path)

        # get conditioning information from metadata
        metadata_design_mask = metadata["design_mask"]
        new_design_mask = (
            metadata["inverse_fold_design_mask"].astype(np.float32)
            if self.use_new_design_mask
            else None
        )

        ss_type = None
        if "ss_type" in metadata:
            ss_type = metadata["ss_type"]

        design_mask = (
            metadata_design_mask if not self.use_new_design_mask else new_design_mask
        )

        binding_type = None
        if "binding_type" in metadata:
            binding_type = metadata["binding_type"]

        # Get features
        feat = self.get_feat(generated_path, design_mask, ss_type, binding_type)

        if self.anchors_on:
            anchor_element = metadata["anchor_element"]
            anchor_charge = metadata["anchor_charge"]
            anchor_coords = metadata["anchor_coords"]
            anchor_element = torch.from_numpy(anchor_element)
            anchor_charge = torch.from_numpy(anchor_charge)
            anchor_coords = torch.from_numpy(anchor_coords)
            feat.update(
                {
                    "anchor_charge": anchor_charge,
                    "anchor_coords": anchor_coords,
                    "anchor_element": anchor_element,
                }
            )
        # Get native features
        if self.return_native:
            if "native_design_mask" in metadata.keys():
                feat_native = self.get_feat(native_path, metadata["native_design_mask"])
            else:
                feat_native = self.get_feat(native_path, metadata_design_mask)

            for k, v in feat_native.items():
                feat[f"native_{k}"] = v

        return feat

    def get_feat(self, path, design_mask=None, ss_type=None, binding_type=None):
        # Load design
        if (
            self.extra_mol_dir is not None
        ):  # Fix so that we don't rewrite the mols every time when get_feat is called
            mols = {
                path.stem: pickle.load(path.open("rb"))
                for path in self.extra_mol_dir.glob("*.pkl")
            }
            for mol_name, mol in mols.items():
                element_counts = defaultdict(int)
                for i, atom in enumerate(mol.GetAtoms()):
                    symbol = atom.GetSymbol()
                    element_counts[symbol] += 1
                    atom_name = f"{symbol}{element_counts[symbol]}"
                    atom.SetProp("name", atom_name)
        try:
            if path.suffix == ".cif":
                structure = mmcif.parse_mmcif(
                    path, mols, moldir=self.moldir, use_original_res_idx=False
                ).data
            elif path.suffix == ".pdb":
                structure = parse_pdb(
                    path, moldir=self.moldir, use_original_res_idx=False
                ).data
            else:
                raise ValueError(f"Invalid path:{path}")  # noqa: T201
        except Exception as e:  # noqa: BLE001
            print(f"Failed to parse mmcif for {path} with error {e}. Skipping.")  # noqa: T201
            raise EvalDatafetchException() from e

        # Tokenize structure
        try:
            tokenized = self.tokenizer.tokenize(structure)
        except Exception as e:  # noqa: BLE001
            print(f"Tokenizer failed on {path} with error {e}. Skipping.")  # noqa: T201
            raise EvalDatafetchException() from e

        # For inverse folding, condition even on structure selected for design
        if self.inverse_fold:
            tokenized.tokens["structure_group"] = 1

        try:
            # Try to find molecules in the dataset moldir if provided
            # Find missing ones in global moldir and check if all found
            molecules = {}
            molecules.update(self.canonicals)
            mol_names = set(tokenized.tokens["res_name"].tolist())
            mol_names = mol_names - set(self.canonicals.keys())
            if mols is not None:
                molecules.update(mols)
            mol_names = mol_names - set(molecules.keys())
            if self.moldir is not None:
                molecules.update(load_molecules(self.moldir, mol_names))
            molecules.update(load_molecules(self.moldir, mol_names))
        except Exception as e:  # noqa: BLE001
            print(f"Molecule loading failed for {path} with error {e}. Skipping.")
            raise EvalDatafetchException() from e

        # Set design mask to be used during featurization to mask designed parts if the dataset is
        # used to make predictions
        if self.design and design_mask is not None:
            tokenized.tokens["design_mask"] = torch.from_numpy(design_mask).bool()

        # Finalize input data
        input_data = Input(
            tokens=tokenized.tokens,
            bonds=tokenized.bonds,
            token_to_res=tokenized.token_to_res,
            structure=structure,
            msa={},
            templates=None,
        )

        # Compute features
        try:
            features = self.featurizer.process(
                input_data,
                molecules=molecules,
                random=np.random.default_rng(None),
                training=False,
                max_seqs=self.max_seqs,
                use_templates=False,
                backbone_only=self.backbone_only,
                atom14=self.atom14,
                atom14_geometric=self.atom14_geometric,
                design=True,
                compute_affinity=self.compute_affinity,
                override_method="X-RAY DIFFRACTION",
                disulfide_prob=self.disulfide_prob,
                disulfide_on=self.disulfide_on,
            )
        except Exception as e:  # noqa: BLE001
            print(f"Featurizer failed on {path} with error {e}. Skipping.")  # noqa: T201
            raise EvalDatafetchException() from e

        # Set conditioning variables that were set during design
        if ss_type is not None:
            features["ss_type"] = torch.from_numpy(ss_type).long()
        if binding_type is not None:
            features["binding_type"] = torch.from_numpy(binding_type).long()

        # Set design mask on top of featurized structure not to mask anything if the dataset is used
        # to only evaluate the predictions
        if not self.design and design_mask is not None:
            features["design_mask"] = torch.from_numpy(design_mask).bool()

        features["str_gen"] = structure
        features["path"] = path
        features["id"] = path.stem
        if (
            self.design
            and design_mask is not None
            and self.design_mask_override is not None
        ):
            print(
                f"design mask being overridden with user input: {self.design_mask_override}"
            )
            new_design_mask = parse_redesign_yaml(
                Path(self.design_mask_override), tokenized
            )
            features["inverse_fold_design_mask"] = torch.from_numpy(
                new_design_mask
            ).bool()

        if len(tokenized.tokens) != len(design_mask):
            print(
                f"WARNING: len(tokenized.tokens) [{len(tokenized.tokens)}] != len(design_mask) "
                f"[{len(design_mask)}] for {path}"
            )
            features["exception"] = True
            return features
        else:
            features["exception"] = False

        # Set templates
        if self.target_templates:
            templates_features = template_from_tokens(
                tokenized, ~design_mask.astype(bool)
            )
        else:
            # Compute template features
            templates_features = load_dummy_templates_v2(
                tdim=1, num_tokens=len(features["res_type"])
            )
        features.update(templates_features)

        features["affinity_token_mask"] = (
            features["mol_type"] == const.chain_type_ids["NONPOLYMER"]
        )

        if "structure" in self.extra_features:
            features["structure"] = structure
        if "tokenized" in self.extra_features:
            features["tokenized"] = tokenized

        return features

    def __len__(self) -> int:
        return len(self.generated_paths)


class EvalDataModule(pl.LightningDataModule):
    def __init__(
        self,
        cfg: DataConfig,
        return_native: bool = False,
        compute_affinity: bool = False,
        target_templates: bool = False,
        skip_existing_folded: bool = False,
        reference_metadata_dir: Optional[Path] = None,
        design_dir: Optional[str] = None,
        extra_features: Optional[List[str]] = None,
        design_mask_override: Optional[str] = None,
        skip_specific_ids: Optional[List[str]] = None,
        use_new_design_mask: bool = False,
    ) -> None:
        super().__init__()
        self.cfg = cfg
        self.return_native = return_native
        self.skip_existing_folded = skip_existing_folded
        self.reference_metadata_dir = (
            Path(reference_metadata_dir) if reference_metadata_dir else None
        )
        self.compute_affinity = compute_affinity
        self.target_templates = target_templates
        self.extra_features = extra_features
        self.disulfide_prob = cfg.disulfide_prob
        self.disulfide_on = cfg.disulfide_on
        self.design_mask_override = cfg.design_mask_override
        self.collate = collate

        if design_dir is not None:
            self.init_dataset(
                design_dir,
                skip_specific_ids=skip_specific_ids,
                extra_features=extra_features,
                use_new_design_mask=use_new_design_mask,
            )

        else:

            # Load canonical molecules
            canonicals = load_canonicals(self.cfg.moldir)

            self._predict_set = EvalDataset(
                generated_paths=[],
                metadata_paths=[],
                native_paths=[],
                canonicals=canonicals,
                moldir=Path(self.cfg.moldir),
                tokenizer=self.cfg.tokenizer,
                featurizer=self.cfg.featurizer,
                return_native=self.return_native,
                reference_metadata_dir=self.reference_metadata_dir,
                target_templates=self.target_templates,
                compute_affinity=self.compute_affinity,
                design=self.cfg.design,
                backbone_only=self.cfg.backbone_only,
                atom14=self.cfg.atom14,
                atom14_geometric=self.cfg.atom14_geometric,
                max_seqs=self.cfg.max_seqs,
                inverse_fold=self.cfg.inverse_fold,
                anchors_on=self.cfg.anchors_on,
                extra_features=self.extra_features,
                disulfide_prob=self.disulfide_prob,
                disulfide_on=self.disulfide_on,
                design_mask_override=self.design_mask_override,
                use_new_design_mask=use_new_design_mask,
            )


    def init_dataset(
        self,
        design_dir,
        skip_specific_ids: Optional[List[str]] = None,
        extra_features: Optional[List[str]] = None,
        use_new_design_mask: bool = False,
    ):
        print(f"Initializing EvalDataModule datasets for {design_dir}")
        design_dir = Path(design_dir)
        assert design_dir.exists(), f"Path does not exist design_dir: {design_dir}"

        # Aggregate paths
        generated_paths = sorted(design_dir.glob(f"*{self.cfg.suffix}"))

        # skip certain ids
        num_files_before = len(generated_paths)
        print(f"[Info] Number of files before filtering: {num_files_before}")
        if skip_specific_ids:
            filtered_generated_paths = [
                p
                for p in generated_paths
                if not any(prob_id in p.name for prob_id in skip_specific_ids)
            ]
            num_files_after = len(filtered_generated_paths)
            print(f"[Info] Skipped specific IDs: {skip_specific_ids}")
            print(f"[Info] Number of files after filtering: {num_files_after}")
            generated_paths = filtered_generated_paths

        if self.skip_existing_folded:
            generated_paths = [
                p
                for p in generated_paths
                if not (design_dir / const.folding_dirname / f"{p.stem}.npz").exists()
            ]
            msg = f"[Info] Skipped already folded IDs. Number of files after filtering: {len(generated_paths)}"
            print(msg)

        target_ids = [
            re.search(rf"{self.cfg.target_id_regex}", p.stem).group(1)
            for p in generated_paths
        ]
        target_ids = list(set(target_ids))
        if self.cfg.num_targets is not None:
            target_ids = target_ids[: self.cfg.num_targets]
            generated_paths = [
                p
                for p in generated_paths
                if re.search(rf"{self.cfg.target_id_regex}", p.stem).group(1)
                in target_ids
            ]

        filtered_paths = []
        for target_id in target_ids:
            paths_of_target = [
                p
                for p in generated_paths
                if re.search(rf"{self.cfg.target_id_regex}", p.stem).group(1)
                == target_id
            ]
            filtered_paths.extend(paths_of_target[: self.cfg.samples_per_target])

        metadata_paths = []
        native_paths = []
        for path in filtered_paths:
            metadata_path = Path(
                str(path).replace(self.cfg.suffix, self.cfg.suffix_metadata)
            )
            native_path = Path(
                str(path).replace(self.cfg.suffix, self.cfg.suffix_native)
            )
            if not metadata_path.exists():
                print(f"[WARNING] Path does not exist: {metadata_path}")
            metadata_paths.append(metadata_path)
            if self.return_native:
                if not native_path.exists():
                    print(f"[WARNING] Path does not exist: {native_path}")
                native_paths.append(native_path)
            else:
                native_paths.append(None)
        print(
            f"Found {len(target_ids)} targets and {len(filtered_paths)} designs to evaluate."
        )

        # Load canonical molecules
        canonicals = load_canonicals(self.cfg.moldir)

        self.predict_set = EvalDataset(
            generated_paths=filtered_paths,
            metadata_paths=metadata_paths,
            native_paths=native_paths,
            canonicals=canonicals,
            moldir=Path(self.cfg.moldir),
            tokenizer=self.cfg.tokenizer,
            featurizer=self.cfg.featurizer,
            return_native=self.return_native,
            reference_metadata_dir=self.reference_metadata_dir,
            target_templates=self.target_templates,
            compute_affinity=self.compute_affinity,
            design=self.cfg.design,
            backbone_only=self.cfg.backbone_only,
            atom14=self.cfg.atom14,
            atom14_geometric=self.cfg.atom14_geometric,
            max_seqs=self.cfg.max_seqs,
            inverse_fold=self.cfg.inverse_fold,
            extra_mol_dir=design_dir / const.molecules_dirname,
            anchors_on=self.cfg.anchors_on,
            extra_features=self.extra_features,
            disulfide_prob=self.disulfide_prob,
            disulfide_on=self.disulfide_on,
            design_mask_override=self.design_mask_override,
            use_new_design_mask=use_new_design_mask,
        )

    def predict_dataloader(self) -> DataLoader:
        return DataLoader(
            self.predict_set,
            batch_size=self.cfg.batch_size,
            num_workers=self.cfg.num_workers,
            pin_memory=self.cfg.pin_memory,
            shuffle=False,
            collate_fn=collate,
        )

    def transfer_batch_to_device(
        self,
        batch: Dict,
        device: torch.device,
        dataloader_idx: int = 0,
    ) -> Dict:
        for key in batch:
            if key not in [
                "metadata",
                "str_gen",
                "id",
                "path",
                "native_metadata",
                "native_str_gen",
                "native_id",
                "native_path",
                "exception",
                "native_exception",
                "skip",
                "native_skip",
                "structure_bonds",
                "native_structure_bonds",
                "extra_mols",
                "native_extra_mols",
                "structure",
                "tokenized",
            ]:
                batch[key] = batch[key].to(device)

        return batch
