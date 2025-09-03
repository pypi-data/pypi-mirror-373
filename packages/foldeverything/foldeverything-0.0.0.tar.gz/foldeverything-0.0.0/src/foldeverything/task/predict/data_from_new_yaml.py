from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Union

import numpy as np
import pytorch_lightning as pl
import torch
from torch import Tensor
from torch.utils.data import DataLoader
from rdkit.Chem import Mol
import yaml
from foldeverything.data import const
from foldeverything.data.data import Input, Structure
from foldeverything.data.feature.featurizer import Featurizer
from foldeverything.data.loading_utils import load_record, load_structure
from foldeverything.data.pad import pad_to_max
from foldeverything.data.mol import load_canonicals, load_molecules
from foldeverything.data.parse import mmcif
from foldeverything.data.parse.schema import parse_boltz_schema, parse_yaml
from foldeverything.data.parse.schema import parse_yaml
from foldeverything.data.sample.sampler import Sample
from foldeverything.data.template.features import load_dummy_templates_v2
from foldeverything.data.tokenize.tokenizer import Tokenizer
from foldeverything.data.tokenize.af3 import TokenData
from foldeverything.data.data import Residue, Bond, Atom, Chain
from foldeverything.data.data import Structure
from foldeverything.data.data import Input
from foldeverything.data.data import DesignInfo
from foldeverything.data.data import StructureInfo
from foldeverything.data.select.protein_new import ProteinSelectorNew
from dataclasses import replace, astuple


@dataclass
class DataConfig:
    """Data configuration."""

    moldir: str
    multiplicity: int
    yaml_path: Union[List[str], str]
    tokenizer: Tokenizer
    featurizer: Featurizer
    backbone_only: bool = False
    atom14: bool = False
    atom14_geometric: bool = False
    atom37: bool = False
    design: bool = True


@dataclass
class Dataset:
    yaml_path: Union[List[str], str]
    tokenizer: Tokenizer
    featurizer: Featurizer
    multiplicity: int = 1


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
            "structure",
            "tokenized",
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
        backbone_only: bool = False,
        atom14: bool = False,
        atom14_geometric: bool = False,
        atom37: bool = False,
        extra_features: Optional[List[str]] = None,
        design: bool = True,
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
        path = dataset.yaml_path
        self.yaml_paths = [path] if isinstance(path, str) else path
        self.extra_features = (
            set(extra_features) if extra_features is not None else set()
        )
        self.selector = (
            ProteinSelectorNew(  # Need to change this if we modify the anchors.yaml
                design_neighborhood_sizes=[2, 4, 6, 8, 10, 12, 14, 16, 18],
                substructure_neighborhood_sizes=[2, 4, 6, 8, 10, 12, 24],
                structure_condition_prob=1.0,
                distance_noise_std=1,
                run_selection=True,
                specify_binding_sites=True,
                ss_condition_prob=0.1,
                select_all=False,
                chain_reindexing=False,
                anchor_prob=1.0,
                max_num_anchor_residues=4,
            )
        )
        self.design = design

    def __getitem__(self, idx: int) -> Dict:
        """Get an item from the dataset.

        Returns
        -------
        Dict[str, Tensor]
            The sampled data features.

        """
        path = Path(self.yaml_paths[idx % len(self.yaml_paths)])

        parsed = parse_yaml(path, mol_dir=self.moldir, mols={})
        structure = parsed.structure
        design_info = parsed.design_info

        # Tokenize structure
        tokenized = self.dataset.tokenizer.tokenize(structure)

        # Transfer conditioning information that is stored in tokens
        token_to_res = tokenized.token_to_res
        tokenized.tokens["design_mask"] = design_info.res_design_mask[token_to_res]
        tokenized.tokens["binding_type"] = design_info.res_binding_type[token_to_res]
        tokenized.tokens["structure_group"] = design_info.res_structure_groups[
            token_to_res
        ]
        if parsed.anchor_data is not None:
            tokens, structure = self.selector.add_anchor_tokens(
                structure,
                tokenized.tokens,
                parsed.anchor_data["structure"],
                parsed.anchor_data["tokens"],
                np.random.default_rng(None),
            )
            parsed.anchor_data["token_to_res"] += len(tokenized.structure.residues)
            tokenized = replace(tokenized, tokens=tokens, structure=structure)
            token_to_res = np.concatenate(
                [tokenized.token_to_res, parsed.anchor_data["token_to_res"]]
            ).astype(np.int32)
        # Try to find molecules in the dataset moldir if provided
        # Find missing ones in global moldir and check if all found
        molecules = {}
        molecules.update(self.canonicals)
        mol_names = set(tokenized.tokens["res_name"].tolist())
        mol_names = mol_names - set(self.canonicals.keys())
        mol_names = mol_names - set(parsed.extra_mols.keys())
        if self.moldir is not None:
            molecules.update(load_molecules(self.moldir, mol_names))

        mol_names = mol_names - set(molecules.keys())
        molecules.update(load_molecules(self.moldir, mol_names))
        molecules.update(parsed.extra_mols)

        # Finalize input data
        input_data = Input(
            tokens=tokenized.tokens,
            bonds=tokenized.bonds,
            token_to_res=token_to_res,
            structure=structure,
            msa={},
            templates=None,
        )
        # Compute features
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
            override_method="X-RAY DIFFRACTION",
            charge_info=None
            if tokenized.tokens["is_anchor"].sum() == 0
            else parsed.anchor_data["charge_info"],
        )

        # transfer secondary structure conditioning
        ss_type = design_info.res_ss_types[token_to_res]
        features["ss_type"] = torch.from_numpy(ss_type).to(features["ss_type"])
        features["design_ss_mask"][ss_type != const.ss_type_ids["UNSPECIFIED"]] = 1

        # Compute template features
        templates_features = load_dummy_templates_v2(
            tdim=1, num_tokens=len(features["res_type"])
        )
        features.update(templates_features)

        # set last necessary features
        features["idx_dataset"] = torch.tensor(1)
        features["id"] = path.stem
        if "structure" in self.extra_features:
            features["structure"] = structure
        if "tokenized" in self.extra_features:
            features["tokenized"] = tokenized
        return features

    def __len__(self) -> int:
        """Get the length of the dataset.

        Returns
        -------
        int
            The length of the dataset.

        """
        return len(self.yaml_paths) * self.dataset.multiplicity


class FromYamlDataModule(pl.LightningDataModule):
    """DataModule for FoldEverything."""

    def __init__(
        self, cfg: DataConfig, batch_size, num_workers, pin_memory, extra_features=None
    ) -> None:
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

        dataset = Dataset(
            yaml_path=cfg.yaml_path,
            multiplicity=cfg.multiplicity,
            tokenizer=cfg.tokenizer,
            featurizer=cfg.featurizer,
        )

        # Load canonical molecules
        canonicals = load_canonicals(cfg.moldir)

        self._predict_set = PredictionDataset(
            dataset=dataset,
            canonicals=canonicals,
            moldir=Path(cfg.moldir),
            backbone_only=cfg.backbone_only,
            atom14=cfg.atom14,
            atom14_geometric=cfg.atom14_geometric,
            atom37=cfg.atom37,
            extra_features=extra_features,
            design=cfg.design,
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
                "structure",
                "tokenized",
                "structure_bonds",
                "extra_mols",
            ]:
                batch[key] = batch[key].to(device)
        return batch
