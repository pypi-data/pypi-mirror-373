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

from foldeverything.data.mol import load_canonicals
from foldeverything.data.parse.affinity import parse_smiles_sequences
from foldeverything.task.process.process import Resource
from foldeverything.task.process.targets.target import TargetsSource
from foldeverything.data.filter.static.filter import StaticFilter


@dataclass(frozen=True, slots=True)
class Protein:
    """A raw PubChem file."""

    normalized_protein_accession: str
    protein_sequences: str


class PubChemTargets(TargetsSource):
    """The PubChem target data source."""

    def __init__(
        self,
        data_dir: str,
        clusters: str,
        chain_map: str,
        components: str,
        filters: Optional[List[StaticFilter]] = None,
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
        self.components = load_canonicals(self._components)

        proteins_dir = outdir / "proteins"
        proteins_dir.mkdir(parents=True, exist_ok=True)

    def fetch(self) -> List[Protein]:
        """Get a list of raw data points.

        Returns
        -------
        List[Raw]
            A list of raw data points

        """
        with open(self._data_dir, "rb") as f:
            d = pickle.load(f)

        data = []
        for key, value in d.items():
            data.append(
                Protein(normalized_protein_accession=key, protein_sequences=value)
            )

        return data

    def parse(self, data: Protein) -> Target:
        """Process a structure.

        Parameters
        ----------
        data : Protein
            The raw input data.

        Returns
        -------
        Target
            The processed data.

        """

        # Parse protein
        protein = parse_smiles_sequences(
            data.protein_sequences.split(";"), [], self.components
        )
        protein = protein.data

        # Return target
        return protein

    def resource(self) -> Dict:
        """Return a shared resource needed for processing.

        Returns
        -------
        Dict
            The shared resource.

        """
        return None

    def process(self, data: Protein, resource: Resource, outdir: Path) -> None:
        """Process a target.

        Parameters
        ----------
        data : Protein
            The raw input data.
        resource: Resource
            The shared resource.
        outdir : Path
            The output directory.

        """
        # Check if we need to process
        protein_path = outdir / "proteins" / f"{data.normalized_protein_accession}.npz"

        if protein_path.exists():
            return

        try:
            # Parse the target
            protein = self.parse(data)
        except Exception:  # noqa: BLE001
            traceback.print_exc()
            print(f"Failed to parse {data.normalized_protein_accession}")
            return

        # Dump protein structure
        np.savez_compressed(protein_path, **asdict(protein))

    def finalize(self, outdir: Path) -> None:
        """Run post-processing in main thread.

        Parameters
        ----------
        outdir : Path
            The output directory.

        """
        print("Finished!")
