from dataclasses import dataclass, replace
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import pytorch_lightning as pl
import torch
from torch import Tensor
from torch.utils.data import DataLoader
from rdkit.Chem import Mol
from foldeverything.data import const
from foldeverything.data.crop.cropper import Cropper
from foldeverything.data.data import Input, Structure, Record, Manifest, MSA
from foldeverything.data.feature.featurizer import Featurizer
from foldeverything.data.select.selector import Selector
from foldeverything.data.filter.dynamic.filter import DynamicFilter
from foldeverything.data.pad import pad_to_max
from foldeverything.data.mol import load_canonicals, load_molecules
from foldeverything.data.sample.sampler import Sampler
from foldeverything.data.tokenize.tokenizer import Tokenizer
from foldeverything.data.loading_utils import load_record, load_structure
from foldeverything.task.predict.data_protein_binder import load_msas


@dataclass
class DataConfig:
    """Data configuration."""

    target_dir: str
    msa_dir: str
    moldir: str
    seq_len: int
    target_ids: str
    scaffold_task_dir: str
    tokenizer: Tokenizer
    featurizer: Featurizer
    selector: Selector
    backbone_only: bool = False
    atom14: bool = False
    atom14_geometric: bool = False
    atom37: bool = False
    design: bool = False
    target_structure_condition: bool = False
    msa_condition: bool = False
    max_seq: int = 1024

@dataclass
class Dataset:
    """Data holder."""

    struct_dir: Path
    record_dir: Path
    target_ids: List[str]
    scaffold_task_dir: Path
    seq_len: int
    tokenizer: Tokenizer
    featurizer: Featurizer
    selector: Selector
    sampler: Optional[Sampler] = None
    cropper: Optional[Cropper] = None


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


def parse_scaffold_samples_csv(scaffold_task_dir: Path, pdb_id: str):
    """
    Parse the CSV file at scaffold_task_dir / pdb_id / f'{pdb_id}_samples.csv'.
    Returns a list of lists, each entry split by commas.
    """
    csv_path = scaffold_task_dir / pdb_id / f"{pdb_id}_samples.csv"
    entries = []
    if csv_path.exists():
        with open(csv_path, "r") as f:
            for line in f:
                entries.append(line.strip().split(","))
    return entries


class PredictionDataset(torch.utils.data.Dataset):
    """Base iterable dataset."""

    def __init__(
        self,
        dataset: Dataset,
        canonicals: dict[str, Mol],
        moldir: str,
        backbone_only: bool = False,
        atom14: bool = False,
        atom14_geometric: bool = False,
        atom37: bool = False,
        design: bool = False,
        all_res_ref_pos: np.ndarray = None,
        target_structure_condition: bool = False,
        msa_condition: bool = False,
        max_seq: int = 1024,
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
        self.backbone_only = backbone_only
        self.atom14 = atom14
        self.atom14_geometric = atom14_geometric
        self.atom37 = atom37
        self.design = design
        self.all_res_ref_pos = all_res_ref_pos
        self.target_structure_condition = target_structure_condition
        self.msa_condition = msa_condition
        self.max_seq = max_seq
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
        scaffold_task_dir = self.dataset.scaffold_task_dir
        
        

        # Load record
        record = load_record(pdb_id, self.dataset.record_dir)

        # Get the structure
        try:
            str_native = load_structure(record, self.dataset.struct_dir)
        except Exception as e:  # noqa: BLE001
            print(f"Failed to load input for {pdb_id} with error {e}. Skipping.")  # noqa: T201
            return self.__getitem__(0)

        # Tokenize structure
        try:
            tokenized = self.dataset.tokenizer.tokenize(str_native)
        except Exception as e:  # noqa: BLE001
            print(f"Tokenizer failed on {pdb_id} with error {e}. Skipping.")  # noqa: T201
            return self.__getitem__(0)

        # Set the scaffolding part to be designed
        try:
            self.dataset.selector.select_scaffold(
                tokenized.tokens,
                random=np.random.default_rng(None),
                fixed_crop=True,
            )

        except Exception as e:
            print(f"Selector failed on {pdb_id} with error {e}. Skipping.")
            return self.__getitem__(0)

        if self.target_structure_condition:
            tokenized.tokens["structure_group"][
                ~tokenized.tokens["design_mask"].astype(bool)
            ] = 1

        # possibly add the msa conditioning and find molecules in the dataset as in data_protein_binder?
        # Find the record with the matching pdb_id
        msas = {}
        if self.msa_condition:
            chain_ids = set(
                tokenized.tokens["asym_id"][
                    tokenized.tokens["target_msa_mask"].astype(bool)
                ]
            )
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
        input_data = Input(
            tokens=tokenized.tokens,
            bonds=tokenized.bonds,
            structure=str_native,
            msa={},
            templates=None,
            record=record,
        )

        # Compute features
        # max_seqs do it same as in data_protein_binder?
        try:
            features = self.dataset.featurizer.process(
                input_data,
                molecules=molecules,
                random=np.random.default_rng(None),
                training=False,
                max_seqs=1,
                backbone_only=self.backbone_only,
                atom14=self.atom14,
                atom14_geometric=self.atom14_geometric,
                atom37=self.atom37,
                design=self.design,
                all_res_ref_pos=self.all_res_ref_pos,
                pad_to_max_seqs=True,
                override_method="X-RAY DIFFRACTION",
            )
        except Exception as e:  # noqa: BLE001
            print(f"Featurizer failed on {pdb_id} with error {e}. Skipping.")  # noqa: T201
            return self.__getitem__(0)

        # the extra 2 lines as in data_protein_binder?
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


class ScaffoldLabDataModule(pl.LightningDataModule):
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
            seq_len=cfg.seq_len,
            tokenizer=cfg.tokenizer,
            featurizer=cfg.featurizer,
            selector=cfg.selector,
        )

        canonicals = load_canonicals(cfg.moldir)

        self._predict_set = PredictionDataset(
            dataset=dataset,
            canonicals=canonicals,
            moldir=Path(cfg.moldir),
            backbone_only=cfg.backbone_only,
            atom14=cfg.atom14,
            atom14_geometric=cfg.atom14_geometric,
            atom37=cfg.atom37,
            design=cfg.design,
            target_structure_condition=cfg.target_structure_condition,
            msa_condition=cfg.msa_condition,
            max_seq=cfg.seq_len,
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
