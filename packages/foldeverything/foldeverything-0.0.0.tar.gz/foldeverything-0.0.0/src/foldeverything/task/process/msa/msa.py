from abc import abstractmethod
from dataclasses import asdict
from pathlib import Path

import numpy as np

from foldeverything.data.data import A3M, MSA
from foldeverything.task.process.process import Resource, Source


class MSASource(Source[A3M]):
    """An MSA data source."""

    def __init__(self, data_dir: str, max_seqs: int) -> None:
        """Initialize the data source.

        Parameters
        ----------
        data_dir : str
            The path to the data directory
        max_seqs: int
            The maximum number of sequences.

        """
        self._data_dir = Path(data_dir)
        self._max_seqs = max_seqs

    @abstractmethod
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
        raise NotImplementedError

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
        msa_path.parent.mkdir(parents=True, exist_ok=True)
        if not msa_path.exists():
            try:
                msa = self.parse(data, resource, self._max_seqs)
                np.savez_compressed(msa_path, **asdict(msa))
            except OverflowError as e:
                print(f"OverflowError: {e}")
                print(f"Skipping {data.id}")
