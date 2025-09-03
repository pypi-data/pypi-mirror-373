from abc import ABC, abstractmethod
import csv
import json
import pprint
import subprocess
import os
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
import tempfile

from foldeverything.complex import Complex
from foldeverything.types import RNA
from foldeverything.eval.metrics.metric import Metric, prepare_coords
from foldeverything.eval.utils import write_complex


def write_rna(rna: RNA, path: str):
    """Write RNA structure to PDB file.

    Parameters
    ----------
    rna : RNA
        The RNA structure to write.
    path : str
    """

    # PDB file can only take 1 character for chain
    new_rna = RNA(
        chain=rna.chain[0],
        sequence=rna.sequence,
        indices=rna.indices,
        coords=rna.coords,
        mask=rna.mask,
    )
    new_complex = Complex(
        proteins=[],
        dnas=[],
        rnas=[new_rna],
        ligands=[],
        resolution=0.0,
        deposited="",
        revised="",
    )
    return write_complex(new_complex, path)


class RNA_calc_inf(Metric):
    """
    Calculate INF score using RNA-tools

    """

    def compute(self, predicted: RNA, target: RNA) -> Dict[str, float]:
        """Compute RNA metrics using RNA-tools
        https://github.com/mmagnus/rna-tools


        Parameters
        ----------
        predicted : RNA
            The predicted structure.
        target : RNA
            The target structure.

        Returns
        -------
        Dict[str, float]
            The RNA tool scores between the predicted and target structure.

        """

        # Write structures to PDB
        pred_path = "pred.pdb"
        target_path = "target.pdb"

        # Run RNA tools
        exec_path = "rna_calc_inf.py"
        with tempfile.TemporaryDirectory(delete=True) as temp_dir:
            output_path = os.path.join(temp_dir, "rna_tools_inf.csv")
            command = [
                exec_path,
                "--target_fn",
                target_path,
                pred_path,
                "-o",
                output_path,
            ]

            # Write structures to PDB
            write_rna(predicted, os.path.join(temp_dir, pred_path))
            write_rna(target, os.path.join(temp_dir, target_path))

            process = subprocess.run(
                command, capture_output=True, text=True, cwd=temp_dir
            )
            results = csv.DictReader(open(output_path, "r").readlines())
            results = list(results)[0]
            for key, val in results.items():
                try:
                    results[key] = float(val)
                except ValueError:
                    pass

        return results


class Clashscore(Metric):
    """
    Calculate Clashscore using Phenix

    """

    def compute(self, predicted: RNA, target: RNA) -> Dict[str, float]:
        """Compute Clashscore using Phenix

        Parameters
        ----------
        predicted : RNA
            The predicted structure.
        target : RNA
            The target structure.

        Returns
        -------
        Dict[str, float]
            The clashscore between the predicted and target structure.

        """

        # Write structures to PDB
        pred_path = "pred.pdb"
        target_path = "target.pdb"

        # Run Phenix
        possible_dirs = [
            "/usr/local/phenix-1.21.1-5286",
            os.path.join(os.getenv("HOME"), "phenix-1.21.1-5286"),
            os.path.join(os.getenv("HOME"), "Programs", "phenix-1.21.1-5286"),
            os.getenv("PHENIX", "/usr/local/phenix-1.21.1-5286"),
        ]
        exec_name = "phenix.clashscore"
        exec_path = None
        for _dir in possible_dirs:
            _exec_path = os.path.join(_dir, "build/bin", exec_name)
            if os.path.exists(_exec_path):
                exec_path = _exec_path
                break
        assert exec_path, f"Phenix not found, checked {possible_dirs}. Download at https://phenix-online.org/download"
        with tempfile.TemporaryDirectory(delete=True) as temp_dir:
            output_path = os.path.join(temp_dir, "clashscore_result.json")
            command = [
                exec_path,
                f"model={pred_path}",
                "nuclear=True",
                "keep_hydrogens=True",
                "--json",
            ]

            # Write structures to PDB
            write_rna(predicted, os.path.join(temp_dir, pred_path))

            process = subprocess.run(
                command, capture_output=True, text=True, cwd=temp_dir
            )
            results = json.load(open(output_path, "r"))
            summary_results = results["summary_results"][""]
            results = summary_results

        return results
