from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Tuple

import gemmi
import numpy as np
from Bio import SeqIO
from pdbeccdutils.core.component import ConformerType
from rdkit import rdBase
from rdkit.Chem import AllChem
from rdkit.Chem.rdchem import Conformer, Mol

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
from foldeverything.data.data import convert_atom_name

####################################################################################################
# DATACLASSES
####################################################################################################


@dataclass(frozen=True, slots=True)
class ParsedAtom:
    """A parsed atom object."""

    name: str
    element: int
    charge: int
    coords: Tuple[float, float, float]
    conformer: Tuple[float, float, float]
    is_present: bool
    chirality: int


@dataclass(frozen=True, slots=True)
class ParsedBond:
    """A parsed bond object."""

    atom_1: int
    atom_2: int
    type: int


@dataclass(frozen=True, slots=True)
class ParsedResidue:
    """A parsed residue object."""

    name: str
    type: int
    idx: int
    atoms: List[ParsedAtom]
    bonds: List[ParsedBond]
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
    type: str
    residues: List[ParsedResidue]


####################################################################################################
# HELPERS
####################################################################################################


def get_unk_token(dtype: gemmi.PolymerType) -> str:
    """Get the unknown token for a given entity type.

    Parameters
    ----------
    dtype : gemmi.EntityType
        The entity type.

    Returns
    -------
    str
        The unknown token.

    """
    if dtype == gemmi.PolymerType.PeptideL:
        unk = const.unk_token["PROTEIN"]
    elif dtype == gemmi.PolymerType.Dna:
        unk = const.unk_token["DNA"]
    elif dtype == gemmi.PolymerType.Rna:
        unk = const.unk_token["RNA"]
    else:
        msg = f"Unknown polymer type: {dtype}"
        raise ValueError(msg)

    return unk


def get_conformer(mol: Mol) -> Conformer:
    """Retrieve an rdkit object for a deemed conformer.

    Inspired by `pdbeccdutils.core.component.Component`.

    Parameters
    ----------
    mol: Mol
        The molecule to process.

    Returns
    -------
    Conformer
        The desired conformer, if any.

    Raises
    ------
    ValueError
        If there are no conformers of the given tyoe.

    """
    for c in mol.GetConformers():
        try:
            if c.GetProp("name") == ConformerType.Computed.name:
                return c
        except KeyError:  # noqa: PERF203
            pass

    for c in mol.GetConformers():
        try:
            if c.GetProp("name") == ConformerType.Ideal.name:
                return c
        except KeyError:  # noqa: PERF203
            pass

    msg = "Conformer does not exist."
    raise ValueError(msg)


####################################################################################################
# PARSING
####################################################################################################


def parse_ccd_residue(
    name: str,
    components: Dict[str, Mol],
    res_idx: int,
) -> Optional[ParsedResidue]:
    """Parse an MMCIF ligand.

    First tries to get the SMILES string from the RCSB.
    Then, tries to infer atom ordering using RDKit.

    Parameters
    ----------
    name: str
        The name of the molecule to parse.
    components : Dict
        The preprocessed PDB components dictionary.
    res_idx : int
        The residue index.

    Returns
    -------
    ParsedResidue, optional
       The output ParsedResidue, if successful.

    """
    unk_chirality = const.chirality_type_ids[const.unk_chirality_type]

    # Get reference component
    ref_mol = components[name]

    # Remove hydrogens
    ref_mol = AllChem.RemoveHs(ref_mol, sanitize=False)

    # Check if this is a single atom CCD residue
    if ref_mol.GetNumAtoms() == 1:
        pos = (0, 0, 0)
        ref_atom = ref_mol.GetAtoms()[0]
        chirality_type = const.chirality_type_ids.get(
            ref_atom.GetChiralTag(), unk_chirality
        )
        atom = ParsedAtom(
            name=ref_atom.GetProp("name"),
            element=ref_atom.GetAtomicNum(),
            charge=ref_atom.GetFormalCharge(),
            coords=pos,
            conformer=(0, 0, 0),
            is_present=True,
            chirality=chirality_type,
        )
        unk_prot_id = const.unk_token_ids["PROTEIN"]
        residue = ParsedResidue(
            name=name,
            type=unk_prot_id,
            atoms=[atom],
            bonds=[],
            idx=res_idx,
            orig_idx=None,
            atom_center=0,  # Placeholder, no center
            atom_disto=0,  # Placeholder, no center
            is_standard=False,
            is_present=True,
        )
        return residue

    # Get reference conformer coordinates
    conformer = get_conformer(ref_mol)

    # Parse each atom in order of the reference mol
    atoms = []
    atom_idx = 0
    idx_map = {}  # Used for bonds later

    for i, atom in enumerate(ref_mol.GetAtoms()):
        # Get atom name, charge, element and reference coordinates
        atom_name = atom.GetProp("name")
        charge = atom.GetFormalCharge()
        element = atom.GetAtomicNum()
        ref_coords = conformer.GetAtomPosition(atom.GetIdx())
        ref_coords = (ref_coords.x, ref_coords.y, ref_coords.z)
        chirality_type = const.chirality_type_ids.get(
            atom.GetChiralTag(), unk_chirality
        )

        # Get PDB coordinates, if any
        coords = (0, 0, 0)
        atom_is_present = True

        # Add atom to list
        atoms.append(
            ParsedAtom(
                name=atom_name,
                element=element,
                charge=charge,
                coords=coords,
                conformer=ref_coords,
                is_present=atom_is_present,
                chirality=chirality_type,
            )
        )
        idx_map[i] = atom_idx
        atom_idx += 1  # noqa: SIM113

    # Load bonds
    bonds = []
    unk_bond = const.bond_type_ids[const.unk_bond_type]
    for bond in ref_mol.GetBonds():
        idx_1 = bond.GetBeginAtomIdx()
        idx_2 = bond.GetEndAtomIdx()

        # Skip bonds with atoms ignored
        if (idx_1 not in idx_map) or (idx_2 not in idx_map):
            continue

        idx_1 = idx_map[idx_1]
        idx_2 = idx_map[idx_2]
        start = min(idx_1, idx_2)
        end = max(idx_1, idx_2)
        bond_type = bond.GetBondType().name
        bond_type = const.bond_type_ids.get(bond_type, unk_bond)
        bonds.append(ParsedBond(start, end, bond_type))

    unk_prot_id = const.unk_token_ids["PROTEIN"]
    return ParsedResidue(
        name=name,
        type=unk_prot_id,
        atoms=atoms,
        bonds=bonds,
        idx=res_idx,
        atom_center=0,
        atom_disto=0,
        orig_idx=None,
        is_standard=False,
        is_present=True,
    )


def parse_polymer(
    sequence: List[str],
    chain_id: str,
    entity: str,
    components: Dict[str, Mol],
) -> Optional[ParsedChain]:
    """Process a gemmi Polymer into a chain object.

    Performs alignment of the full sequence to the polymer
    residues. Loads coordinates and masks for the atoms in
    the polymer, following the ordering in const.atom_order.

    Parameters
    ----------
    polymer : gemmi.ResidueSpan
        The polymer to process.
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
    unk_chirality = const.chirality_type_ids[const.unk_chirality_type]

    # Check what type of sequence this is
    if all(c in const.rna_letter_to_token for c in sequence):
        chain_type = const.chain_type_ids["RNA"]
        token_map = const.rna_letter_to_token
    elif all(c in const.dna_letter_to_token for c in sequence):
        chain_type = const.chain_type_ids["DNA"]
        token_map = const.dna_letter_to_token
    elif all(c in const.prot_letter_to_token for c in sequence):
        chain_type = const.chain_type_ids["PROTEIN"]
        token_map = const.prot_letter_to_token
    else:
        msg = f"Unknown polymer type: {sequence}"
        raise ValueError(msg)

    # Get coordinates and masks
    parsed = []
    for res_idx, res_code in enumerate(sequence):
        # Load ref residue
        res_name = token_map[res_code]
        ref_mol = components[res_name]
        ref_mol = AllChem.RemoveHs(ref_mol, sanitize=False)
        ref_conformer = get_conformer(ref_mol)

        # Only use reference atoms set in constants
        ref_name_to_atom = {a.GetProp("name"): a for a in ref_mol.GetAtoms()}
        ref_atoms = [ref_name_to_atom[a] for a in const.ref_atoms[res_name]]

        # Iterate, always in the same order
        atoms: List[ParsedAtom] = []

        for ref_atom in ref_atoms:
            # Get atom name
            atom_name = ref_atom.GetProp("name")
            idx = ref_atom.GetIdx()

            # Get conformer coordinates
            ref_coords = ref_conformer.GetAtomPosition(idx)
            ref_coords = (ref_coords.x, ref_coords.y, ref_coords.z)

            # Set 0 coordinate
            atom_is_present = True
            coords = (0, 0, 0)

            # Add atom to list
            atoms.append(
                ParsedAtom(
                    name=atom_name,
                    element=ref_atom.GetAtomicNum(),
                    charge=ref_atom.GetFormalCharge(),
                    coords=coords,
                    conformer=ref_coords,
                    is_present=atom_is_present,
                    chirality=const.chirality_type_ids.get(
                        ref_atom.GetChiralTag(), unk_chirality
                    ),
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
                idx=res_idx,
                atom_center=atom_center,
                atom_disto=atom_disto,
                is_standard=True,
                is_present=True,
                orig_idx=None,
            )
        )

    # Return polymer object
    return ParsedChain(
        name=chain_id,
        entity=entity,
        residues=parsed,
        type=chain_type,
    )


def parse_fasta(
    fasta_file: Path,
    components: Mapping[str, Mol],
) -> Structure:
    """Parse a fasta file.

    Parameters
    ----------
    fasta_file : Path
        Path to the fasta file.
    components : Dict
        Dictionary of CCD components.

    Returns
    -------
    Structure
        The parsed structure.

    """
    with fasta_file.open("r") as f:
        records = list(SeqIO.parse(f, "fasta"))

    # Disable rdkit warnings
    blocker = rdBase.BlockLogs()  # noqa: F841

    # Group by entities
    entity_id = 0
    seq_to_entity: Dict[str, str] = {}
    for seq_record in records:
        if str(seq_record.seq) not in seq_to_entity:
            seq_to_entity[str(seq_record.seq)] = str(entity_id)
            entity_id += 1

    # Parse chains
    chains: List[ParsedChain] = []
    chain_id_to_entity: Dict[int, str] = {}
    for chain_id, seq_record in enumerate(records):
        # Get entity
        entity_type = "NonPolymer" if "LIGAND" in seq_record.id else "Polymer"
        entity_id = seq_to_entity[str(seq_record.seq)]
        chain_id_to_entity[chain_id] = entity_id

        # Parse a polymer
        if entity_type == "Polymer":
            parsed_polymer = parse_polymer(
                sequence=list(str(seq_record.seq)),
                chain_id=chain_id,
                entity=str(entity_id),
                components=components,
            )
            chains.append(parsed_polymer)

        # Parse a non-polymer
        elif entity_type == "NonPolymer":
            residue = parse_ccd_residue(
                name=str(seq_record.seq),
                components=components,
                res_idx=0,
            )
            chains.append(
                ParsedChain(
                    name=chain_id,
                    entity=str(entity_id),
                    residues=[residue],
                    type=const.chain_type_ids["NONPOLYMER"],
                )
            )

    # If no chains parsed fail
    if not chains:
        msg = "No chains parsed!"
        raise ValueError(msg)

    # Create tables
    atom_data = []
    bond_data = []
    res_data = []
    chain_data = []

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
                atom_data.append(
                    (
                        atom.name,
                        atom.coords,
                        atom.is_present,
                        atom.chirality,
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
    ensemble = np.array([], dtype=Ensemble)
    coords = np.array([], dtype=Coords)

    data = Structure(
        atoms=atoms,
        bonds=bonds,
        residues=residues,
        chains=chains,
        interfaces=interfaces,
        mask=mask,
        ensemble=ensemble,
        coords=coords,
    )

    return data
