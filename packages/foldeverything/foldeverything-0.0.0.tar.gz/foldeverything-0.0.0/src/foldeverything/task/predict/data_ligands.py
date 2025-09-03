from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List
import re
import numpy as np
import pytorch_lightning as pl
import torch
from torch import Tensor
from torch.utils.data import DataLoader
from rdkit.Chem import Mol
from foldeverything.data import const
from foldeverything.data.data import (
    Input,
    Structure,
)
from foldeverything.data.feature.featurizer import Featurizer
from foldeverything.data.pad import pad_to_max
from foldeverything.data.mol import (
    load_canonicals,
    load_molecules,
    compute_3d,
    mol_from_smile,
)
from foldeverything.data.parse.affinity import parse_smiles_sequences
from foldeverything.data.parse.fasta import parse_polymer
from foldeverything.data.template.features import load_dummy_templates_v2
from foldeverything.data.tokenize.tokenizer import Tokenizer
from foldeverything.data.template.features import (
    load_dummy_templates_v2,
)
from foldeverything.data.select.protein_new import ProteinSelectorNew


@dataclass
class DataConfig:
    """Data configuration."""

    target_dir: str
    msa_dir: str
    moldir: str
    min_len: int
    max_len: int
    target_ids: str
    tokenizer: Tokenizer
    featurizer: Featurizer
    use_templates: bool = False
    max_templates: int = 4
    backbone_only: bool = False
    atom14: bool = False
    atom14_geometric: bool = False
    atom37: bool = False
    design: bool = False
    target_structure_condition: bool = False
    multiplicity: int = 1
    ligand_design: bool = False
    disulfide_prob: float = 1.0
    disulfide_on: bool = False


@dataclass
class Dataset:
    """Data holder."""

    struct_dir: Path
    record_dir: Path
    target_ids: List[str]
    min_len: int
    max_len: int
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
            "tokenized",
            "structure",
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
        design: bool = False,
        target_structure_condition: bool = False,
        max_templates: bool = False,
        use_templates: bool = False,
        anchors_on: bool = False,
        ligand_design: bool = False,
        disulfide_prob: float = 1.0,
        disulfide_on: bool = False,
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
        self.use_templates = use_templates
        self.max_templates = max_templates
        self.backbone_only = backbone_only
        self.atom14 = atom14
        self.atom14_geometric = atom14_geometric
        self.design = design
        self.target_structure_condition = target_structure_condition
        self.atom37 = atom37
        self.anchors_on = anchors_on
        self.ligand_design = ligand_design
        self.disulfide_prob = disulfide_prob
        self.disulfide_on = disulfide_on
        if self.anchors_on:
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

    def __getitem__(self, idx: int) -> Dict:
        """Get an item from the dataset.

        Returns
        -------
        Dict[str, Tensor]
            The sampled data features.

        """
        # Get a sample from the dataset
        target_id = self.dataset.target_ids[idx % len(self.dataset.target_ids)]
        # Get the structure
        try:
            if "prot-" in target_id:
                target_id = target_id.lower()
                seq = target_id.replace("prot-", "")

                str_target = parse_smiles_sequences([seq.upper()], [], self.moldir).data

            elif "smiles-" in target_id:
                smiles_list = target_id.split("smiles-")[1:]
                mols = mol_from_smile(smiles_list)

                # If there is only one atom (e.g. ions), no need to compute 3D.
                # compute_3d overwrites the input mol object.
                _ = [
                    compute_3d(mol) if mol.GetNumAtoms() > 1 else False for mol in mols
                ]
                str_target = parse_smiles_sequences([], mols, self.moldir).data

            else:
                target_id = target_id.lower()
                ccd = target_id.split("_")[0]
                pdb_id = target_id.split("_")[1].lower()
                str_native = Structure.load(self.dataset.struct_dir / f"{pdb_id}.npz")
                res_selection = str_native.residues["name"] == ccd.upper()
                if res_selection.sum() > 1:
                    print(f"CCD {ccd} occurs multiple times in {pdb_id}. Using first.")
                    res_selection = np.arange(len(res_selection))[res_selection][[0]]
                str_target = Structure.extract_residues(str_native, res_selection)

            if self.dataset.min_len == self.dataset.max_len:
                length = self.dataset.min_len
            else:
                length = np.random.random_integers(
                    self.dataset.min_len, self.dataset.max_len
                )
            if self.ligand_design:
                structure = str_native
            else:
                str_prot = Structure.empty_protein(seq_len=length)
                structure = Structure.concatenate(str_prot, str_target)

        except Exception as e:  # noqa: BLE001
            raise e
            print(f"Failed to load input for {target_id}  with error {e}. Skipping.")  # noqa: T201
            return self.__getitem__(0)

        # Tokenize structure
        if self.anchors_on:
            try:
                native_tokenized = self.dataset.tokenizer.tokenize(str_native)
            except Exception as e:
                print(f"Tokenizer failed on {target_id} with error {e}. Skipping.")  # noqa: T201
                return self.__getitem__(0)
        # Check if the structure is valid
        try:
            tokenized = self.dataset.tokenizer.tokenize(structure)
        except Exception as e:  # noqa: BLE001
            print(f"Tokenizer failed on {target_id} with error {e}. Skipping.")  # noqa: T201
            return self.__getitem__(0)

        # Design mask logic
        if self.ligand_design:
            ligand_mask = (
                tokenized.tokens["mol_type"] == const.chain_type_ids["NONPOLYMER"]
            )
            if "_" in target_id and len(target_id.split("_")) == 2:
                ccd_name = target_id.split("_")[0].upper()
                ligand_mask &= tokenized.tokens["res_name"] == ccd_name

            tokenized.tokens["design_mask"] = ligand_mask.astype(
                tokenized.tokens["mol_type"].dtype
            )

            tokenized.tokens["structure_group"][:] = 0
            tokenized.tokens["structure_group"][~tokenized.tokens["design_mask"].astype(bool)] = 1
        else:
            tokenized.tokens["design_mask"] = (
                tokenized.tokens["asym_id"] == tokenized.tokens["asym_id"][0]
            ).astype(tokenized.tokens["asym_id"].dtype)


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
            print(f"Molecule loading failed for {target_id} with error {e}. Skipping.")
            return self.__getitem__(0)
        # Add anchors

        if self.anchors_on:
            native_tokenized.tokens["design_mask"] = (
                native_tokenized.tokens["is_standard"]
                & native_tokenized.tokens["resolved_mask"]
                & (native_tokenized.tokens["res_type"] < 22)
            )
            self.selector.run_distance_sampling(
                native_tokenized.tokens, np.random.default_rng(None)
            )
            anchor_tokens, anchor_structure = self.selector.extract_anchor_tokens(
                str_native, native_tokenized.tokens, np.random.default_rng(None)
            )
            if anchor_tokens is not None:
                tokens, structure = self.selector.add_anchor_tokens(
                    structure,
                    tokenized.tokens,
                    anchor_structure,
                    anchor_tokens,
                    np.random.default_rng(None),
                )
                anchor_atom_to_res_idx = []
                for i in range(anchor_structure.chains["res_num"][0]):
                    anchor_atom_to_res_idx.extend(
                        [i] * anchor_structure.residues["atom_num"][i]
                    )
                token_to_res = np.concatenate(
                    [tokenized.token_to_res, anchor_atom_to_res_idx]
                ).astype(np.int32)
        # Finalize input data
        input_data = Input(
            tokens=tokens
            if self.anchors_on and anchor_tokens is not None
            else tokenized.tokens,
            bonds=tokenized.bonds,
            token_to_res=token_to_res
            if self.anchors_on and anchor_tokens is not None
            else tokenized.token_to_res,
            structure=structure,
            msa={},
            templates=None,
        )

        # Compute features
        try:
            features = self.dataset.featurizer.process(
                input_data,
                molecules=molecules,
                random=np.random.default_rng(None),
                training=False,
                max_seqs=1,
                use_templates=self.use_templates,
                max_templates=self.max_templates,
                backbone_only=self.backbone_only,
                atom14=self.atom14,
                atom14_geometric=self.atom14_geometric,
                atom37=self.atom37,
                design=self.design,
                override_method="X-RAY DIFFRACTION",
                disulfide_prob=self.disulfide_prob,
                disulfide_on=self.disulfide_on,
            )
        except Exception as e:  # noqa: BLE001
            print(f"Featurizer failed on {target_id} with error {e}. Skipping.")  # noqa: T201
            return self.__getitem__(0)

        # Compute template features
        templates_features = load_dummy_templates_v2(
            tdim=1, num_tokens=len(features["res_type"])
        )
        features.update(templates_features)

        features["idx_dataset"] = torch.tensor(1)

        def sanitize_filename(name):
            return re.sub(r"[^A-Za-z0-9._-]", "_", name)

        features["id"] = sanitize_filename(target_id)
        return features

    def __len__(self) -> int:
        """Get the length of the dataset.

        Returns
        -------
        int
            The length of the dataset.

        """
        return len(self.dataset.target_ids) * self.dataset.multiplicity


class LigandBinderDataModule(pl.LightningDataModule):
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
            target_ids = [x for x in f.read().splitlines()]
            print("split", target_ids)

        dataset = Dataset(
            struct_dir=Path(cfg.target_dir) / "structures",
            record_dir=Path(cfg.target_dir) / "records",
            target_ids=target_ids,
            multiplicity=cfg.multiplicity,
            min_len=cfg.min_len,
            max_len=cfg.max_len,
            tokenizer=cfg.tokenizer,
            featurizer=cfg.featurizer,
        )

        # Load canonical molecules
        canonicals = load_canonicals(cfg.moldir)

        self._predict_set = PredictionDataset(
            dataset=dataset,
            canonicals=canonicals,
            moldir=Path(cfg.moldir),
            use_templates=cfg.use_templates,
            max_templates=cfg.max_templates,
            backbone_only=cfg.backbone_only,
            atom14=cfg.atom14,
            atom14_geometric=cfg.atom14_geometric,
            design=cfg.design,
            target_structure_condition=cfg.target_structure_condition,
            ligand_design=cfg.ligand_design,
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
                "tokenized",
                "structure",
                "structure_bonds",
                "extra_mols",
            ]:
                batch[key] = batch[key].to(device)
        return batch
