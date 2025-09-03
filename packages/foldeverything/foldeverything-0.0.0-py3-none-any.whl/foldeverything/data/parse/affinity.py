from dataclasses import dataclass
import re
from typing import Dict, List, Optional, Tuple

import numpy as np
from rdkit.Chem import AllChem
from rdkit.Chem.rdchem import Conformer, Mol

from foldeverything.data import const
from foldeverything.data.conformers_smile_new import get_conformer
from foldeverything.data.const import prot_letter_to_token
from foldeverything.data.data import (
    Atom,
    Bond,
    Chain,
    Coords,
    Ensemble,
    Interface,
    Residue,
    Structure,
    StructureInfo,
)
from foldeverything.data.parse.mmcif import get_mol
from foldeverything.task.process.process import Resource

####################################################################################################
# DATACLASSES
####################################################################################################


@dataclass(frozen=True, slots=True)
class ParsedAtom:
    """A parsed atom object."""

    name: str
    coords: Tuple[float, float, float]
    is_present: bool
    bfactor: float
    plddt: Optional[float] = None


@dataclass(frozen=True, slots=True)
class ParsedBond:
    """A parsed bond object."""

    chain_1: str
    chain_2: str
    residue_index_1: int
    residue_index_2: int
    atom_index_1: str
    atom_index_2: str
    type: int


@dataclass(frozen=True, slots=True)
class ParsedResidue:
    """A parsed residue object."""

    name: str
    type: int
    idx: int
    atoms: List[Atom]
    bonds: List[Bond]
    orig_idx: Optional[int]
    atom_center: int
    atom_disto: int
    is_standard: bool
    is_present: bool


@dataclass(frozen=True, slots=True)
class ParsedChain:
    """A parsed chain object."""

    name: str
    entity: str
    type: int
    residues: List[ParsedResidue]
    sequence: Optional[str] = None


@dataclass(frozen=True, slots=True)
class ParsedConnection:
    """A parsed connection object."""

    chain_1: str
    chain_2: str
    residue_index_1: int
    residue_index_2: int
    atom_index_1: str
    atom_index_2: str


@dataclass(frozen=True, slots=True)
class ParsedStructure:
    """A parsed structure object."""

    data: Structure
    info: StructureInfo
    sequences: Dict[str, str]


####################################################################################################
# HELPERS
####################################################################################################


def convert_sequence_to_list(sequence):
    # Define the regular expression to match single uppercase letters and alphanumerical codes in {}, without capturing the braces
    matches = re.findall(r"[A-Z]|\{([A-Za-z0-9]{3})\}", sequence)
    # Flatten the result, replacing None with the matched letter
    parsed_sequence = [
        match if match else letter
        for letter, match in re.findall(r"([A-Z])|\{([A-Za-z0-9]{3})\}", sequence)
    ]
    return parsed_sequence


def parse_smiles_sequences(
    sequences: List[str], mols: List[Mol], moldir: str
) -> ParsedStructure:
    # TODO: change the code to be able to handle multimer with same chain i.e. sequences: List[Tuple[str, int]]
    # TODO: change the code to be able to handle multi-ligands chain i.e. glycans
    """Parse a structure in MMCIF format.

    Parameters
    ----------
    smiles : List[str]
        List of smiles.
    sequences: List[str]
        List of sequences.
    mols: List[Mol]
        The preprocessed rdkit Mol list.
    Returns
    -------
    ParsedStructure
        The parsed structure.

    """
    moldict = {}

    chains = []
    count_chains = 0
    # Add polymers to the chain
    for sequence in sequences:
        parsed_polymer = parse_sequence(sequence=sequence,moldict=moldict,moldir=moldir,chain_id=str(count_chains),entity=str(count_chains),)
        chains.append(parsed_polymer)
        count_chains += 1
    for mol in mols:
        parsed_polymer = parse_smile(
            name="LIG",
            mol=mol,
            res_idx=0,
            chain_id=str(count_chains),
            entity=str(count_chains),
        )
        chains.append(parsed_polymer)
        count_chains += 1

    # Create tables
    atom_data = []
    atom_affinity_data = []
    bond_data = []
    res_data = []
    chain_data = []
    coords_data = []

    # Convert parsed chains to tables
    atom_idx = 0
    res_idx = 0
    asym_id = 0
    sym_id = 0

    chain_to_seq = {}

    for chain_idx, chain in enumerate(chains):
        # Compute number of atoms and residues
        res_num = len(chain.residues)
        atom_num = sum(len(res.atoms) for res in chain.residues)
        chain_data.append(
            (
                chain.name,
                chain.type,
                chain.entity,
                sym_id,
                asym_id,
                atom_idx,
                atom_num,
                res_idx,
                res_num,
                0
            )
        )

        if chain.sequence is not None:
            chain_to_seq[chain.name] = chain.sequence

        # Add residue, atom, bond, data
        for i, res in enumerate(chain.residues):
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
                atom_data.append(
                    (
                        atom.name,
                        atom.coords,
                        atom.is_present,
                        atom.bfactor,
                        0.0,
                    )
                )
                coords_data.append((atom.coords,))
                atom_idx += 1
            res_idx += 1
        asym_id += 1

    ensemble_data = [(0, atom_idx)]

    # Return parsed structure
    info = StructureInfo(
        deposited=-1,
        revised=-1,
        released=-1,
        num_chains=len(chains),
        num_interfaces=0,
    )

    data = Structure(
        atoms=np.array(atom_data, dtype=Atom),
        bonds=np.array(bond_data, dtype=Bond),
        residues=np.array(res_data, dtype=Residue),
        chains=np.array(chain_data, dtype=Chain),
        interfaces=np.empty(0, dtype=Interface),
        mask=np.ones(len(chain_data), dtype=bool),
        coords=np.array(coords_data, dtype=Coords),
        ensemble=np.array(ensemble_data, dtype=Ensemble),
    )
    return ParsedStructure(data=data, info=info, sequences=chain_to_seq)


def parse_sequence(
    sequence: str,
    moldict: dict[str, Mol],
    moldir: str,
    chain_id: str,
    entity: str,
) -> Optional[ParsedChain]:
    """Parse a sequence into a list of integers.

    Parameters
    ----------
    sequence : str
        The sequence string.

    Returns
    -------
    List[int]
        The parsed sequence.

    """
    parsed = []
    sequence = convert_sequence_to_list(sequence)
    ref_res = set(const.tokens)

    for res_idx, aa in enumerate(sequence):
        # Load regular residues
        if len(aa) == 1 and prot_letter_to_token[aa] in ref_res:
            res_name = prot_letter_to_token[aa]
            ref_mol = get_mol(res_name, moldict, moldir)
            ref_mol = AllChem.RemoveHs(ref_mol, sanitize=False)

            # Only use reference atoms set in constants
            ref_name_to_atom = {a.GetProp("name"): a for a in ref_mol.GetAtoms()}
            ref_atoms = [ref_name_to_atom[a] for a in const.ref_atoms[res_name]]

            # Iterate, always in the same order
            atoms: List[Atom] = []

            for i, ref_atom in enumerate(ref_atoms):
                # Get atom name
                name = ref_atom.GetProp("name")

                # Get coordinated from PDB
                atom_is_present = True
                coords = (0, 0, 0)

                # Add atom to list
                atoms.append(
                    ParsedAtom(
                        name=name,
                        coords=coords,
                        is_present=atom_is_present,
                        bfactor=0,
                        plddt=0,
                    )
                )

            atom_center = const.res_to_center_atom_id[res_name]
            atom_disto = const.res_to_disto_atom_id[res_name]

            # Load bonds
            bonds = []
            unk_bond = const.bond_types.index(const.unk_bond_type)
            for bond in ref_mol.GetBonds():
                idx_1 = bond.GetBeginAtomIdx()
                idx_2 = bond.GetEndAtomIdx()

                start = min(idx_1, idx_2)
                end = max(idx_1, idx_2)
                bond_type = bond.GetBondType().name
                bond_type = (
                    const.bond_types.index(bond_type)
                    if bond_type in const.bond_types
                    else unk_bond
                )
                bonds.append(
                    ParsedBond(chain_id, chain_id, res_idx, res_idx, start, end, bond_type)
                )

            parsed.append(
                ParsedResidue(
                    name=res_name,
                    atoms=atoms,
                    bonds=[],
                    idx=res_idx,
                    is_standard=True,
                    is_present=True,
                    atom_center=atom_center,
                    atom_disto=atom_disto,
                    orig_idx=res_idx,
                    type=const.token_ids[res_name],
                )
            )
        else:
            # Try to parse as a ligand
            res_name = prot_letter_to_token[aa]
            residue_chain = parse_smile(
                name=res_name,
                mol=get_mol(res_name, moldict, moldir),
                res_idx=res_idx,
                chain_id=chain_id,
                entity=entity,
            )
            assert len(residue_chain.residues) == 1, "Only one residue should be parsed"
            residue = residue_chain.residues[0]

            # If failed, just set as unknown
            if residue is None:
                residue = ParsedResidue(
                    name=res_name,
                    type=const.unk_token_ids["PROTEIN"],
                    atoms=[],
                    bonds=[],
                    is_standard=False,
                    is_present=False,
                    atom_center=0,
                    atom_disto=0,
                    idx=res_idx,
                    orig_idx=None,
                )

            parsed.append(residue)

    return ParsedChain(
        name=chain_id,
        entity=entity,
        residues=parsed,
        type=const.chain_types.index("PROTEIN"),
        sequence=sequence,
    )


def parse_smile(
    name: str,
    mol: Mol,
    res_idx: int,
    chain_id: str,
    entity: str,
) -> Optional[ParsedResidue]:
    """Parse an MMCIF ligand.

    First tries to get the SMILES string from the RCSB.
    Then, tries to infer atom ordering using RDKit.

    Parameters
    ----------
    name: str
        The name of the molecule to parse.
    mol : Mol
        rdkit Mol.
    res_idx : int
        The residue index.

    Returns
    -------
    ParsedResidue, optional
       The output ParsedResidue, if successful.

    """
    residues = []
    is_present = True
    orig_idx = 0
    # Remove hydrogens
    ref_mol = AllChem.RemoveHs(mol, sanitize=False)
    if ref_mol is None:
        return None

    # Check if this is a single atom CCD residue
    if ref_mol.GetNumAtoms() == 1:
        pos = (0, 0, 0)
        if is_present:
            pos = (0, 0, 0)
        ref_atom = ref_mol.GetAtoms()[0]
        atom = ParsedAtom(
            name=name,
            coords=pos,
            is_present=is_present,
            plddt=0,
            bfactor=0,
        )
        residue = ParsedResidue(
            name=name,
            atoms=[atom],
            bonds=[],
            idx=res_idx,
            orig_idx=orig_idx,
            is_standard=False,
            is_present=is_present,
            type=const.unk_token_ids["PROTEIN"],
            atom_center=0,
            atom_disto=0,
        )
        residues.append(residue)
    else:
        # Parse each atom in order of the reference mol
        atoms = []
        atom_idx = 0
        idx_map = {}  # Used for bonds later

        for i, atom in enumerate(ref_mol.GetAtoms()):
            # Get atom name, charge, element and reference coordinates
            atom_name = atom.GetProp("name")

            # Get PDB coordinates, if any
            coords = (0, 0, 0)
            atom_is_present = True

            # Add atom to list
            atoms.append(
                ParsedAtom(
                    name=atom_name,
                    coords=coords,
                    is_present=atom_is_present,
                    bfactor=0.0,
                )
            )
            idx_map[i] = atom_idx
            atom_idx += 1

        # Load bonds
        bonds = []
        unk_bond = const.bond_types.index(const.unk_bond_type)
        for bond in ref_mol.GetBonds():
            idx_1 = bond.GetBeginAtomIdx()
            idx_2 = bond.GetEndAtomIdx()

            if (idx_1 not in idx_map) or (idx_2 not in idx_map):
                continue

            idx_1 = idx_map[idx_1]
            idx_2 = idx_map[idx_2]
            start = min(idx_1, idx_2)
            end = max(idx_1, idx_2)
            bond_type = bond.GetBondType().name
            bond_type = (
                const.bond_types.index(bond_type)
                if bond_type in const.bond_types
                else unk_bond
            )
            bonds.append(ParsedBond(start, end, bond_type))

        residue = ParsedResidue(
            name=name,
            atoms=atoms,
            bonds=bonds,
            idx=res_idx,
            orig_idx=orig_idx,
            is_standard=False,
            is_present=is_present,
            type=const.unk_token_ids["PROTEIN"],
            atom_center=0,
            atom_disto=0,
        )
        residues.append(residue)

    return ParsedChain(
        name=chain_id,
        entity=entity,
        residues=residues,
        type=const.chain_types.index("NONPOLYMER"),
    )
