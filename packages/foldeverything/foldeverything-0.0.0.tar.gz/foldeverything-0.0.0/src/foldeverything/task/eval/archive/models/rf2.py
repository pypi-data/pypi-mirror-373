import os
import sys
from os import PathLike
from pathlib import Path
from typing import List

import torch

from foldeverything.eval.data.dataset import Dataset
from foldeverything.eval.models.model import Model
from foldeverything.eval.protein import Prediction


class RosettaFold2(Model):
    """Run the RosettaFold2 model on a dataset."""

    def __init__(self, code_path: os.PathLike, weights_path: os.PathLike) -> None:
        """Initialize the model.

        Parameters
        ----------
        code_path: PathLike
            Path to the RosettaFold2 code.
        weights_path : PathLike
            Path to the model checkpoint.

        """
        self.code_path = code_path
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

        # Load model
        sys.path.append(Path(self.code_path) / "network")
        from predict import Predictor

        pred = Predictor(self.weights_path, torch.device("cuda"))

        # Read predictions
        for target in dataset:
            # Skip if prediction already exists
            pdb_file = pdb / f"{target.name}_00_pred.pdb"
            if Path.exists(pdb_file):
                print(f"Prediction for {target.name} already exists, skipping.")
                continue

            try:
                pred.predict(
                    inputs=[target.msa],
                    out_prefix=pdb / f"{target.name}",
                    symm="C1",
                    n_recycles=3,
                    n_models=1,
                    subcrop=-1,
                    nseqs=256,
                    nseqs_full=2048,
                    ffdb=None,
                )
            except Exception as e:  # noqa: BLE001
                print(f"Failed to predict {target.name}: {e}")
                continue

        # Return predictions
        predictions = []
        for target in dataset:
            pdb_file = pdb / f"{target.name}_00_pred.pdb"
            predictions.append(
                Prediction(
                    name=target.name,
                    sequence=target.sequence,
                    chain="A",
                    path=pdb_file,
                )
            )

        return predictions
