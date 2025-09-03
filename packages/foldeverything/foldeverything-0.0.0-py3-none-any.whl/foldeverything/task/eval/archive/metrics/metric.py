from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple, Union

import numpy as np

from foldeverything.types import Polymer, Protein


def check_valid(polymer: Polymer, atoms: List[str]) -> None:
    """Check if the atoms are valid.

    Parameters
    ----------
    polymer : Protein
        The protein to check.
    atoms : List[str]
        The atoms to check.

    Raises
    ------
    ValueError
        If an atom is invalid.

    """
    atom_set = set(polymer.atom_types())
    invalid = [a for a in atoms if a not in atom_set]
    if invalid:
        msg = f"Invalid atom in atom list: {invalid}"
        raise ValueError(msg)


def select_atoms(polymer: Polymer, atoms: List[str]) -> Polymer:
    """Select atoms from the polymer.

    Parameters
    ----------
    polymer : Polymer
        The polymer from which to select atoms.
    atoms : List[str]
        The atoms to select.

    Returns
    -------
    Polymer
        The polymer with the selected atoms.

    """

    # Select atoms
    atom_mapping = {a: i for i, a in enumerate(polymer.atom_types())}

    _atom_indices = [atom_mapping[a] for a in atoms]
    coords = polymer.coords[:, _atom_indices, :]
    mask = polymer.mask[:, _atom_indices]

    # Return new Polymer
    polymer_type = type(polymer)
    return polymer_type(
        chain=polymer.chain,
        sequence=polymer.sequence,
        indices=polymer.indices,
        coords=coords,
        mask=mask,
    )


def prepare_coords(
    predicted: Polymer, target: Polymer
) -> Tuple[np.ndarray, np.ndarray]:
    """Prepare the coordinates for comparison.

    Flattens the coordinates and masks, ensures that
    the target atoms are present in the prediction,
    and selects the atoms according to the target mask.

    Parameters
    ----------
    predicted : Polymer
        The predicted polymer.
    target : Polymer
        The target polymer.

    Returns
    -------
    np.ndarray
        The prepared coordinates for the prediction.
    np.ndarray
        The prepared coordinates for the target.

    """

    # Flatten
    pred_coords = predicted.coords.reshape(-1, 3)
    target_coords = target.coords.reshape(-1, 3)
    pred_mask = predicted.mask.reshape(-1)
    target_mask = target.mask.reshape(-1)

    # Sometime not every single atom is in the prediction
    # this is a bit strange but usually a very tiny number
    # in the whole dataset, so we just ignore these cases
    common_atoms = pred_mask & target_mask

    # Select the atoms present in the target.
    pred_coords = pred_coords[common_atoms]
    target_coords = target_coords[common_atoms]

    return pred_coords, target_coords


class Metric(ABC):
    """Abstract base class for metrics."""

    valid_modes = {"all_atom", "backbone", "custom"}

    def __init__(self, mode="all_atom", atoms: Optional[List[str]] = None) -> None:
        """Initialize the metric.

        Parameters
        ----------
        mode : str, optional
            The atom-selection mode of the metric. Can be "all_atom", "backbone", or "custom".
        atoms : List[str], optional
            The atoms to use. Only used in "custom" mode.

        """
        self._atoms = None
        self._mode = mode
        assert mode in self.valid_modes, f"Invalid mode: {mode}"
        assert (mode == "custom") == (
            atoms is not None
        ), "Atoms must be set in custom mode, but not others."
        if atoms is not None:
            self._atoms = sorted(atoms)

    @property
    def name(self) -> str:
        """The name of the metric.

        Returns
        -------
        str
            The name of the metric.

        """
        name = self.__class__.__name__
        if self._atoms is not None:
            name += f"_{','.join(self._atoms)}"
        else:
            name += f"_{self._mode}"
        return name

    def preprocess(self, polymer: Polymer) -> Polymer:
        """Preprocess the protein.

        Handles atom selection. Can be overridden for
        metric-specific preprocessing if necessary.

        Parameters
        ----------
        polymer : Polymer
            The polymer to preprocess.

        Returns
        -------
        Polymer
            The preprocessed polymer

        """
        # Select atoms if given
        if self._mode in {"custom"}:
            # Check that custom atoms are valid
            check_valid(polymer, self._atoms)

        # Perform selection
        if self._mode in {"backbone", "custom"}:
            _atoms = self._atoms
            if self._mode == "backbone":
                # TODO Make this a property of the type?
                _atoms = ["CA"] if "CA" in polymer.atom_types() else ["C4'"]
            polymer = select_atoms(polymer, _atoms)

        return polymer

    @abstractmethod
    def compute(self, predicted: Polymer, target: Polymer) -> float:
        """Compute the metric between two sets of coordinates.

        Parameters
        ----------
        predicted : Polymer
            The predicted polymer.
        target : Polymer
            The reference polymer.

        Returns
        -------
        float
            The computed metric.

        """
        raise NotImplementedError

    def __call__(
        self, predicted: Polymer, target: Polymer
    ) -> Union[Dict[str, float], float]:
        """Compute the metric between two polymers.

        Parameters
        ----------
        predicted: Polymer
            The predicted polymer.
        predicted: Polymer
            The reference polymer.

        Returns
        -------
        float
            The computed metric.

        """
        # Preprocess both polymers
        predicted = self.preprocess(predicted)
        target = self.preprocess(target)

        # Compute metric
        return self.compute(predicted, target)
