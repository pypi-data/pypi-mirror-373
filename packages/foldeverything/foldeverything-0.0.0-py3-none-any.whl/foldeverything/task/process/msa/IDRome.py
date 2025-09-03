import json
from pathlib import Path
from typing import Dict, List

from tqdm import tqdm

from foldeverything.data.data import A3M, MSA
from foldeverything.data.parse.a3m import process_a3m
from foldeverything.task.process.msa.msa import MSASource
from foldeverything.task.process.process import Resource


class IDRomeMSA(MSASource):
    """The IDRome MSA data source."""

    def __init__(
        self,
        data_dir: str,
        max_seqs: int,
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
        print("Initializing IDRomeMSA")
        super().__init__(data_dir, max_seqs)

    def fetch(self) -> List[A3M]:
        """Get a list of raw data points.

        Returns
        -------
        List[A3M]
            A list of raw data points

        """
        print("Fetching IDRomeMSA")
        data: List[A3M] = []

        for file in tqdm(self._data_dir.rglob("*.a3m*")):
            msa_id = str(file.stem).split(".")[0].upper()
            msa = A3M(id=msa_id, path=str(file))
            data.append(msa)

        return data

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
        return process_a3m(Path(data.path), {}, max_seqs)
