from dataclasses import replace
from typing import Optional

import numpy as np

from foldeverything.data import const
from foldeverything.data.crop.cropper import Cropper
from foldeverything.data.data import Tokenized


class MonomerCropper(Cropper):
    """Cropping protein monomers contiguously."""

    def crop(
        self,
        data: Tokenized,
        max_tokens: int,
        random: np.random.Generator,
        max_atoms: Optional[int] = None,  # noqa: ARG002
        chain_id: Optional[int] = None,
        interface_id: Optional[int] = None,
    ) -> Tokenized:
        """Crop the data to a maximum number of tokens.

        TODO add maximum number of atoms consideration

        Parameters
        ----------
        data : Tokenized
            The tokenized data.
        max_tokens : int
            The maximum number of tokens to crop.
        random : np.random.Generator
            The random state for reproducibility.
        max_atoms : Optional[int]
            The maximum number of atoms to consider.

        Returns
        -------
        Tokenized
            The cropped data.

        """
        # Check if interface was passed in
        if interface_id is not None:
            msg = "Monomer cropping does not support interfaces."
            raise ValueError(msg)

        # Get the token data
        token_data = data.tokens
        token_bonds = data.bonds

        # Pick a protein chain
        mask = data.structure.mask
        chains = data.structure.chains

        if chain_id is not None:
            chain = chains[chain_id]
        else:
            chains = chains[mask]
            prot_id = const.chain_type_ids["PROTEIN"]
            prot_chains = chains[chains["mol_type"] == prot_id]
            chain = prot_chains[random.choice(len(chains))]

        # Select relevant tokens, noting that the
        # selection is naturally contiguous here.
        chain_tokens = token_data["asym_id"] == chain["asym_id"]
        token_data = token_data[chain_tokens]

        # Crop the tokens if needed
        if len(token_data) > max_tokens:
            # Make sure we don't crop on an unknown token
            unk_idx = const.token_ids[const.unk_token["PROTEIN"]]
            valid = np.argwhere(token_data["res_type"] != unk_idx)

            # Favor low-indices, if any
            valid_b = valid[(valid + max_tokens) < len(token_data)]
            idx = random.choice(valid_b) if valid_b.size else random.choice(valid)
            token_data = token_data[idx : idx + max_tokens]

        # Only keep bonds within the cropped tokens
        indices = token_data["token_index"]
        token_bonds = token_bonds[np.isin(token_bonds["token_1"], indices)]
        token_bonds = token_bonds[np.isin(token_bonds["token_2"], indices)]

        # Return the cropped tokens
        return replace(data, tokens=token_data, bonds=token_bonds)
