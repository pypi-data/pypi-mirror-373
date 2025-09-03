from abc import ABC, abstractmethod
from typing import Dict, Optional

from torch import Tensor

from foldeverything.data.data import Input


class Featurizer(ABC):
    """Featurizer for model training."""

    @abstractmethod
    def process(
        self,
        data: Input,
        max_seqs: int,
        pad_to_max_seqs: bool,
        training: bool,
        symmetries: Dict,
        max_tokens: Optional[int] = None,
        max_atoms: Optional[int] = None,
        compute_symmetries: Optional[bool] = False,
        binder_pocket_conditioned_prop: Optional[float] = 0.0,
        contact_conditioned_prop: Optional[float] = 0.0,
        binder_pocket_cutoff_min: Optional[float] = 4.0,
        binder_pocket_cutoff_max: Optional[float] = 20.0,
        binder_pocket_sampling_geometric_p: Optional[float] = 0.0,
        only_ligand_binder_pocket: Optional[bool] = False,
        only_pp_contact: Optional[bool] = False,
        maximum_bond_distance: Optional[int] = 0,
    ) -> Dict[str, Tensor]:
        """Compute features.

        Parameters
        ----------
        data : Input
            The input data to the model.
        max_tokens : int
            The maximum number of tokens.
        max_atoms : int
            The maximum number of atoms
        training : bool
            Whether the model is in training mode.

        Returns
        -------
        Dict[str, Tensor]
            The features for model training.

        """
        raise NotImplementedError
