from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import numpy as np
import pytorch_lightning as pl
import torch
from torch import Tensor
from torch.utils.data import DataLoader
from rdkit.Chem import Mol
from foldeverything.data.data import Input, Record, MSA
from foldeverything.data.feature.featurizer import Featurizer
from foldeverything.data.pad import pad_to_max
from foldeverything.data.template.features import (
    load_dummy_templates_v2,
)
from foldeverything.data.mol import load_canonicals, load_molecules
from foldeverything.data.tokenize.tokenizer import Tokenizer
from foldeverything.data.loading_utils import load_record, load_structure


@dataclass
class DataConfig:
    """Data configuration."""

    target_dir: str
    msa_dir: str
    moldir: str
    target_ids: str
    tokenizer: Tokenizer
    featurizer: Featurizer
    msa_condition: bool = False
    max_seq: int = 1024


@dataclass
class Dataset:
    """Data holder."""

    struct_dir: Path
    record_dir: Path
    target_ids: List[str]
    tokenizer: Tokenizer
    featurizer: Featurizer


def load_msas(record: Record, chain_ids: set[int], msa_dir: Path) -> Dict[int, MSA]:
    """Load the given input data.

    Parameters
    ----------
    record : Record
        The record to load.
    chain_ids : set[int]
        The chain ids to load.
    msa_dir : Path
        The path to the MSA directory.

    Returns
    -------
    Input
        The loaded input.

    """
    # Load the relevant MSAs
    msas = {}
    for chain in record.chains:
        if chain.chain_id in chain_ids:
            msa_id = chain.msa_id
            if msa_id != -1:
                msa = np.load(msa_dir / f"{msa_id}.npz")
                msas[chain.chain_id] = MSA(**msa)
    return msas


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
            "id",
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
        msa_condition: bool = False,
        max_seq: int = 1024,
        max_templates: int = 4,
        msa_dir: str = "/data/rbg/shared/projects/foldeverything/rcsb/msa",
    ) -> None:
        """Initialize the training dataset.

        Parameters
        ----------
        datasets : List[Dataset]
            The datasets to sample from.

        """
        super().__init__()
        self.dataset = dataset
        self.moldir = moldir
        self.canonicals = canonicals
        self.msa_condition = msa_condition
        self.max_seq = max_seq
        self.max_templates = max_templates
        self.msa_dir = msa_dir

    def __getitem__(self, idx: int) -> Dict:
        """Get an item from the dataset.

        Returns
        -------
        Dict[str, Tensor]
            The sampled data features.

        """
        # Get a sample from the dataset
        pdb_id = self.dataset.target_ids[idx]

        # Load record
        record = load_record(pdb_id, self.dataset.record_dir)

        # Get the structure
        try:
            structure = load_structure(record, self.dataset.struct_dir)
        except Exception as e:  # noqa: BLE001
            print(f"Failed to load input for {pdb_id} with error {e}. Skipping.")  # noqa: T201
            raise e
            return self.__getitem__(0)

        # Tokenize structure
        try:
            tokenized = self.dataset.tokenizer.tokenize(structure)
        except Exception as e:  # noqa: BLE001
            print(f"Tokenizer failed on {pdb_id} with error {e}. Skipping.")  # noqa: T201
            raise e
            return self.__getitem__(0)

        # Find the record with the matching pdb_id
        msas = {}
        if self.msa_condition:
            chain_ids = set(tokenized.tokens["asym_id"])
            if record is None:
                raise print(
                    f"Record with id {pdb_id} not found in manifest. Skip MSA loading."
                )
            else:
                try:
                    msas = load_msas(
                        record=record, chain_ids=chain_ids, msa_dir=self.msa_dir
                    )
                except Exception as e:  # noqa: BLE001
                    print(
                        f"MSA loading failed for {record.id} with error {e}. Skipping."
                    )

        try:
            # Try to find molecules in the dataset moldir if provided
            # Find missing ones in global moldir and check if all found
            molecules = {}
            molecules.update(self.canonicals)
            mol_names = set(tokenized.tokens["res_name"].tolist())
            mol_names = mol_names - set(self.canonicals.keys())
            if self.moldir is not None:
                molecules.update(load_molecules(self.moldir, mol_names))

            mol_names = mol_names - set(molecules.keys())
            molecules.update(load_molecules(self.moldir, mol_names))
        except Exception as e:  # noqa: BLE001
            raise e
            print(f"Molecule loading failed for {record.id} with error {e}. Skipping.")
            return self.__getitem__(0)

        # Finalize input data
        input_data = Input(
            tokens=tokenized.tokens,
            bonds=tokenized.bonds,
            token_to_res=tokenized.token_to_res,
            structure=structure,
            msa=msas,
            templates=None,
            record=record,
        )

        # Compute features
        try:
            features = self.dataset.featurizer.process(
                input_data,
                molecules=molecules,
                random=np.random.default_rng(None),
                training=False,
                max_seqs=self.max_seq,  # if self.msa_condition else 1,
                pad_to_max_seqs=True,
                override_method="X-RAY DIFFRACTION",
            )
        except Exception as e:  # noqa: BLE001
            raise e
            print(f"Featurizer failed on {pdb_id} with error {e}. Skipping.")  # noqa: T201
            return self.__getitem__(0)

        templates_features = load_dummy_templates_v2(
            tdim=self.max_templates, num_tokens=len(features["res_type"])
        )
        features.update(templates_features)
        features["idx_dataset"] = torch.tensor(1)
        features["id"] = pdb_id
        return features

    def __len__(self) -> int:
        """Get the length of the dataset.

        Returns
        -------
        int
            The length of the dataset.

        """
        return len(self.dataset.target_ids)


class FoldingDataModule(pl.LightningDataModule):
    """DataModule for FoldEverything."""

    def __init__(self, cfg: DataConfig, batch_size, num_workers, pin_memory) -> None:
        """Initialize the DataModule.

        Parameters
        ----------
        config : DataConfig
            The data configuration.

        """
        super().__init__()
        self.cfg = cfg
        self.batch_size = batch_size
        self.num_workers = num_workers
        self.pin_memory = pin_memory

        with Path(cfg.target_ids).open("r") as f:
            target_ids = [x.lower() for x in f.read().splitlines()]
            print("split", target_ids)

        dataset = Dataset(
            struct_dir=Path(cfg.target_dir) / "structures",
            record_dir=Path(cfg.target_dir) / "records",
            target_ids=target_ids,
            tokenizer=cfg.tokenizer,
            featurizer=cfg.featurizer,
        )

        # Load canonical molecules
        canonicals = load_canonicals(cfg.moldir)

        self._predict_set = PredictionDataset(
            dataset=dataset,
            canonicals=canonicals,
            moldir=Path(cfg.moldir),
            msa_condition=cfg.msa_condition,
            msa_dir=Path(cfg.msa_dir),
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
            batch_size=self.batch_size,
            num_workers=self.num_workers,
            pin_memory=self.pin_memory,
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
                "id",
                "structure_bonds",
                "extra_mols",
            ]:
                batch[key] = batch[key].to(device)
        return batch
