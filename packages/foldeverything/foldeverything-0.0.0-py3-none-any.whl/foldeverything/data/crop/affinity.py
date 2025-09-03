
from dataclasses import replace
from typing import List, Optional, Set

import numpy as np
from scipy.spatial.distance import cdist

from foldeverything.data import const
from foldeverything.data.crop.cropper import Cropper
from foldeverything.data.data import Tokenized


class AffinityCropper(Cropper):
    """Interpolate between contiguous and spatial crops."""

    def __init__(
        self,
        neighborhood_sizes: List[int],
        max_dist: Optional[int] = None,
        max_tokens_protein: int = 100000,
    ) -> None:
        """Initialize the cropper.

        Parameters
        ----------
        neighborhood_sizes : List[int]
            Modulates the type of cropping to be performed.
            Smaller neighborhoods result in more spatial
            cropping. Larger neighborhoods result in more
            continuous cropping. A mix can be achieved by
            providing a list of sizes from which to sample.

        """
        self.neighborhood_sizes = neighborhood_sizes
        self.max_dist = max_dist
        self.max_tokens_protein = max_tokens_protein

    def crop(  # noqa: PLR0915
        self,
        data: Tokenized,
        max_tokens: int,
        random: np.random.RandomState,
        max_atoms: Optional[int] = None,
        return_indices: bool = False,
    ) -> Tokenized:
        """Crop the data to a maximum number of tokens.

        Parameters
        ----------
        data : Tokenized
            The tokenized data.
        max_tokens : int
            The maximum number of tokens to crop.
        random : np.random.RandomState
            The random state for reproducibility.
        max_atoms : Optional[int]
            The maximum number of atoms to consider.

        Returns
        -------
        Tokenized
            The cropped data.

        """
        # Randomly select a neighborhood size
        neighborhood_size = random.choice(self.neighborhood_sizes)

        # Get token data
        token_data = data.tokens
        token_bonds = data.bonds

        # Filter to resolved tokens
        valid_tokens = token_data[token_data["resolved_mask"]]

        # Check if we have any valid tokens
        if not valid_tokens.size:
            msg = "No valid tokens in structure"
            raise ValueError(msg)

        # Sort all tokens by distance to query_coords
        dists = valid_tokens["min_dist_ligand"]
        indices = np.argsort(dists)

        # Select cropped indices
        cropped: Set[int] = set()
        total_atoms = 0

        # protein tokens
        cropped_protein: Set[int] = set()
        ligand_ids = set(valid_tokens[valid_tokens["mol_type"] == 3]["token_idx"])

        for idx in indices:
            # Stop if we exceed the max distance
            if self.max_dist is not None and dists[idx] > self.max_dist:
                break

            # Get the token
            token = valid_tokens[idx]

            # Get all tokens from this chain
            chain_tokens = token_data[token_data["asym_id"] == token["asym_id"]]

            # Pick the whole chain if possible, otherwise select
            # a contiguous subset centered at the query token
            if len(chain_tokens) <= neighborhood_size:
                new_tokens = chain_tokens
            else:
                # First limit to the maximum set of tokens, with the
                # neighboorhood on both sides to handle edges. This
                # is mostly for efficiency with the while loop below.
                min_idx = token["res_idx"] - neighborhood_size
                max_idx = token["res_idx"] + neighborhood_size

                max_token_set = chain_tokens
                max_token_set = max_token_set[max_token_set["res_idx"] >= min_idx]
                max_token_set = max_token_set[max_token_set["res_idx"] <= max_idx]

                # Start by adding just the query token
                new_tokens = max_token_set[max_token_set["res_idx"] == token["res_idx"]]

                # Expand the neighborhood until we have enough tokens, one
                # by one to handle some edge cases with non-standard chains.
                # We switch to the res_idx instead of the token_idx to always
                # include all tokens from modified residues or from ligands.
                min_idx = max_idx = token["res_idx"]
                while new_tokens.size < neighborhood_size:
                    min_idx = min_idx - 1
                    max_idx = max_idx + 1
                    new_tokens = max_token_set
                    new_tokens = new_tokens[new_tokens["res_idx"] >= min_idx]
                    new_tokens = new_tokens[new_tokens["res_idx"] <= max_idx]

            # Compute new tokens and new atoms
            new_indices = set(new_tokens["token_idx"]) - cropped
            new_tokens = token_data[list(new_indices)]
            new_atoms = np.sum(new_tokens["atom_num"])

            # Stop if we exceed the max number of tokens or atoms
            if (
                (len(new_indices) > (max_tokens - len(cropped)))
                or ((max_atoms is not None) and ((total_atoms + new_atoms) > max_atoms))
                or (
                    len(cropped_protein | new_indices - ligand_ids)
                    > self.max_tokens_protein
                )
            ):
                break

            # Add new indices
            cropped.update(new_indices)
            total_atoms += new_atoms

            # Add protein indices
            cropped_protein.update(new_indices - ligand_ids)

        # Get the cropped tokens sorted by index
        token_data = token_data[sorted(cropped)]

        # Only keep bonds within the cropped tokens
        indices = token_data["token_idx"]
        token_bonds = token_bonds[np.isin(token_bonds["token_1"], indices)]
        token_bonds = token_bonds[np.isin(token_bonds["token_2"], indices)]

        # Return the cropped tokens
        if return_indices:
            return replace(data, tokens=token_data, bonds=token_bonds), sorted(cropped)
        else:
            return replace(data, tokens=token_data, bonds=token_bonds)

    def crop_with_indices(self, data, cropped) -> Tokenized:  # noqa: PLR0915
        """Crop the data to a maximum number of tokens.

        Parameters
        ----------
        data : Tokenized
            The tokenized data.
        indices : List[int]
            The indices of the crop.

        Returns
        -------
        Tokenized
            The cropped data.

        """
        # Get token data
        token_data = data.tokens
        token_bonds = data.bonds

        # Get the cropped tokens sorted by index
        token_data = token_data[cropped]

        # Only keep bonds within the cropped tokens
        indices = token_data["token_idx"]
        token_bonds = token_bonds[np.isin(token_bonds["token_1"], indices)]
        token_bonds = token_bonds[np.isin(token_bonds["token_2"], indices)]

        return replace(data, tokens=token_data, bonds=token_bonds)
