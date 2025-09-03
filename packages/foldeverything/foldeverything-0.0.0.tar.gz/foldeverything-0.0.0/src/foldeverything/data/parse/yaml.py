from pathlib import Path
from typing import Dict, List, Optional

import gemmi
import numpy as np
import yaml
from rdkit import rdBase
from rdkit.Chem import AllChem
from rdkit.Chem.rdchem import Mol

from foldeverything.data import const
from foldeverything.data.data import (
    Atom,
    Bond,
    Chain,
    Coords,
    Ensemble,
    Interface,
    Residue,
    Structure,
)
from foldeverything.data.parse.mmcif import (
    ParsedAtom,
    ParsedChain,
    ParsedResidue,
    get_mol,
    parse_ccd_residue,
)


def parse_polymer(
    polymer_type: gemmi.PolymerType,
    sequence: List[str],
    chain_id: str,
    entity: str,
    mols: Dict[str, Mol],
    moldir: str,
) -> Optional[ParsedChain]:
    """Process a gemmi Polymer into a chain object.

    Performs alignment of the full sequence to the polymer
    residues. Loads coordinates and masks for the atoms in
    the polymer, following the ordering in const.atom_order.

    Parameters
    ----------
    polymer_type : gemmi.PolymerType
        The polymer type.
    sequence : str
        The full sequence of the polymer.
    chain_id : str
        The chain identifier.
    entity : str
        The entity name.
    components : Dict[str, Mol]
        The preprocessed PDB components dictionary.

    Returns
    -------
    ParsedChain, optional
        The output chain, if successful.

    Raises
    ------
    ValueError
        If the alignment fails.

    """
    # Get polymer class
    if polymer_type == gemmi.PolymerType.PeptideL:
        chain_type = const.chain_type_ids["PROTEIN"]
        residue_kind = gemmi.ResidueKind.AA
    elif polymer_type == gemmi.PolymerType.Dna:
        chain_type = const.chain_type_ids["DNA"]
        residue_kind = gemmi.ResidueKind.DNA
    elif polymer_type == gemmi.PolymerType.Rna:
        chain_type = const.chain_type_ids["RNA"]
        residue_kind = gemmi.ResidueKind.RNA

    # Get full sequence
    full_sequence = gemmi.expand_one_letter_sequence(sequence, residue_kind)

    # Get coordinates and masks
    ref_res = set(const.tokens)
    parsed = []
    for i, res_name in enumerate(full_sequence):
        # Map MSE to MET
        if res_name == "MSE":
            res_name = "MET"  # noqa: PLW2901

        # Handle non-standard residues
        elif res_name not in ref_res:
            modified_mol = get_mol(res_name, mols, moldir)
            if modified_mol is not None:
                residue = parse_ccd_residue(
                    name=res_name,
                    ref_mol=modified_mol,
                    res_idx=i,
                    gemmi_mol=None,
                    is_covalent=True,
                )
                parsed.append(residue)
                continue
            else:  # noqa: RET507
                res_name = "UNK"

        # Load regular residues
        ref_mol = get_mol(res_name, mols, moldir)
        ref_mol = AllChem.RemoveHs(ref_mol, sanitize=False)

        # Only use reference atoms set in constants
        ref_name_to_atom = {a.GetProp("name"): a for a in ref_mol.GetAtoms()}
        ref_atoms = [ref_name_to_atom[a] for a in const.ref_atoms[res_name]]

        # Iterate, always in the same order
        atoms: List[ParsedAtom] = []

        for ref_atom in ref_atoms:
            # Get atom name
            atom_name = ref_atom.GetProp("name")

            # Get coordinated from PDB
            atom_is_present = False
            coords = (0, 0, 0)
            bfactor = 0

            # Add atom to list
            atoms.append(
                ParsedAtom(
                    name=atom_name,
                    coords=coords,
                    is_present=atom_is_present,
                    bfactor=bfactor,
                )
            )
        atom_center = const.res_to_center_atom_id[res_name]
        atom_disto = const.res_to_disto_atom_id[res_name]
        parsed.append(
            ParsedResidue(
                name=res_name,
                type=const.token_ids[res_name],
                atoms=atoms,
                bonds=[],
                idx=i,
                atom_center=atom_center,
                atom_disto=atom_disto,
                is_standard=True,
                is_present=False,
                orig_idx=None,
            )
        )

    # Return polymer object
    return ParsedChain(
        name=chain_id,
        entity=entity,
        residues=parsed,
        type=chain_type,
        sequence=sequence,
    )


def parse_yaml(
    data: Dict,
    mols: Optional[Dict[str, Mol]] = None,
    moldir: Optional[str] = None,
) -> Structure:
    """Parse a fasta file.

    Parameters
    ----------
    data : Dict
        The yaml data.
    mols : Dict[str, Mol]
        A set of preloaded molecules, if any.
    moldir : str
        The directory to load molecules from.

    Returns
    -------
    Structure
        The parsed structure.

    """
    # Disable rdkit warnings
    blocker = rdBase.BlockLogs()  # noqa: F841

    # Parse chains
    chains: List[ParsedChain] = []
    chain_id_to_entity: Dict[int, str] = {}
    for entity_id, entity in enumerate(data["sequences"]):
        # Skip non-protein entities for now
        if "protein" not in entity:
            raise NotImplementedError

        ids = entity["protein"]["id"]
        if isinstance(ids, str):
            ids = [ids]

        for chain_id in ids:
            parsed_polymer = parse_polymer(
                polymer_type=gemmi.PolymerType.PeptideL,
                sequence=entity["protein"]["sequence"],
                chain_id=chain_id,
                entity=entity_id,
                mols=mols,
                moldir=moldir,
            )
            chains.append(parsed_polymer)
            chain_id_to_entity[chain_id] = entity_id

    # If no chains parsed fail
    if not chains:
        msg = "No chains parsed!"
        raise ValueError(msg)

    # Create tables
    atom_data = []
    bond_data = []
    res_data = []
    chain_data = []
    coords_data = []

    # Convert parsed chains to tables
    atom_idx = 0
    res_idx = 0
    asym_id = 0
    sym_count = {}
    chain_to_idx = {}

    for asym_id, chain in enumerate(chains):
        # Compute number of atoms and residues
        res_num = len(chain.residues)
        atom_num = sum(len(res.atoms) for res in chain.residues)

        # Find all copies of this chain in the assembly
        entity_id = chain_id_to_entity[chain.name]
        sym_id = sym_count.get(entity_id, 0)
        chain_data.append(
            (
                chain.name,
                chain.type,
                entity_id,
                sym_id,
                asym_id,
                atom_idx,
                atom_num,
                res_idx,
                res_num,
                0,  # cyclic_period
            )
        )

        chain_to_idx[chain.name] = asym_id
        sym_count[entity_id] = sym_id + 1

        # Add residue, atom, bond, data
        for res in chain.residues:
            atom_center = atom_idx + res.atom_center
            atom_disto = atom_idx + res.atom_disto
            res_data.append(
                (
                    res.name,
                    res.type,
                    res.idx,
                    atom_idx,
                    len(res.atoms),
                    atom_center,
                    atom_disto,
                    res.is_standard,
                    res.is_present,
                )
            )

            for bond in res.bonds:
                chain_1 = asym_id
                chain_2 = asym_id
                res_1 = res_idx
                res_2 = res_idx
                atom_1 = atom_idx + bond.atom_1
                atom_2 = atom_idx + bond.atom_2
                bond_data.append(
                    (
                        chain_1,
                        chain_2,
                        res_1,
                        res_2,
                        atom_1,
                        atom_2,
                        bond.type,
                    )
                )

            for atom in res.atoms:
                coords_data.append((atom.coords,))
                atom_data.append(
                    (
                        atom.name,
                        atom.coords,
                        atom.is_present,
                        0.0,
                        0.0,
                    )
                )
                atom_idx += 1

            res_idx += 1

    # Convert into datatypes
    atoms = np.array(atom_data, dtype=Atom)
    bonds = np.array(bond_data, dtype=Bond)
    residues = np.array(res_data, dtype=Residue)
    chains = np.array(chain_data, dtype=Chain)
    interfaces = np.array([], dtype=Interface)
    mask = np.ones(len(chain_data), dtype=bool)
    coords = np.array(coords_data, dtype=Coords)
    ensemble = np.array([(0, len(coords_data))], dtype=Ensemble)

    data = Structure(
        atoms=atoms,
        bonds=bonds,
        residues=residues,
        chains=chains,
        interfaces=interfaces,
        mask=mask,
        coords=coords,
        ensemble=ensemble,
    )

    return data
