from dataclasses import dataclass, replace
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
import pytorch_lightning as pl
import torch
from rdkit.Chem import Mol
from torch import Tensor
from torch.utils.data import DataLoader

from foldeverything.data import const
from foldeverything.data.crop.cropper import Cropper
from foldeverything.data.data import (
    Input,
    Manifest,
)
from foldeverything.data.feature.featurizer import Featurizer
from foldeverything.data.filter.dynamic.filter import DynamicFilter
from foldeverything.data.mol import load_canonicals
from foldeverything.data.pad import pad_to_max
from foldeverything.data.sample.sampler import Sample
from foldeverything.data.tokenize.tokenizer import Tokenizer
from foldeverything.task.train.data import (
    load_dummy_templates_v2,
    load_molecules,
    load_msas,
    load_record,
    load_structure,
    load_templates_v2,
)


@dataclass
class DataConfig:
    """Data configuration."""

    target_dir: str
    msa_dir: str
    featurizer: Featurizer
    tokenizer: Tokenizer
    max_atoms: int
    max_tokens: int
    max_seqs: int
    samples_per_epoch: int
    batch_size: int
    num_workers: int
    random_seed: int
    pin_memory: bool
    atoms_per_window_queries: int
    min_dist: float
    max_dist: float
    num_bins: int
    num_ensembles_train: int = 1
    num_ensembles_val: int = 1
    return_affinity: bool = False
    disulfide_prob: float = 1.0
    disulfide_on: bool = False
    cropper: Optional[Cropper] = None
    template_dir: Optional[str] = None
    manifest_path: Optional[str] = None
    filters: Optional[list[DynamicFilter]] = None
    has_structure_label: bool = True
    has_affinity_label: bool = False
    val_group: Optional[str] = "RCSB"
    moldir: Optional[str] = None
    override_bfactor: Optional[bool] = False
    override_method: Optional[str] = None

    disto_use_ensemble: Optional[bool] = False
    fix_single_ensemble: Optional[bool] = True
    overfit: Optional[int] = None
    pad_to_max_tokens: bool = False
    pad_to_max_atoms: bool = False
    pad_to_max_seqs: bool = False
    return_train_symmetries: bool = False
    return_val_symmetries: bool = True
    train_binder_pocket_conditioned_prop: float = 0.0
    val_binder_pocket_conditioned_prop: float = 0.0
    train_contact_conditioned_prop: float = 0.0
    val_contact_conditioned_prop: float = 0.0
    binder_pocket_cutoff_min: float = 4.0
    binder_pocket_cutoff_max: float = 20.0
    binder_pocket_cutoff_val: float = 6.0
    binder_pocket_sampling_geometric_p: float = 0.0
    maximum_bond_distance: int = 0
    val_batch_size: int = 1
    return_train_affinity: bool = False
    return_val_affinity: bool = False
    add_affinity_cropping: Optional[bool] = False
    max_tokens_affinity: int = 384
    max_tokens_to_atomize_affinity: int = 32
    max_atoms_to_atomize_affinity: int = 128
    affinity_only_atoms: bool = False
    single_sequence_prop_training: float = 0.0
    msa_sampling_training: bool = False
    use_templates: bool = False
    max_templates: int = 4
    no_template_prob: float = 0.0
    compute_frames: bool = True
    ignore_covalent: Optional[bool] = False


@dataclass
class Dataset:
    """Data holder."""

    samples: pd.DataFrame
    struct_dir: Path
    msa_dir: Path
    record_dir: Path
    template_dir: Path
    cropper: Cropper
    tokenizer: Tokenizer
    featurizer: Featurizer
    val_group: str
    has_structure_label: bool = True
    has_affinity_label: bool = False
    moldir: Optional[str] = None
    override_bfactor: Optional[bool] = False
    override_method: Optional[str] = None


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
            "all_coords",
            "all_resolved_mask",
            "crop_to_all_atom_map",
            "chain_symmetries",
            "amino_acids_symmetries",
            "ligand_symmetries",
            "activity_name",
            "activity_qualifier",
            "sid",
            "cid",
            "aid",
            "normalized_protein_accession",
            "pair_id",
            "record",
            "structure_bonds",
            "extra_mols",
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


class PredictionDataset(torch.utils.data.Dataset):
    """Base iterable dataset."""

    def __init__(
        self,
        dataset: Dataset,
        canonicals: dict[str, Mol],
        moldir: str,
        random_seed: int = 42,
        max_atoms: Optional[int] = None,
        max_tokens: Optional[int] = None,
        max_seqs: Optional[int] = None,
        pad_to_max_atoms: bool = False,
        pad_to_max_tokens: bool = False,
        pad_to_max_seqs: bool = False,
        atoms_per_window_queries: int = 32,
        min_dist: float = 2.0,
        max_dist: float = 22.0,
        num_bins: int = 64,
        num_ensembles: int = 1,
        ensemble_sample_replacement: Optional[bool] = False,
        disto_use_ensemble: Optional[bool] = False,
        fix_single_ensemble: Optional[bool] = True,
        overfit: Optional[int] = None,
        return_symmetries: Optional[bool] = False,
        binder_pocket_conditioned_prop: Optional[float] = 0.0,
        contact_conditioned_prop: Optional[float] = 0.0,
        binder_pocket_cutoff: Optional[float] = 6.0,
        maximum_bond_distance: Optional[int] = 0,
        return_affinity: bool = False,
        add_affinity_cropping: Optional[bool] = False,
        max_tokens_affinity: int = 384,
        max_tokens_to_atomize_affinity: int = 32,
        max_atoms_to_atomize_affinity: int = 128,
        affinity_only_atoms: bool = False,
        use_templates: bool = False,
        max_templates: int = 4,
        no_template_prob: float = 0.0,
        compute_frames: bool = True,
        ignore_covalent: bool = False,
        disulfide_prob: float = 1.0,
        disulfide_on: bool = False,
    ) -> None:
        """Initialize the training dataset.

        Parameters
        ----------
        datasets : List[Dataset]
            The datasets to sample from.
        max_tokens : int
            The maximum number of tokens.
        overfit : bool
            Whether to overfit the dataset

        """
        super().__init__()
        self.dataset = dataset
        self.canonicals = canonicals
        self.moldir = moldir
        self.max_atoms = max_atoms
        self.max_tokens = max_tokens
        self.max_seqs = max_seqs
        self.random_seed = random_seed
        self.pad_to_max_tokens = pad_to_max_tokens
        self.pad_to_max_atoms = pad_to_max_atoms
        self.pad_to_max_seqs = pad_to_max_seqs
        self.overfit = overfit
        self.atoms_per_window_queries = atoms_per_window_queries
        self.min_dist = min_dist
        self.max_dist = max_dist
        self.num_bins = num_bins
        self.num_ensembles = num_ensembles
        self.ensemble_sample_replacement = ensemble_sample_replacement
        self.disto_use_ensemble = disto_use_ensemble
        self.fix_single_ensemble = fix_single_ensemble
        self.return_symmetries = return_symmetries
        self.return_affinity = return_affinity
        self.binder_pocket_conditioned_prop = binder_pocket_conditioned_prop
        self.contact_conditioned_prop = contact_conditioned_prop
        self.binder_pocket_cutoff = binder_pocket_cutoff
        self.maximum_bond_distance = maximum_bond_distance
        self.add_affinity_cropping = add_affinity_cropping
        self.max_tokens_affinity = max_tokens_affinity
        self.max_tokens_to_atomize_affinity = max_tokens_to_atomize_affinity
        self.max_atoms_to_atomize_affinity = max_atoms_to_atomize_affinity
        self.affinity_only_atoms = affinity_only_atoms
        self.use_templates = use_templates
        self.max_templates = max_templates
        self.no_template_prob = no_template_prob
        self.compute_frames = compute_frames
        self.ignore_covalent = ignore_covalent
        self.override_bfactor = dataset.override_bfactor
        self.override_method = dataset.override_method
        self.disulfide_prob = disulfide_prob
        self.disulfide_on = disulfide_on

    def __getitem__(self, idx: int) -> Dict:
        """Get an item from the dataset.

        Returns
        -------
        Dict[str, Tensor]
            The sampled data features.

        """
        # Set random state
        seed = self.random_seed if self.overfit is None else None
        random = np.random.default_rng(seed)

        # Get a sample from the dataset
        sample = Sample(**self.dataset.samples.iloc[idx].to_dict())
        record = load_record(sample.record_id, self.dataset.record_dir)

        # Get the structure
        try:
            structure = load_structure(record, self.dataset.struct_dir)
            structure.atoms["is_present"] = True
            structure.residues["is_present"] = True
        except Exception as e:  # noqa: BLE001
            print(f"Failed to load input for {record.id} with error {e}. Skipping.")
            return self.__getitem__(0)

        # Ignore glycans
        if self.ignore_covalent:
            for i, chain in enumerate(structure.chains):
                if (chain["mol_type"] == const.chain_type_ids["NONPOLYMER"]) and chain[
                    "res_num"
                ] > 1:
                    structure.mask[i] = False

        # Tokenize structure
        try:
            tokenized = self.dataset.tokenizer.tokenize(structure)
        except Exception as e:  # noqa: BLE001
            print(f"Tokenizer failed on {record.id} with error {e}. Skipping.")  # noqa: T201
            return self.__getitem__(0)

        # Get unique chains
        chain_ids = set(np.unique(tokenized.tokens["asym_id"]).tolist())

        # Load msas and templates
        try:
            msas = load_msas(chain_ids, record, self.dataset.msa_dir)
        except Exception as e:  # noqa: BLE001
            print(f"MSA loading failed for {record.id} with error {e}. Skipping.")
            return self.__getitem__(0)

        # Load templates
        if self.dataset.template_dir is not None:
            try:
                templates_features = load_templates_v2(
                    tokenized=tokenized,
                    record=record,
                    template_dir=self.dataset.template_dir,
                    structure_dir=self.dataset.struct_dir,
                    tokenizer=self.dataset.tokenizer,
                    max_templates=self.max_templates,
                    no_template_prob=self.no_template_prob,
                    training=False,
                    random=random,
                    max_tokens=len(tokenized.tokens),
                )
            except Exception as e:  # noqa: BLE001
                print(
                    f"Template loading failed for {record.id} with error {e}. Using no templates."
                )
                templates = None
                templates_features = load_dummy_templates_v2(
                    tdim=self.max_templates, num_tokens=len(tokenized.tokens)
                )
        else:
            templates = None
            templates_features = load_dummy_templates_v2(
                tdim=self.max_templates, num_tokens=len(tokenized.tokens)
            )

        try:
            # Try to find molecules in the dataset moldir if provided
            # Find missing ones in global moldir and check if all found
            molecules = {}
            molecules.update(self.canonicals)
            mol_names = set(tokenized.tokens["res_name"].tolist())
            mol_names = mol_names - set(self.canonicals.keys())
            if self.dataset.moldir is not None:
                molecules.update(load_molecules(self.dataset.moldir, mol_names))

            mol_names = mol_names - set(molecules.keys())
            molecules.update(load_molecules(self.moldir, mol_names))
        except Exception as e:  # noqa: BLE001
            print(f"Molecule loading failed for {record.id} with error {e}. Skipping.")
            return self.__getitem__(0)

        # Finalize input data
        input_data = Input(
            tokens=tokenized.tokens,
            bonds=tokenized.bonds,
            token_to_res=tokenized.token_to_res,
            structure=structure,
            msa=msas,
            templates=templates,
            record=record,
        )

        # Compute features
        try:
            features = self.dataset.featurizer.process(
                input_data,
                molecules=molecules,
                random=random,
                training=False,
                max_atoms=None,
                max_tokens=None,
                max_seqs=self.max_seqs,
                pad_to_max_seqs=self.pad_to_max_seqs,
                atoms_per_window_queries=self.atoms_per_window_queries,
                min_dist=self.min_dist,
                max_dist=self.max_dist,
                num_bins=self.num_bins,
                num_ensembles=self.num_ensembles,
                ensemble_sample_replacement=self.ensemble_sample_replacement,
                disto_use_ensemble=self.disto_use_ensemble,
                fix_single_ensemble=self.fix_single_ensemble,
                compute_symmetries=self.return_symmetries,
                binder_pocket_conditioned_prop=self.binder_pocket_conditioned_prop,
                contact_conditioned_prop=self.contact_conditioned_prop,
                binder_pocket_cutoff_min=self.binder_pocket_cutoff,
                binder_pocket_cutoff_max=self.binder_pocket_cutoff,
                binder_pocket_sampling_geometric_p=1.0,  # this will only sample a single pocket token
                only_ligand_binder_pocket=True,
                only_pp_contact=True,
                maximum_bond_distance=self.maximum_bond_distance,
                compute_affinity=self.return_affinity,
                affinity_info=record.affinity,
                has_structure_label=self.dataset.has_structure_label,
                has_affinity_label=self.dataset.has_affinity_label,
                add_affinity_cropping=self.add_affinity_cropping,
                max_tokens_affinity=self.max_tokens_affinity,
                max_tokens_to_atomize_affinity=self.max_tokens_to_atomize_affinity,
                max_atoms_to_atomize_affinity=self.max_atoms_to_atomize_affinity,
                affinity_only_atoms=self.affinity_only_atoms,
                single_sequence_prop=0.0,
                use_templates=self.use_templates,
                max_templates=self.max_templates,
                override_bfactor=self.override_bfactor,
                override_method=self.override_method,
                compute_frames=self.compute_frames,
                disulfide_prob=self.disulfide_prob,
                disulfide_on=self.disulfide_on,
            )
        except Exception as e:  # noqa: BLE001
            print(f"Featurizer failed on {record.id} with error {e}. Skipping.")  # noqa: T201
            return self.__getitem__(0)

        # Add record
        features.update(templates_features)
        features["record"] = record

        return features

    def __len__(self) -> int:
        """Get the length of the dataset.

        Returns
        -------
        int
            The length of the dataset.

        """
        return len(self.dataset.samples)


class FoldEverythingDataModule(pl.LightningDataModule):
    """DataModule for FoldEverything."""

    def __init__(self, cfg: DataConfig) -> None:
        """Initialize the DataModule.

        Parameters
        ----------
        config : DataConfig
            The data configuration.

        """
        super().__init__()
        self.cfg = cfg

        # Create validation dataset
        if cfg.manifest_path is not None:
            path = Path(cfg.manifest_path)
        else:
            path = Path(cfg.target_dir) / "manifest.json"
        manifest: Manifest = Manifest.load(path)

        # Filter records
        if cfg.filters is not None:
            filtered_records = [
                record
                for record in manifest.records
                if all(f.filter(record) for f in cfg.filters)
            ]
            manifest = replace(manifest, records=filtered_records)

        samples: list[Sample] = [Sample(r.id) for r in manifest.records]
        samples = pd.DataFrame([s.record_id for s in samples], columns=["record_id"])
        samples = samples.replace({np.nan: None})
        samples["record_id"] = samples["record_id"].astype("string")

        # Get relevant directories
        struct_dir = Path(cfg.target_dir) / "structures"
        record_dir = Path(cfg.target_dir) / "records"
        msa_dir = Path(cfg.msa_dir)

        # Get template_dir, if any
        template_dir = cfg.template_dir
        template_dir = Path(template_dir) if template_dir is not None else None

        # Get moldir, if any
        moldir = cfg.moldir
        moldir = Path(moldir) if moldir is not None else None

        dataset = Dataset(
            samples=samples,
            struct_dir=struct_dir,
            msa_dir=msa_dir,
            record_dir=record_dir,
            template_dir=template_dir,
            moldir=moldir,
            cropper=cfg.cropper,
            tokenizer=cfg.tokenizer,
            featurizer=cfg.featurizer,
            val_group=cfg.val_group,
            has_structure_label=cfg.has_structure_label,
            has_affinity_label=cfg.has_affinity_label,
        )

        # Load canonical molecules
        canonicals = load_canonicals(cfg.moldir)

        self._predict_set = PredictionDataset(
            dataset=dataset,
            canonicals=canonicals,
            moldir=moldir,
            random_seed=cfg.random_seed,
            max_atoms=cfg.max_atoms,
            max_tokens=cfg.max_tokens,
            max_seqs=cfg.max_seqs,
            maximum_bond_distance=cfg.maximum_bond_distance,
            ignore_covalent=cfg.ignore_covalent,
            return_affinity=cfg.return_affinity,
            use_templates=cfg.use_templates,
            no_template_prob=cfg.no_template_prob,
            max_templates=cfg.max_templates,
            disulfide_prob=cfg.disulfide_prob,
            disulfide_on=cfg.disulfide_on,
        )

    def predict_dataloader(self) -> DataLoader:
        """Get the training dataloader.

        Returns
        -------
        DataLoader
            The training dataloader.

        """
        return DataLoader(
            self._predict_set,
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
        dataloader_idx: int,  # noqa: ARG002
    ) -> Dict:
        """Transfer a batch to the given device.

        Parameters
        ----------
        batch : Dict
            The batch to transfer.
        device : torch.device
            The device to transfer to.
        dataloader_idx : int
            The dataloader index.

        Returns
        -------
        np.Any
            The transferred batch.

        """
        for key in batch:
            if key not in [
                "all_coords",
                "all_resolved_mask",
                "crop_to_all_atom_map",
                "chain_symmetries",
                "amino_acids_symmetries",
                "ligand_symmetries",
                "activity_name",
                "activity_qualifier",
                "sid",
                "cid",
                "normalized_protein_accession",
                "pair_id",
                "record",
                "structure_bonds",
                "extra_mols",
            ]:
                batch[key] = batch[key].to(device)
        return batch
