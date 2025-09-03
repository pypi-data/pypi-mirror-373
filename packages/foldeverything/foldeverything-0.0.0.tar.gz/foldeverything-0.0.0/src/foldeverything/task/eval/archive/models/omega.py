import os
import subprocess
from os import PathLike
from pathlib import Path
from typing import List

from foldeverything.eval.data.dataset import Dataset
from foldeverything.eval.models.model import Model
from foldeverything.eval.protein import Prediction


class Omegafold(Model):
    """Run the Omegafold v2 model on a dataset."""

    def __init__(self, weights_path: os.PathLike) -> None:
        """Initialize the model.

        Parameters
        ----------
        weights_path : PathLike
            Path to the model checkpoint.

        """
        self.weights_path = weights_path

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
            # Dump fasta file
            fasta = Path(outdir) / "input.fasta"
            with Path.open(fasta, "w") as f:
                f.write(dataset.fasta)

            # Run model
            weights_path = Path(self.weights_path)
            subprocess.run(
                [
                    "omegafold",
                    fasta,
                    pdb,
                    "--weights_file",
                    weights_path,
                    "--model",
                    "1",
                    "--subbatch_size",
                    "448",
                ]
            )
        else:
            print(f"Directory {pdb} already exists. Skipping prediction.")

        # Read predictions
        predictions = []
        for target in dataset:
            pdb_file = pdb / f"{target.name}.pdb"
            predictions.append(
                Prediction(
                    name=target.name,
                    sequence=target.sequence,
                    chain="A",
                    path=pdb_file,
                )
            )

        return predictions
