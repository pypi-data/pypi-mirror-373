from dataclasses import asdict
import json
from pathlib import Path
from typing import Dict, List

import numpy as np

from foldeverything.data.data import A3M, MSA
from foldeverything.data.parse.a3m import process_a3m
from foldeverything.task.process.msa.msa import MSASource
from foldeverything.task.process.process import Resource


class PubChemMSA(MSASource):
    """The PubChem MSA data source."""

    def __init__(
        self,
        data_dir: str,
        max_seqs: int,
        taxonomy: str,
    ) -> None:
        """Initialize the data source.

        Parameters
        ----------
        data_dir : str
            Path to the MSA data.
        taxonomy : str
            Path to the taxonomy file.
        max_seqs: int
            The maximum number of sequences.

        """
        super().__init__(data_dir, max_seqs)
        self._taxonomy = taxonomy

    def fetch(self) -> List[A3M]:
        """Get a list of raw data points.

        Returns
        -------
        List[A3M]
            A list of raw data points

        """
        data: List[A3M] = []
        for file in self._data_dir.rglob("*.a3m.gz"):
            msa_id = ".".join(file.name.split(".")[:-2])
            msa = A3M(id=msa_id, path=str(file))
            data.append(msa)
        for file in self._data_dir.rglob("*.a3m"):
            msa_id = ".".join(file.name.split(".")[:-1])
            msa = A3M(id=msa_id, path=str(file))
            data.append(msa)

        return data

    def resource(self) -> Dict:
        """Return a shared resource needed for processing.

        Returns
        -------
        Dict
            The shared resource.

        """
        return None

    def parse(self, data: A3M, resource: Resource, max_seqs: int) -> MSA:
        """Process a target.

        Parameters
        ----------
        data : A3M
            The raw input data.
        resource: Resource
            The shared resource.
        max_seqs: int
            The maximum number of sequences.

        """
        return process_a3m(Path(data.path), resource, max_seqs)

    def process(self, data: A3M, resource: Resource, outdir: Path) -> None:
        """Run processing in a worker thread.

        Parameters
        ----------
        data : A3M
            The raw input data.
        resource: Resource
            The shared resource.
        outdir : Path
            The output directory.

        """
        msa_path = outdir / f"{data.id}.npz"
        msa = self.parse(data, None, self._max_seqs)
        np.savez_compressed(msa_path, **asdict(msa))
