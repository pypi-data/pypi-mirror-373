from pathlib import Path
from typing import List

from foldeverything.data.data import A3M, MSA
from foldeverything.data.parse.a3m import process_a3m
from foldeverything.task.process.msa.msa import MSASource
from foldeverything.task.process.process import Resource


class AFDBMSA(MSASource):
    """The AFDB MSA data source."""

    def __init__(self, data_dir: str, max_seqs: int, ids: str) -> None:
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
        self._ids = set(Path(ids).read_text().splitlines())

    def fetch(self) -> List[A3M]:
        """Get a list of raw data points.

        Returns
        -------
        List[A3M]
            A list of raw data points

        """
        data = []
        for path in Path(self._data_dir).glob("**/*.a3m.gz"):
            name = path.name.split(".")[0]
            full_name = path.parent.name + "/" + name
            if name in self._ids:
                data.append(A3M(id=full_name, path=str(path)))
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
