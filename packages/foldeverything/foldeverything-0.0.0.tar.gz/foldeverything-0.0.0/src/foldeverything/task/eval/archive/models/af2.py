# Note: we use the ColabFold implementation of AlphaFold2

import os
import shutil
import subprocess
from os import PathLike
from pathlib import Path
from typing import List

from foldeverything.eval.data.dataset import Dataset
from foldeverything.eval.models.model import Model
from foldeverything.eval.protein import Prediction


class AlphaFold2(Model):
    """Run the AlphaFold2 (Openfold) model on a dataset."""

    def __init__(self, code_path: os.PathLike) -> None:
        """Initialize the model.

        Parameters
        ----------
        code_path : PathLike
            Path to the model checkpoint.

        """
        self.code_path = code_path

    def predict(self, dataset: Dataset, outdir: PathLike) -> List[Prediction]:
        """Predict the target structures for the given dataset.

        Parameters
        ----------
        dataset : Dataset
            The dataset to predict on.
        outdir: PathLike
            Path to the predicted structures.

        Returns
        -------
        List[Prediction]
            Predictions in the same order as the dataset.

        """
        # Create output directory
        pdb = Path(outdir) / "pdbs"
        pdb.mkdir(exist_ok=True)

        # Check directory is empty
        if len(os.listdir(pdb)) == 0:
            # Dump fasta files, for openfold
            # one per target. MSA's are passed
            # as a separate directory
            fasta = Path(outdir) / "fasta"
            fasta.mkdir(exist_ok=True)
            for target in dataset:
                fasta_file = fasta / f"{target.name}.fasta"
                with open(fasta_file, "w") as f:
                    f.write(f">{target.name}\n{target.sequence}")

            # Dump a3m files for openfold
            msa = Path(outdir) / "msa"
            msa.mkdir(exist_ok=True)
            for target in dataset:
                msa_folder = msa / target.name
                msa_folder.mkdir(exist_ok=True)
                msa_file = msa_folder / f"{target.name}.a3m"
                shutil.copyfile(target.msa, msa_file)

            # Run model
            code_path = Path(self.code_path)
            model = "finetuning_no_templ_2.pt"
            script = code_path / "run_pretrained_openfold.py"
            weights = code_path / "openfold/resources/openfold_params" / model
            subprocess.run(
                [
                    "python",
                    script,
                    fasta,
                    "./",  # unused templates
                    "--config_preset",
                    "model_3",
                    "--model_device",
                    "cuda",
                    "--use_precomputed_alignments",
                    msa,
                    "--output_dir",
                    pdb,
                    "--openfold_checkpoint_path",
                    weights,
                    "--skip_relaxation",
                    "--long_sequence_inference",
                ]
            )

        else:
            print(f"Directory {pdb} already exists. Skipping prediction.")

        # Read predictions
        predictions = []
        for target in dataset:
            pdb_file = pdb / f"predictions/{target.name}_model_3_unrelaxed.pdb"
            predictions.append(
                Prediction(
                    name=target.name,
                    sequence=target.sequence,
                    chain="A",
                    path=pdb_file,
                )
            )

        return predictions
