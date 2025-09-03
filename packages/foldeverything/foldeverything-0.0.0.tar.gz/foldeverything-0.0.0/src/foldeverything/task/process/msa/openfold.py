import os
from pathlib import Path
from typing import List

from foldeverything.data.data import A3M, MSA
from foldeverything.data.parse.a3m import process_a3m
from foldeverything.task.process.msa.msa import MSASource
from foldeverything.task.process.process import Resource


class OpenFoldMSA(MSASource):
    """The OpenFold MSA data source."""

    def fetch(self) -> List[A3M]:
        """Get a list of raw data points.

        Returns
        -------
        List[A3M]
            A list of raw data points

        """
        data = []
        for name in os.listdir(self._data_dir):
            if not Path.is_dir(self._data_dir / name):
                continue

            path = self._data_dir / name
            pdb = path / "pdb" / f"{name}.pdb"
            msa = path / "a3m" / "uniclust30.a3m"
            if (
                pdb.exists()
                and msa.exists()
                and pdb.stat().st_size > 0
                and msa.stat().st_size > 0
            ):
                data.append(A3M(id=name, path=str(msa)))

        return data

    def parse(self, data: A3M, resource: Resource, max_seqs: int) -> MSA:  # noqa: ARG002
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
