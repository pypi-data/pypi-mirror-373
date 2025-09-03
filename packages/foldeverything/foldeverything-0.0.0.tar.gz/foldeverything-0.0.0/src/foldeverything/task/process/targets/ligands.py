import pickle
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import replace, asdict, dataclass

import json
import traceback

import numpy as np
import pandas as pd
from tqdm import tqdm
import rdkit

from foldeverything.data import const
from foldeverything.data.data import (
    Atom,
    Bond,
    Chain,
    ChainInfo,
    PubChem,
    Record,
    Residue,
    Structure,
    StructureInfo,
    InterfaceInfo,
    Target,
    AffinityInfo,
)
from foldeverything.data.parse.affinity import parse_smiles_sequences
from foldeverything.task.process.process import Resource
from foldeverything.task.process.targets.target import TargetsSource
from foldeverything.data.filter.static.filter import StaticFilter
from rdkit.Chem import Mol


@dataclass(frozen=True, slots=True)
class Ligand:
    """A raw PubChem file."""

    cid: int
    smiles: str
    mol: Mol


class PubChemTargets(TargetsSource):
    """The PubChem target data source."""

    def __init__(
        self,
        data_dir: str,
        components: str,
        clusters: str,
        chain_map: str,
        filters: Optional[List[StaticFilter]] = None,
        filter_num_heavy_atoms: int = 5
    ) -> None:
        """Initialize the data source.

        Parameters
        ----------
        data_dir : str
            Directory containing the dataframe.

        """
        super().__init__(data_dir, components, filters)
        self._data_dir = Path(data_dir)
        self._components = components
        self.filter_num_heavy_atoms = filter_num_heavy_atoms

    def setup(self, outdir: Path) -> None:
        """Run pre-processing in main thread.

        Parameters
        ----------
        outdir : Path
            The output directory.

        """
        # Set default pickle properties
        pickle_option = rdkit.Chem.PropertyPickleOptions.AllProps
        rdkit.Chem.SetDefaultPickleProperties(pickle_option)

        ligands_dir = outdir / "ligands"
        ligands_dir.mkdir(parents=True, exist_ok=True)

    def fetch(self) -> List[Ligand]:
        """Get a list of raw data points.

        Returns
        -------
        List[Raw]
            A list of raw data points

        """
        with open(self._data_dir, "rb") as f:
            d = pickle.load(f)

        with Path(self._components).open("rb") as f:
            components = pickle.load(f)

        data = []
        failed = 0
        for key, value in d.items():
            try:
                data.append(Ligand(cid=key, smiles=value, mol=components[str(key)]))
            except:
                failed += 1
        print(f"Failed ligands to parse: {failed}")
        return data

    def parse(self, data: Ligand) -> Target:
        """Process a structure.

        Parameters
        ----------
        data : Ligand
            The raw input data.

        Returns
        -------
        Target
            The processed data.

        """

        # Parse protein
        ligand = parse_smiles_sequences([], [data.mol], None)
        ligand = ligand.data

        # raise Exception if ligand has less thatn < 5 atoms
        if ligand.atoms.shape[0] < self.filter_num_heavy_atoms:
            raise Exception("Number of heavy atoms is too small!")

        # Return target
        return ligand

    def resource(self) -> Dict:
        """Return a shared resource needed for processing.

        Returns
        -------
        Dict
            The shared resource.

        """
        return None

    def process(self, data: Ligand, resource: Resource, outdir: Path) -> None:
        """Process a target.

        Parameters
        ----------
        data : Ligand
            The raw input data.
        resource: Resource
            The shared resource.
        outdir : Path
            The output directory.

        """
        # Check if we need to process
        ligand_path = outdir / "ligands" / f"{data.cid}.npz"

        if ligand_path.exists():
            return

        try:
            # Parse the target
            ligand = self.parse(data)
        except Exception:  # noqa: BLE001
            # traceback.print_exc()
            print(f"Failed to parse {data.cid}")
            return

        # Dump ligand structure
        np.savez_compressed(ligand_path, **asdict(ligand))

    def finalize(self, outdir: Path) -> None:
        """Run post-processing in main thread.

        Parameters
        ----------
        outdir : Path
            The output directory.

        """
        print("Finished!")
