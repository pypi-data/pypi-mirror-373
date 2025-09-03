import json
import os
import re
import urllib
import zipfile
from pathlib import Path
from typing import List, Optional

import gdown
import requests

from foldeverything.eval.data.dataset import Dataset
from foldeverything.eval.protein import Target

# from import parse

VALID_PERIODS = [
    "1-year",
    "6-months",
    "3-months",
    "1-month",
    "1-week",
]

ESMFOLD_DATE = "2022-04-01"
ESMFOLD_PERIOD = "3-months"
ESMFOLD_MSA = "https://drive.google.com/uc?id=1u3fhKTpKd1JFHVM4f-LwUkZqGYAA4oTG"


class CAMEO(Dataset):
    """CAMEO Dataset."""

    def __init__(
        self,
        cache_dir: str,
        period: str = ESMFOLD_PERIOD,
        end_date: str = ESMFOLD_DATE,
        msas: str = ESMFOLD_MSA,
        max_len: Optional[int] = None,
    ) -> None:
        """Initialize the dataset.

        Parameters
        ----------
        cache_dir : str
            The directory to store the dataset.
        period : str
            The length of the period from which to draw.
        end_date : str
            The end date, in YYYY-MM-DD format.
        msas : str
            Precomputed MSAs to use.
        max_len : Optional[int]
            The max length of proteins to load.

        """
        if period not in VALID_PERIODS:
            msg = f"Invalid period. Choose from {VALID_PERIODS}"
            raise ValueError(msg)

        date_regex = re.compile("^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
        if not date_regex.match(end_date):
            msg = f"Invalid date: {end_date}. Use YYYY-MM-DD format"
            raise ValueError(msg)

        self._period = period
        self._end = end_date
        self._max_len = max_len
        self._msas = msas

        super().__init__(cache_dir)

    @property
    def name(self) -> str:
        """The name of the dataset.

        Returns
        -------
        str
            The name of the metric.

        """
        name = f"CAMEO_{self._period}_{self._end}"
        if self._max_len is not None:
            name += f"<{self._max_len}r"

        return name

    def download(self, cache_dir: str) -> None:
        """Download the dataset.

        Parameters
        ----------
        cache_dir : str
            The directory to store the dataset.

        """
        # Set data dir
        dir_name = f"cameo_{self._period}_{self._end}"
        data_dir = Path(cache_dir) / dir_name
        if Path.exists(data_dir):
            print(f"Directory {dir_name} already exists. Skipping download.")
            return

        # Create data dir
        Path.mkdir(data_dir, parents=True, exist_ok=True)

        # Download the pdbs
        pdb_dir = data_dir / "pdb"
        Path.mkdirs(pdb_dir, exist_ok=True)
        url = "/".join(
            [
                "https://www.cameo3d.org/",
                "modeling",
                "targets",
                self._period,
                "ajax",
                f"?to_date={self._end}",
            ]
        )
        raw_data = requests.get(url, timeout=10).text
        parsed_data = json.loads(raw_data)
        chain_data = parsed_data["aaData"]
        for chain in chain_data:
            pdb_id = chain["pdbid"].lower()
            chain_id = chain["pdbid_chain"]

            pdb_path = pdb_dir / f"{pdb_id}_{chain_id}.cif"
            pdb_url = f"https://files.rcsb.org/view/{pdb_id.upper()}.cif"
            urllib.request.urlretrieve(pdb_url, pdb_path)

        # Download the MSAs from google drive
        msa_file = data_dir / "a3m.zip"
        msa_dir = data_dir / "a3m"
        gdown.download(self._msas, msa_file)
        with zipfile.ZipFile(msa_file, "r") as zip_ref:
            zip_ref.extractall(msa_dir)

        # Delete the zip file
        Path.unlink(msa_file)

    def load(self, cache_dir: str) -> List[Target]:
        """Load the dataset.

        Parameters
        ----------
        cache_dir : str
            The directory to store the dataset.

        Returns
        -------
        List[Protein]
            The dataset as a list of Protein objects.

        """
        # Set data dir
        dir_name = f"cameo_{self._period}_{self._end}"
        data_dir = Path(cache_dir) / dir_name
        pdb_dir = data_dir / "pdb"

        proteins = []
        for file in os.listdir(pdb_dir):
            if not file.endswith(".cif"):
                continue

            # We need to parse the file to get the sequence
            name = file.split(".")[0]
            pdb_id, chain = name.split("_")
            pdb_id = pdb_id.lower()
            pdb_path = pdb_dir / file
            with Path.open(pdb_path) as f:
                data = parse(file_id=name, mmcif_string=f.read())
                data = data.mmcif_object

            seq = data.chain_to_seqres[chain]
            if (self._max_len is not None) and (len(seq) > self._max_len):
                continue

            # Get msa path
            msa = data_dir / "a3m" / f"{name}.a3m"

            # Create target object
            protein = Target(
                name=name,
                path=pdb_path,
                chain=chain,
                sequence=seq,
                msa=msa,
            )
            proteins.append(protein)

        return proteins
