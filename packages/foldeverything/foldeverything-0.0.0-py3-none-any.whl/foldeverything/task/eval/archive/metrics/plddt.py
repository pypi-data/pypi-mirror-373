from typing import Dict

import scipy

from foldeverything.types import Protein, Polymer
from foldeverything.eval.metrics.lddt import lddt
from foldeverything.eval.metrics.metric import Metric, prepare_coords


class PLDDT(Metric):
    """lDDT metric for protein structure prediction."""

    def compute(self, pred: Protein, target: Protein) -> Dict[str, float]:
        """Compute the lDDT between the predicted and target proteins.

        Parameters
        ----------
        pred : Protein
            The predicted protein.
        target : Protein
            The target protein.

        Returns
        -------
        Dict[str, float]
            pLDDT, and correlation between pLDDT and lDDT.

        """
        pred_coords, target_coords = prepare_coords(pred, target)
        lddt_val = lddt(pred_coords, target_coords, per_residue=True)

        # Flatten
        pred_b_factors = pred.b_factors.reshape(-1, 1)
        pred_mask = pred.mask.reshape(-1)
        target_mask = target.mask.reshape(-1)
        common_atoms = pred_mask & target_mask

        # Select the atoms present in the target.
        plddt = pred_b_factors[common_atoms][:, 0]

        plddt_protein = plddt.mean()

        _, _, r_value, p_value, std_err = scipy.stats.linregress(plddt, lddt_val)

        metrics = {
            "plddt": plddt_protein,
            "R": r_value,
            "P": p_value,
            "std_err": std_err,
        }

        return metrics
