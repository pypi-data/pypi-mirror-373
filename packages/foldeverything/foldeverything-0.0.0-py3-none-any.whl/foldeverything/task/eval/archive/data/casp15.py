import os
import urllib
import zipfile
from pathlib import Path
from typing import List

import edit_distance
import gdown
import pandas as pd
from Bio import SeqIO

from foldeverything.eval.data.dataset import Dataset
from foldeverything.eval.protein import Target

# from import parse

# Download links
LIST_URL = "https://predictioncenter.org/casp15/targetlist.cgi?type=csv"
SEQS_URL = "https://predictioncenter.org/download_area/CASP15/sequences/casp15.seq.txt"
MSA_URL = "https://drive.google.com/uc?id=1tvxRXrUc3uxdEws9shiO916fG_wJPJ-C"


class CASP15(Dataset):
    """CASP15 dataset with all RCSB accessible targets."""

    def __init__(
        self,
        cache_dir: str,
        msas: str = MSA_URL,
    ) -> None:
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
        return "CASP15"

    def download(self, cache_dir: str) -> None:
        """Download the dataset.

        Parameters
        ----------
        cache_dir : str
            The directory to store the dataset.

        """
        # Set data dir
        dir_name = "casp15"
        data_dir = Path(cache_dir) / dir_name
        if Path.exists(data_dir):
            print(f"Directory {dir_name} already exists. Skipping download.")
            return

        # Create data dir
        Path.mkdir(data_dir, parents=True, exist_ok=True)

        # Download target list
        targets_file = data_dir / "list.csv"
        urllib.request.urlretrieve(LIST_URL, targets_file)

        # Download sequences
        seq_file = data_dir / "seqs.fasta"
        urllib.request.urlretrieve(SEQS_URL, seq_file)

        # Download target pdb's
        metadata = pd.read_csv(targets_file, sep=";", on_bad_lines="warn")
        metadata = metadata[metadata["Target"].str.startswith("T")]
        metadata = metadata[metadata["Cancellation Date"] == "-"]

        Path.mkdir(data_dir / "pdb", parents=True, exist_ok=True)
        for _, row in metadata.iterrows():
            desc = row["Description"].strip().split(" ")
            if len(desc) < 2:
                continue

            pdb_id = desc[-1]
            if len(pdb_id) != 4:
                continue

            try:
                pdb_url = f"https://files.rcsb.org/view/{pdb_id.upper()}.cif"
                pdb_path = data_dir / "pdb" / f"{row['Target']}.cif"
                urllib.request.urlretrieve(pdb_url, pdb_path)
            except urllib.error.HTTPError:
                pass

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
            The list of protein targets.

        """
        # Set data dir
        data_dir = Path(cache_dir) / "casp15"

        # Read sequences
        with Path.open(data_dir / "seqs.fasta") as f:
            seqs = SeqIO.parse(f, "fasta")
            seqs = {seq.id: str(seq.seq) for seq in seqs}

        # Read targets
        targets = os.listdir(data_dir / "pdb")
        targets = [t.split(".")[0] for t in targets if t.endswith(".cif")]

        # Load proteins
        proteins = []
        for name in targets:
            # Find matching chain by taking closest edit distance
            sequence = seqs[name]

            # We need to load the data for that
            pdb_path = data_dir / "pdb" / f"{name}.cif"
            if not Path.exists(pdb_path):
                msg = f"File {pdb_path} does not exist"
                raise FileNotFoundError(msg)

            with Path.open(pdb_path) as f:
                data = parse(file_id=name, mmcif_string=f.read())
                data = data.mmcif_object

            closest = None
            chains = list(data.chain_to_seqres.keys())
            for chain in chains:
                seq = data.chain_to_seqres[chain]
                dist = edit_distance.edit_distance(seq, sequence)
                if closest is None or (dist < closest[1]):
                    closest = (chain, dist)

            # Get msa path
            msa = data_dir / "a3m" / f"{name}.a3m"

            chain = closest[0]
            protein = Target(
                name=name, path=pdb_path, chain=chain, sequence=sequence, msa=msa
            )
            proteins.append(protein)

        return proteins
