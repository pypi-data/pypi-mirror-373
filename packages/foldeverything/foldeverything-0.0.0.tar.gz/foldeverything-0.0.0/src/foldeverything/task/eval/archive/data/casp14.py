import tarfile
import urllib
import zipfile
from pathlib import Path
from typing import List

import gdown
import pandas as pd
from Bio import SeqIO

from foldeverything.eval.data.dataset import Dataset
from foldeverything.eval.protein import Target

# from import parse

# Download links
LIST_URL = "https://predictioncenter.org/casp14/targetlist.cgi?type=csv"
SEQS_URL = "https://predictioncenter.org/download_area/CASP14/sequences/casp14.seq.txt"
PDBS_URL = "https://predictioncenter.org/download_area/CASP14/targets/_4invitees/casp14.targ.whole.4invitees.tgz"
MSA_URL = "https://drive.google.com/uc?id=10gVJ91oQDSNsHkBqa6puDvkuxzTfm1GY"

# Set of targets utilized in the ColabFold paper
# Omits T1044, T1077, T1085, T1086, T1088
CASP14_COLABFOLD_PAPER = [
    "T1024",
    "T1025",
    "T1026",
    "T1027",
    "T1028",
    "T1029",
    "T1030",
    "T1031",
    "T1032",
    "T1033",
    "T1034",
    "T1035",
    "T1036s1",
    "T1037",
    "T1038",
    "T1039",
    "T1040",
    "T1041",
    "T1042",
    "T1043",
    "T1045s1",
    "T1045s2",
    "T1046s1",
    "T1046s2",
    "T1047s1",
    "T1047s2",
    "T1049",
    "T1050",
    "T1052",
    "T1053",
    "T1054",
    "T1055",
    "T1056",
    "T1057",
    "T1058",
    "T1060s2",
    "T1060s3",
    "T1061",
    "T1064",
    "T1065s1",
    "T1065s2",
    "T1067",
    "T1068",
    "T1070",
    "T1073",
    "T1074",
    "T1076",
    "T1078",
    "T1079",
    "T1080",
    "T1082",
    "T1083",
    "T1084",
    "T1087",
    "T1089",
    "T1090",
    "T1091",
    "T1092",
    "T1093",
    "T1094",
    "T1095",
    "T1096",
    "T1099",
    "T1100",
    "T1101",
]

# Set of domains utilized in the Colabfold paper
# Currently unused but for reference
CASP14_DOMAINS_COLABFOLD_PAPER = [
    "T1024-D1",
    "T1024-D2",
    "T1025-D1",
    "T1026-D1",
    "T1027-D1",
    "T1028-D1",
    "T1029-D1",
    "T1030-D1",
    "T1030-D2",
    "T1031-D1",
    "T1032-D1",
    "T1033-D1",
    "T1034-D1",
    "T1035-D1",
    "T1036s1-D1",
    "T1037-D1",
    "T1038-D1",
    "T1038-D2",
    "T1039-D1",
    "T1040-D1",
    "T1041-D1",
    "T1042-D1",
    "T1043-D1",
    "T1045s1-D1",
    "T1045s2-D1",
    "T1046s1-D1",
    "T1046s2-D1",
    "T1047s1-D1",
    "T1047s2-D1",
    "T1047s2-D2",
    "T1047s2-D3",
    "T1049-D1",
    "T1050-D1",
    "T1050-D2",
    "T1050-D3",
    "T1052-D1",
    "T1052-D2",
    "T1052-D3",
    "T1053-D1",
    "T1053-D2",
    "T1054-D1",
    "T1055-D1",
    "T1056-D1",
    "T1057-D1",
    "T1058-D1",
    "T1058-D2",
    "T1060s2-D1",
    "T1060s3-D1",
    "T1061-D1",
    "T1061-D2",
    "T1061-D3",
    "T1064-D1",
    "T1065s1-D1",
    "T1065s2-D1",
    "T1067-D1",
    "T1068-D1",
    "T1070-D1",
    "T1070-D2",
    "T1070-D3",
    "T1070-D4",
    "T1073-D1",
    "T1074-D1",
    "T1076-D1",
    "T1078-D1",
    "T1079-D1",
    "T1080-D1",
    "T1082-D1",
    "T1083-D1",
    "T1084-D1",
    "T1087-D1",
    "T1089-D1",
    "T1090-D1",
    "T1091-D1",
    "T1091-D2",
    "T1091-D3",
    "T1091-D4",
    "T1092-D1",
    "T1092-D2",
    "T1093-D1",
    "T1093-D2",
    "T1093-D3",
    "T1094-D1",
    "T1094-D2",
    "T1095-D1",
    "T1096-D1",
    "T1096-D2",
    "T1099-D1",
    "T1100-D1",
    "T1100-D2",
    "T1101-D1",
    "T1101-D2",
]


# Reduced list of targets for ESMFold paper
# Limited to after May 2020 in RCSB, up to July 2022.
CASP14_ESMFOLD_PAPER = [
    "T1024",
    "T1025",
    "T1026",
    "T1027",
    "T1028",
    "T1029",
    "T1030",
    "T1031",
    "T1032",
    "T1033",
    "T1034",
    "T1035",
    "T1036s1",
    "T1037",
    "T1038",
    "T1039",
    "T1040",
    "T1041",
    "T1042",
    "T1043",
    "T1044",
    "T1045s1",
    "T1045s2",
    "T1046s1",
    "T1046s2",
    "T1047s1",
    "T1047s2",
    "T1049",
    "T1050",
    "T1053",
    "T1054",
    "T1055",
    "T1056",
    "T1057",
    "T1058",
    "T1064",
    "T1065s1",
    "T1065s2",
    "T1067",
    "T1070",
    "T1073",
    "T1074",
    "T1076",
    "T1078",
    "T1079",
    "T1080",
    "T1082",
    "T1089",
    "T1090",
    "T1091",
    "T1099",
]


class CASP14(Dataset):
    """The CASP14 Protein Dataset."""

    def __init__(
        self,
        cache_dir: str,
        subset: str = "esmfold",
        msas: str = MSA_URL,
    ) -> None:
        """Initialize the dataset.

        Parameters
        ----------
        cache_dir : str
            The directory to store the dataset.
        subset : str
            The subset of the dataset to use.
            One of "all", "colabfold", "esmfold".
        msas : str
            Precomputed MSAs to use.

        """
        if subset not in ["all", "colabfold", "esmfold"]:
            msg = f"Invalid subset: {subset}"
            raise ValueError(msg)

        self._subset = subset
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
        name = "CASP14"
        if self._subset != "all":
            name += f"_{self._subset}"
        return name

    def download(self, cache_dir: str) -> None:
        """Download the dataset.

        Parameters
        ----------
        cache_dir : str
            The directory to store the dataset.

        """
        # Set data dir
        dir_name = "casp14"
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
        pdb_file = data_dir / "casp14_targets.tgz"
        urllib.request.urlretrieve(PDBS_URL, pdb_file)

        # Extract targets
        extract_folder = data_dir / "pdb"
        Path.mkdir(extract_folder, parents=True, exist_ok=True)
        tar = tarfile.open(pdb_file)
        tar.extractall(path=extract_folder)
        tar.close()

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
        data_dir = Path(cache_dir) / "casp14"

        # Pick subset
        if self._subset == "all":
            metadata = pd.read_csv(data_dir / "list.csv", sep=";")
            metadata = metadata[metadata["Target"].str.startswith("T")]
            metadata = metadata[metadata["Cancellation Date"] == "-"]
            targets = list(metadata["Target"])
        elif self._subset == "colabfold":
            targets = CASP14_COLABFOLD_PAPER
        elif self._subset == "esmfold":
            targets = CASP14_ESMFOLD_PAPER
        else:
            msg = f"Invalid subset: {self._subset}"
            raise ValueError(msg)

        # Read sequences
        with Path.open(data_dir / "seqs.fasta") as f:
            seqs = SeqIO.parse(f, "fasta")
            seqs = {seq.id: str(seq.seq) for seq in seqs}

        # Load targets
        proteins = []
        for name in targets:
            pdb_path = data_dir / "pdb" / f"{name}.pdb"
            if not Path.exists(pdb_path):
                msg = f"File {pdb_path} does not exist"
                raise FileNotFoundError(msg)

            # Get msa path
            msa = data_dir / "a3m" / f"{name}.a3m"

            protein = Target(
                name=name,
                path=pdb_path,
                chain=None,
                sequence=seqs[name],
                msa=msa,
            )
            proteins.append(protein)

        return proteins
