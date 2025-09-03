import os
import urllib
import zipfile
from pathlib import Path
from typing import List

import gdown

from foldeverything.eval.data.dataset import Dataset
from foldeverything.eval.protein import Target

# from import parse


# Set of long PDB targets deposited in 2023:
# - PDBs deposited between 2023-01-01 and 2023-12-31
# - Single chain per assembly
# - Over 1000 residues, under 4000
# - Resolution under 4.0A
# - Filtered to avoid duplicates

LONG_TARGETS = [
    "7FSE",
    "8C4A",
    "8C4S",
    "8C6I",
    "8C8U",
    "8FTH",
    "8G3H",
    "8I4A",
    "8IEK",
    "8IF3",
    "8J3W",
    "8JB5",
    "8JBR",
    "8JHU",
    "8JVH",
    "8JX7",
    "8JZN",
    "8K9Q",
    "8OFB",
    "8PD0",
    "8PD9",
    "8PM6",
    "8QEB",
    "8SIB",
    "8SL1",
    "8SSC",
    "8SX7",
    "8SZP",
    "8TN9",
    "8TX1",
    "8TXZ",
    "8TZE",
    "8U7H",
    "8X2H",
]
MSA_URL = "https://drive.google.com/uc?id=1eU4Ot5zrJW-N57YVv6ls41gMfmLdox3W"


class LongProts(Dataset):
    """The dataset of long proteins deposited in 2023.

    - PDBs deposited between 2023-01-01 and 2023-12-31
    - Single chain per assembly
    - Over 1000 residues, under 4000
    - Resolution under 4.0A
    - Filtered to avoid duplicates

    """

    def __init__(self, cache_dir: str, msas: str = MSA_URL) -> None:
        """Initialize the dataset.

        Parameters
        ----------
        cache_dir : str
            The directory to store the dataset.
        msas : str
            Precomputed MSAs to use.

        """
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
        return "LongProts"

    def download(self, cache_dir: str) -> None:
        """Download the dataset.

        Parameters
        ----------
        cache_dir : str
            The directory to store the dataset.

        """
        # Set data dir
        dir_name = "longprots"
        data_dir = Path(cache_dir) / dir_name
        if Path.exists(data_dir):
            print(f"Directory {dir_name} already exists. Skipping download.")
            return

        # Create data dir
        Path.mkdir(data_dir, parents=True, exist_ok=True)

        # Download PDBs
        pdb_dir = data_dir / "pdb"
        Path.mkdir(pdb_dir, parents=True, exist_ok=True)
        for pdb_id in LONG_TARGETS:
            pdb_path = pdb_dir / f"{pdb_id.lower()}.cif"
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
        List[Target]
            The dataset as a list of Target objects.

        """
        data_dir = Path(cache_dir) / "longprots"
        pdb_dir = data_dir / "pdb"

        proteins = []
        for file in os.listdir(pdb_dir):
            if not file.endswith(".cif"):
                continue

            # Load data
            name = file.split(".")[0].lower()
            pdb_path = pdb_dir / file
            with Path.open(pdb_path) as f:
                data = parse(file_id=name, mmcif_string=f.read())
                data = data.mmcif_object

            # Get longest chain
            chain = max(
                data.chain_to_seqres,
                key=lambda x: len(data.chain_to_seqres[x]),
            )
            sequence = data.chain_to_seqres[chain]

            # Get msa path
            msa = data_dir / "a3m" / f"{name}.a3m"

            protein = Target(
                name=name,
                path=pdb_path,
                chain=chain,
                sequence=sequence,
                msa=msa,
            )
            proteins.append(protein)

        return proteins
