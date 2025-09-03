from collections.abc import Mapping
from dataclasses import dataclass
from dataclasses import replace, astuple
from collections import defaultdict
from pathlib import Path
import re
from typing import Optional

import click
import numpy as np
from Bio import Align
from rdkit import Chem, rdBase
from rdkit.Chem import AllChem
from rdkit.Chem.rdchem import Conformer, Mol
from rdkit.Chem.rdMolDescriptors import CalcNumHeavyAtoms
from scipy.spatial.distance import cdist
import yaml

from foldeverything.data import const
from foldeverything.data.mol import load_molecules
from foldeverything.data.parse.mmcif import parse_mmcif
from foldeverything.data.parse.pdb_parser import parse_pdb
from foldeverything.data.select.protein_new import next_label
from foldeverything.data.data import (
    Atom,
    Bond,
    Chain,
    ChainInfo,
    Coords,
    DesignInfo,
    Ensemble,
    Interface,
    Record,
    Residue,
    Structure,
    StructureInfo,
    Target,
    TemplateInfo,
    Token,
)
from foldeverything.data.tokenize.af3 import TokenData
from dataclasses import replace

####################################################################################################
# DATACLASSES
####################################################################################################


@dataclass(frozen=True)
class ParsedAtom:
    """A parsed atom object."""

    name: str
    element: int
    charge: int
    coords: tuple[float, float, float]
    conformer: tuple[float, float, float]
    is_present: bool
    chirality: int


@dataclass(frozen=True)
class ParsedBond:
    """A parsed bond object."""

    atom_1: int
    atom_2: int
    type: int


@dataclass(frozen=True)
class ParsedRDKitBoundsConstraint:
    """A parsed RDKit bounds constraint object."""

    atom_idxs: tuple[int, int]
    is_bond: bool
    is_angle: bool
    upper_bound: float
    lower_bound: float


@dataclass(frozen=True)
class ParsedChiralAtomConstraint:
    """A parsed chiral atom constraint object."""

    atom_idxs: tuple[int, int, int, int]
    is_reference: bool
    is_r: bool


@dataclass(frozen=True)
class ParsedStereoBondConstraint:
    """A parsed stereo bond constraint object."""

    atom_idxs: tuple[int, int, int, int]
    is_check: bool
    is_e: bool


@dataclass(frozen=True)
class ParsedPlanarBondConstraint:
    """A parsed planar bond constraint object."""

    atom_idxs: tuple[int, int, int, int, int, int]


@dataclass(frozen=True)
class ParsedPlanarRing5Constraint:
    """A parsed planar bond constraint object."""

    atom_idxs: tuple[int, int, int, int, int]


@dataclass(frozen=True)
class ParsedPlanarRing6Constraint:
    """A parsed planar bond constraint object."""

    atom_idxs: tuple[int, int, int, int, int, int]


@dataclass(frozen=True)
class ParsedResidue:
    """A parsed residue object."""

    name: str
    type: int
    idx: int
    atoms: list[ParsedAtom]
    bonds: list[ParsedBond]
    orig_idx: Optional[int]
    atom_center: int
    atom_disto: int
    is_standard: bool
    is_present: bool


@dataclass(frozen=True)
class ParsedChain:
    """A parsed chain object."""

    entity: str
    type: int
    residues: list[ParsedResidue]
    res_design_mask: list[bool]
    cyclic_period: int
    sequence: Optional[str] = None
    sampleidx_to_specidx: Optional[np.ndarray] = None


@dataclass(frozen=True)
class Alignment:
    """A parsed alignment object."""

    query_st: int
    query_en: int
    template_st: int
    template_en: int


####################################################################################################
# HELPERS
####################################################################################################


def compute_3d_conformer(mol: Mol, version: str = "v3") -> bool:
    """Generate 3D coordinates using EKTDG method.

    Taken from `pdbeccdutils.core.component.Component`.

    Parameters
    ----------
    mol: Mol
        The RDKit molecule to process
    version: str, optional
        The ETKDG version, defaults ot v3

    Returns
    -------
    bool
        Whether computation was successful.

    """
    if version == "v3":
        options = AllChem.ETKDGv3()
    elif version == "v2":
        options = AllChem.ETKDGv2()
    else:
        options = AllChem.ETKDGv2()

    options.clearConfs = False
    conf_id = -1

    try:
        conf_id = AllChem.EmbedMolecule(mol, options)

        if conf_id == -1:
            print(
                f"WARNING: RDKit ETKDGv3 failed to generate a conformer for molecule "
                f"{Chem.MolToSmiles(AllChem.RemoveHs(mol))}, so the program will start with random coordinates. "
                f"Note that the performance of the model under this behaviour was not tested."
            )
            options.useRandomCoords = True
            conf_id = AllChem.EmbedMolecule(mol, options)

        AllChem.UFFOptimizeMolecule(mol, confId=conf_id, maxIters=1000)

    except RuntimeError:
        pass  # Force field issue here
    except ValueError:
        pass  # sanitization issue here

    if conf_id != -1:
        conformer = mol.GetConformer(conf_id)
        conformer.SetProp("name", "Computed")
        conformer.SetProp("coord_generation", f"ETKDG{version}")

        return True

    return False


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
    # Try using the computed conformer
    for c in mol.GetConformers():
        try:
            if c.GetProp("name") == "Computed":
                return c
        except KeyError:  # noqa: PERF203
            pass

    # Fallback to the ideal coordinates
    for c in mol.GetConformers():
        try:
            if c.GetProp("name") == "Ideal":
                return c
        except KeyError:  # noqa: PERF203
            pass

    # Fallback to boltz2 format
    conf_ids = [int(conf.GetId()) for conf in mol.GetConformers()]
    if len(conf_ids) > 0:
        conf_id = conf_ids[0]
        conformer = mol.GetConformer(conf_id)
        return conformer

    msg = "Conformer does not exist."
    raise ValueError(msg)


def get_mol(ccd: str, mols: dict, moldir: str) -> Mol:
    """Get mol from CCD code.

    Return mol with ccd from mols if it is in mols. Otherwise load it from moldir,
    add it to mols, and return the mol.
    """
    mol = mols.get(ccd)
    if mol is None:
        mol = load_molecules(moldir, [ccd])[ccd]
    return mol


####################################################################################################
# PARSING
####################################################################################################
def parse_ccd_residue(
    name: str,
    ref_mol: Mol,
    res_idx: int,
) -> Optional[ParsedResidue]:
    """Parse an MMCIF ligand.

    First tries to get the SMILES string from the RCSB.
    Then, tries to infer atom ordering using RDKit.

    Parameters
    ----------
    name: str
        The name of the molecule to parse.
    ref_mol: Mol
        The reference molecule to parse.
    res_idx : int
        The residue index.

    Returns
    -------
    ParsedResidue, optional
       The output ParsedResidue, if successful.

    """
    unk_chirality = const.chirality_type_ids[const.unk_chirality_type]

    # Check if this is a single heavy atom CCD residue
    if CalcNumHeavyAtoms(ref_mol) == 1:
        # Remove hydrogens
        ref_mol = AllChem.RemoveHs(ref_mol, sanitize=False)

        pos = (0, 0, 0)
        ref_atom = ref_mol.GetAtoms()[0]
        chirality_type = const.chirality_type_ids.get(
            str(ref_atom.GetChiralTag()), unk_chirality
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
        # Ignore Hydrogen atoms
        if atom.GetAtomicNum() == 1:
            continue

        # Get atom name, charge, element and reference coordinates
        atom_name = atom.GetProp("name")
        charge = atom.GetFormalCharge()
        element = atom.GetAtomicNum()
        ref_coords = conformer.GetAtomPosition(atom.GetIdx())
        ref_coords = (ref_coords.x, ref_coords.y, ref_coords.z)
        chirality_type = const.chirality_type_ids.get(
            str(atom.GetChiralTag()), unk_chirality
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
    sequence: list[str],
    raw_sequence: str,
    entity: str,
    chain_type: str,
    components: dict[str, Mol],
    cyclic: bool,
    mol_dir: Path,
) -> Optional[ParsedChain]:
    """Process a sequence into a chain object.

    Performs alignment of the full sequence to the polymer
    residues. Loads coordinates and masks for the atoms in
    the polymer, following the ordering in const.atom_order.

    Parameters
    ----------
    sequence : list[str]
        The full sequence of the polymer.
    entity : str
        The entity id.
    entity_type : str
        The entity type.
    components : dict[str, Mol]
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
    ref_res = set(const.tokens)
    unk_chirality = const.chirality_type_ids[const.unk_chirality_type]

    # Make sequence and distinguish between design and non-design
    seq_processed = []
    res_design_mask = []
    sampleidx_to_specidx = []
    count = 0
    for token in sequence:
        if isinstance(token, str):
            seq_processed.append(token)
            res_design_mask.append(False)
            sampleidx_to_specidx.append(count)
            count += 1
        elif isinstance(token, tuple):
            if len(token) == 1:
                num = start = token[0]
                sampleidx_to_specidx.extend(range(count, count + num))
            elif len(token) == 2:
                start, end = token
                num = np.random.randint(start, end + 1)
                mapping = list(range(count, count + start))
                mapping += [count + start - 1] * (num - start)
                sampleidx_to_specidx.extend(mapping)
            res_design_mask.extend([True] * num)
            seq_processed.extend(["GLY"] * num)
            count += start
        else:
            raise ValueError("Token must be tuple of int or string")
    sampleidx_to_specidx = np.array(sampleidx_to_specidx)

    # Get coordinates and masks
    parsed = []
    for res_idx, res_name in enumerate(seq_processed):
        # Check if modified residue
        # Map MSE to MET
        res_corrected = res_name if res_name != "MSE" else "MET"

        # Handle non-standard residues
        if res_corrected not in ref_res:
            ref_mol = get_mol(res_corrected, components, mol_dir)
            residue = parse_ccd_residue(
                name=res_corrected,
                ref_mol=ref_mol,
                res_idx=res_idx,
            )
            parsed.append(residue)
            continue

        # Load ref residue
        ref_mol = get_mol(res_corrected, components, mol_dir)
        ref_mol = AllChem.RemoveHs(ref_mol, sanitize=False)
        ref_conformer = get_conformer(ref_mol)

        # Only use reference atoms set in constants
        ref_name_to_atom = {a.GetProp("name"): a for a in ref_mol.GetAtoms()}
        ref_atoms = [ref_name_to_atom[a] for a in const.ref_atoms[res_corrected]]

        # Iterate, always in the same order
        atoms: list[ParsedAtom] = []

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
                        str(ref_atom.GetChiralTag()), unk_chirality
                    ),
                )
            )

        atom_center = const.res_to_center_atom_id[res_corrected]
        atom_disto = const.res_to_disto_atom_id[res_corrected]
        parsed.append(
            ParsedResidue(
                name=res_corrected,
                type=const.token_ids[res_corrected],
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
    if cyclic:
        cyclic_period = len(seq_processed)
    else:
        cyclic_period = 0
    # Return polymer object
    return ParsedChain(
        entity=entity,
        residues=parsed,
        res_design_mask=res_design_mask,
        type=chain_type,
        cyclic_period=cyclic_period,
        sequence=raw_sequence,
        sampleidx_to_specidx=sampleidx_to_specidx,
    )


# Define helper
def parse_range(ranges, c_start=0, c_end=None):
    ranges = str(ranges)
    if "," in ranges:
        spec_list = ranges.split(",")
    else:
        spec_list = [ranges]

    indices = []
    for spec in spec_list:
        if re.fullmatch(r"\d+", spec):
            # Single number. Convert it from 1 indexed to 0 indexed.
            start = int(spec) - 1
            end = int(spec) - 1
            indices.append(c_start + start)
        elif re.fullmatch(r"\d+..\d+", spec):
            # Range with start and end. Convert the start from 1 indexed to 0 indexed. Leave the end untouched because the specification is inclusive (+1) but 1 indexed (-1).
            start, end = map(int, spec.split(".."))
            start -= 1
            indices += list(range(c_start + start, c_start + end))
        elif re.fullmatch(r"..\d+", spec):
            # Range that is inclusive of the specified end (which is specified in a 1 indexed fashion).
            end = int(spec.replace("..", ""))
            start = 0
            indices += list(range(c_start, c_start + end))
        elif re.fullmatch(r"\d+..", spec):
            assert c_end is not None
            # Range that is inclusive of the specified start (which is specified in a 1 indexed fashion).
            start = int(spec.replace("..", ""))
            start -= 1
            end = c_end - c_start
            indices += list(range(c_start + start, c_end))
    if start < 0:
        msg = f"There is a 0 in the specified range(s) {ranges}. Residue indices are 1 indexed."
        raise ValueError(msg)

    if c_end is not None and end > c_end - c_start:
        msg = f"Specified end {ranges} is higher than the lenght of the chain."
        raise ValueError(msg)
    return indices


def parse_boltz_schema(  # noqa: C901, PLR0915, PLR0912
    name: str,
    schema: dict,
    mols: Mapping[str, Mol],
    mol_dir: Optional[Path] = None,
) -> Target:
    """Parse a Boltz input yaml / json.

    The input file should be a dictionary with the following format:

    version: 1
    sequences:
        - protein:
            id: A
            sequence: "MADQLTEEQIAEFKEAFSLF"
        - protein:
            id: [B, C]
            sequence: "AKLSILPWGHC"
        - rna:
            id: D
            sequence: "GCAUAGC"
        - ligand:
            id: E
            smiles: "CC1=CC=CC=C1"
        - ligand:
            id: [F, G]
            ccd: []
    constraints:
        - bond:
            atom1: [A, 1, CA]
            atom2: [A, 2, N]
    templates:
        - cif: path/to/template.cif
    Parameters
    ----------
    name : str
        A name for the input.
    schema : dict
        The input schema.
    components : dict
        Dictionary of CCD components.
    mol_dir: Path
        Path to the directory containing the molecules.
    boltz2: bool
        Whether to parse the input for Boltz2.

    Returns
    -------
    Target
        The parsed target.

    """
    # Assert version 1
    version = schema.get("version", 1)
    if version != 1:
        msg = f"Invalid version {version} in input!"
        raise ValueError(msg)

    # Assert no ambiguous namings present
    for name in ["res_idx", "residue_idx", "residue_index"]:
        if name in str(schema):
            raise ValueError(f"Found {name} in yaml. Did you mean 'res_index'?")

    # Disable rdkit warnings
    blocker = rdBase.BlockLogs()  # noqa: F841

    # First group items that have the same type, sequence and modifications
    items_to_group = {}
    for item in schema["sequences"]:
        # Get entity type
        entity_type = next(iter(item.keys())).lower()
        if entity_type not in {"protein", "dna", "rna", "ligand", "file", "anchors"}:
            msg = f"Invalid entity type: {entity_type}"
            raise ValueError(msg)

        # Get sequence
        if entity_type in {"protein", "dna", "rna"}:
            seq = str(item[entity_type]["sequence"])
        elif entity_type == "ligand":
            assert "smiles" in item[entity_type] or "ccd" in item[entity_type]
            assert "smiles" not in item[entity_type] or "ccd" not in item[entity_type]
            if "smiles" in item[entity_type]:
                seq = str(item[entity_type]["smiles"])
            else:
                seq = str(item[entity_type]["ccd"])
        elif entity_type == "anchors":
            continue
        if entity_type != "file":
            items_to_group.setdefault((entity_type, seq), []).append(item)

    # Go through entities and parse them
    extra_mols: dict[str, Mol] = {}
    parsed_chains: dict[str, ParsedChain] = {}
    res_bind_type: list[int] = []
    ss_type: list[int] = []
    chain_to_msa: dict[str, str] = {}
    entity_to_seq: dict[str, str] = {}
    is_msa_custom = False
    is_msa_auto = False
    ligand_id = 1
    for entity_id, items in enumerate(items_to_group.values()):
        # Get entity type and sequence
        entity_type = next(iter(items[0].keys())).lower()

        # Ensure all the items share the same msa
        msa = -1
        if entity_type == "protein":
            designed = bool(re.search(r"\d", str(items[0][entity_type]["sequence"])))
            if designed:
                # Get the msa, default to -1, meaning no msa.
                msa = items[0][entity_type].get("msa", -1)
                if (msa is None) or (msa == ""):
                    msa = -1
            else:
                # Get the msa, default to 0, meaning auto-generated
                msa = items[0][entity_type].get("msa", 0)
                if (msa is None) or (msa == ""):
                    msa = 0

            # Check if all MSAs are the same within the same entity
            for item in items:
                item_msa = item[entity_type].get("msa", 0)
                if (item_msa is None) or (item_msa == ""):
                    item_msa = 0

                if item_msa != msa and not designed:
                    msg = "All proteins with the same sequence must share the same MSA!"
                    raise ValueError(msg)

            # Set the MSA, warn if passed in single-sequence mode
            if msa == "empty":
                msa = -1
                msg = (
                    "Found explicit empty MSA for some proteins, will run "
                    "these in single sequence mode."
                )
                click.echo(msg)

            if msa not in (0, -1):
                is_msa_custom = True
            elif msa == 0:
                is_msa_auto = True

        # Parse a polymer
        if entity_type in {"protein", "dna", "rna"}:
            # Get token map
            if entity_type == "rna":
                token_map = const.rna_letter_to_token
            elif entity_type == "dna":
                token_map = const.dna_letter_to_token
            elif entity_type == "protein":
                token_map = const.prot_letter_to_token
            else:
                msg = f"Unknown polymer type: {entity_type}"
                raise ValueError(msg)

            # Get polymer info
            chain_type = const.chain_type_ids[entity_type.upper()]
            unk_token = const.unk_token[entity_type.upper()]

            # Extract sequence
            raw_seq = str(items[0][entity_type]["sequence"])
            entity_to_seq[entity_id] = raw_seq

            # Convert sequence to standard and design tokens
            tokens = re.findall(r"\d+\.\.\d+|\d+|[a-zA-Z]", raw_seq)
            seq = []
            for token in tokens:
                if re.fullmatch(r"\d+..\d+", token):  # Case 2: range
                    start, end = map(int, token.split(".."))
                    seq.append((start, end))
                elif re.fullmatch(r"\d+", token):  # Case 1: single number
                    seq.append((int(token),))
                else:
                    seq.extend([token_map.get(c, unk_token) for c in token])

            # Apply modifications
            for mod in items[0][entity_type].get("modifications", []):
                code = mod["ccd"]
                idx = mod["position"] - 1  # 1-indexed
                seq[idx] = code

            cyclic = items[0][entity_type].get("cyclic", False)

            # Parse a polymer
            parsed_chain = parse_polymer(
                sequence=seq,
                raw_sequence=raw_seq,
                entity=entity_id,
                chain_type=chain_type,
                components=mols,
                cyclic=cyclic,
                mol_dir=mol_dir,
            )

        # Parse a non-polymer
        elif (entity_type == "ligand") and "ccd" in (items[0][entity_type]):
            seq = items[0][entity_type]["ccd"]
            if isinstance(seq, str):
                seq = [seq]

            residues = []
            for res_idx, code in enumerate(seq):
                # Get mol
                ref_mol = get_mol(code, mols, mol_dir)

                # Parse residue
                residue = parse_ccd_residue(
                    name=code,
                    ref_mol=ref_mol,
                    res_idx=res_idx,
                )
                residues.append(residue)

            # Create multi ligand chain
            parsed_chain = ParsedChain(
                entity=entity_id,
                residues=residues,
                res_design_mask=[False] * len(residues),
                type=const.chain_type_ids["NONPOLYMER"],
                cyclic_period=0,
                sequence=None,
            )

            assert not items[0][entity_type].get("cyclic", False), (
                "Cyclic flag is not supported for ligands"
            )

        elif (entity_type == "ligand") and ("smiles" in items[0][entity_type]):
            seq = items[0][entity_type]["smiles"]
            mol = AllChem.MolFromSmiles(seq)
            mol = AllChem.AddHs(mol)

            # Set atom names
            canonical_order = AllChem.CanonicalRankAtoms(mol)
            for atom, can_idx in zip(mol.GetAtoms(), canonical_order):
                atom_name = atom.GetSymbol().upper() + str(can_idx + 1)
                if len(atom_name) > 4:
                    raise ValueError(
                        f"{seq} has an atom with a name longer than 4 characters: {atom_name}"
                    )
                atom.SetProp("name", atom_name)

            success = compute_3d_conformer(mol)
            if not success:
                msg = f"Failed to compute 3D conformer for {seq}"
                raise ValueError(msg)

            mol_no_h = AllChem.RemoveHs(mol)
            extra_mols[f"LIG{ligand_id}"] = mol_no_h

            residue = parse_ccd_residue(
                name=f"LIG{ligand_id}",
                ref_mol=mol,
                res_idx=0,
            )
            ligand_id += 1
            parsed_chain = ParsedChain(
                entity=entity_id,
                residues=[residue],
                res_design_mask=[False],
                type=const.chain_type_ids["NONPOLYMER"],
                cyclic_period=0,
                sequence=None,
            )

            assert not items[0][entity_type].get("cyclic", False), (
                "Cyclic flag is not supported for ligands"
            )
        elif entity_type == "anchors":
            pass
        elif entity_type == "file":
            pass
        else:
            msg = f"Invalid entity type: {entity_type}"
            raise ValueError(msg)

        # Parse binding site specification
        num = len(parsed_chain.residues)
        for item in items:
            entry = item[entity_type]
            binding_spec = entry.get("binding_types", None)
            ids = item[entity_type]["id"]
            num_chains = 1 if isinstance(ids, str) else len(ids)
            for _ in range(num_chains):
                if binding_spec is not None:
                    if isinstance(binding_spec, str):
                        for char in binding_spec:
                            if char.lower() == "u":
                                res_bind_type.append(
                                    const.binding_type_ids["UNSPECIFIED"]
                                )
                            elif char.lower() == "b":
                                res_bind_type.append(const.binding_type_ids["BINDING"])
                            elif char.lower() == "n":
                                res_bind_type.append(
                                    const.binding_type_ids["NOT_BINDING"]
                                )
                            else:
                                msg = (
                                    f"Invalid binding_type '{char}' in: {binding_spec}"
                                )
                                raise ValueError(msg)

                        # Fill missing specification with unspecified
                        if len(binding_spec) < num:
                            num_missing = num - len(binding_spec)
                            res_bind_type.extend(
                                [const.binding_type_ids["UNSPECIFIED"]] * num_missing
                            )
                        if len(binding_spec) > num:
                            msg = f"Misspecified secondary_structure {binding_spec} which is shorter than the sequence."
                            raise ValueError(msg)
                    else:
                        types = np.ones(num) * const.binding_type_ids["UNSPECIFIED"]
                        if "binding" in binding_spec:
                            indices = parse_range(binding_spec["binding"], 0, num)
                            types[indices] = const.binding_type_ids["BINDING"]

                        if "not_binding" in binding_spec:
                            indices = parse_range(binding_spec["not_binding"], 0, num)
                            types[indices] = const.binding_type_ids["NOT_BINDING"]
                        res_bind_type.extend(types.tolist())
                else:
                    res_bind_type.extend([const.binding_type_ids["UNSPECIFIED"]] * num)

        # Parse ss conditioning specification
        for item in items:
            entry = item[entity_type]
            ss_spec = entry.get("secondary_structure", None)
            ids = item[entity_type]["id"]
            num_chains = 1 if isinstance(ids, str) else len(ids)
            for _ in range(num_chains):
                if ss_spec is not None:
                    if isinstance(ss_spec, str):
                        for char in ss_spec:
                            if char.lower() == "u":
                                ss_type.append(const.ss_type_ids["UNSPECIFIED"])
                            elif char.lower() == "l":
                                ss_type.append(const.ss_type_ids["LOOP"])
                            elif char.lower() == "h":
                                ss_type.append(const.ss_type_ids["HELIX"])
                            elif char.lower() == "s":
                                ss_type.append(const.ss_type_ids["SHEET"])
                            else:
                                msg = f"Invalid secondary_structure '{char}' in: {ss_spec}"
                                raise ValueError(msg)

                        # Fill missing specification with unspecified
                        if len(ss_spec) < num:
                            num_missing = num - len(ss_spec)
                            ss_type.extend(
                                [const.ss_type_ids["UNSPECIFIED"]] * num_missing
                            )
                        if len(ss_spec) > num:
                            msg = f"Misspecified secondary_structure {ss_spec} which is shorter than the sequence."
                            raise ValueError(msg)
                    else:
                        types = np.ones(num) * const.ss_type_ids["UNSPECIFIED"]
                        if "loop" in ss_spec:
                            indices = parse_range(ss_spec["loop"], 0, num)
                            types[indices] = const.ss_type_ids["LOOP"]
                        if "helix" in ss_spec:
                            indices = parse_range(ss_spec["helix"], 0, num)
                            types[indices] = const.ss_type_ids["HELIX"]
                        if "sheet" in ss_spec:
                            indices = parse_range(ss_spec["sheet"], 0, num)
                            types[indices] = const.ss_type_ids["SHEET"]
                        ss_type.extend(types.tolist())
                else:
                    ss_type.extend([const.ss_type_ids["UNSPECIFIED"]] * num)

        # Add as many parsed_chains as provided ids
        for item in items:
            if entity_type in {"protein", "dna", "rna", "ligand"}:
                ids = item[entity_type]["id"]
                if isinstance(ids, str):
                    ids = [ids]
                for chain_name in ids:
                    parsed_chains[chain_name] = parsed_chain
                    chain_to_msa[chain_name] = msa

    res_bind_type = np.array(res_bind_type, dtype=np.int32)
    ss_type = np.array(ss_type, dtype=np.int32)
    # Check if msa is custom or auto
    if is_msa_custom and is_msa_auto:
        msg = "Cannot mix custom and auto-generated MSAs in the same input!"
        raise ValueError(msg)

    # Create tables
    atom_data = []
    bond_data = []
    res_data = []
    chain_data = []
    res_design_mask = []
    anchor_mask = []  # Initialize anchor_mask here
    protein_chains = set()

    # Convert parsed chains to tables
    atom_idx = 0
    res_idx = 0
    asym_id = 0
    sym_count = {}
    chain_to_idx = {}

    # Keep a mapping of (chain_name, residue_idx, atom_name) to atom_idx
    atom_idx_map = {}

    for asym_id, (chain_name, chain) in enumerate(parsed_chains.items()):
        # Compute number of atoms and residues
        res_num = len(chain.residues)
        atom_num = sum(len(res.atoms) for res in chain.residues)

        # Extend res_design_mask
        res_design_mask.extend(chain.res_design_mask)

        # Save protein chains for later
        if chain.type == const.chain_type_ids["PROTEIN"]:
            protein_chains.add(chain_name)

        # Find all copies of this chain in the assembly
        entity_id = int(chain.entity)
        sym_id = sym_count.get(entity_id, 0)
        chain_data.append(
            (
                chain_name,
                chain.type,
                entity_id,
                sym_id,
                asym_id,
                atom_idx,
                atom_num,
                res_idx,
                res_num,
                chain.cyclic_period,
            )
        )
        chain_to_idx[chain_name] = asym_id
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
                atom_1 = atom_idx + bond.atom_1
                atom_2 = atom_idx + bond.atom_2
                bond_data.append(
                    (
                        asym_id,
                        asym_id,
                        res_idx,
                        res_idx,
                        atom_1,
                        atom_2,
                        bond.type,
                    )
                )

            for atom in res.atoms:
                # Add atom to map
                atom_idx_map[(chain_name, res.idx, atom.name)] = (
                    asym_id,
                    res_idx,
                    atom_idx,
                )

                # Add atom to data
                atom_data.append(
                    (
                        atom.name,
                        atom.element,
                        atom.charge,
                        atom.coords,
                        atom.conformer,
                        atom.is_present,
                        atom.chirality,
                    )
                )
                atom_idx += 1
            res_idx += 1
        if chain.cyclic_period > 0:
            bond_data.append(
                (
                    asym_id,
                    asym_id,
                    0,
                    chain.cyclic_period - 1,
                    atom_idx_map[(chain_name, 0, "N")][2],
                    atom_idx_map[(chain_name, chain.cyclic_period - 1, "C")][2],
                    const.bond_type_ids["COVALENT"],
                )
            )
    res_design_mask = np.array(res_design_mask)

    # Parse constraints
    connections = []
    constraints = schema.get("constraints", [])
    for constraint in constraints:
        if "bond" in constraint:
            if "atom1" not in constraint["bond"] or "atom2" not in constraint["bond"]:
                msg = f"Bond constraint was not properly specified"
                raise ValueError(msg)

            c1, r1, a1 = tuple(constraint["bond"]["atom1"])
            c2, r2, a2 = tuple(constraint["bond"]["atom2"])
            r1 = r1 - 1  # 1-indexed
            r2 = r2 - 1  # 1-indexed

            # Map index
            if parsed_chains[c1].sampleidx_to_specidx is not None:
                r1 = np.where(parsed_chains[c1].sampleidx_to_specidx == r1)[0].item()
            if parsed_chains[c2].sampleidx_to_specidx is not None:
                r2 = np.where(parsed_chains[c2].sampleidx_to_specidx == r2)[0].item()

            c1, r1, a1 = atom_idx_map[(c1, r1, a1)]
            c2, r2, a2 = atom_idx_map[(c2, r2, a2)]

            connections.append((c1, c2, r1, r2, a1, a2))
        elif "total_len" in constraint:
            total_len = constraints["total_len"]
            if "min" in total_len:
                min_len = total_len["min"]
                if min_len < 0:
                    msg = f"Min length constraint must be non-negative"
                    raise ValueError(msg)
            if "max" in total_len:
                max_len = total_len["max"]
                if max_len < 0:
                    msg = f"Max length constraint must be non-negative"
                    raise ValueError(msg)
            if min_len > max_len:
                msg = f"Min length constraint is greater than max length constraint"
                raise ValueError(msg)

    # Convert into datatypes
    residues = np.array(res_data, dtype=Residue)
    chains = np.array(chain_data, dtype=Chain)
    interfaces = np.array([], dtype=Interface)
    mask = np.ones(len(chain_data), dtype=bool)

    atom_data = [(a[0], a[3], a[5], 0.0, 1.0) for a in atom_data]
    connections = [(*c, const.bond_type_ids["COVALENT"]) for c in connections]
    bond_data = bond_data + connections
    atoms = np.array(atom_data, dtype=Atom)
    bonds = np.array(bond_data, dtype=Bond)
    coords = [(x,) for x in atoms["coords"]]
    coords = np.array(coords, Coords)
    ensemble = np.array([(0, len(coords))], dtype=Ensemble)
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

    # File parsing
    structure_groups = np.zeros(len(data.residues), dtype=np.int32)
    for item in schema["sequences"]:
        entity_type = next(iter(item.keys())).lower()
        if entity_type != "file":
            continue

        # Setup
        file = item["file"]
        path = Path(file["path"])
        include = file.get("include", "all")  # include all by default
        include_proximity = file.get("include_proximity", None)
        exclude = file.get("exclude", None)
        structure_spec = file.get("structure_groups", None)
        design = file.get("design", None)
        not_design = file.get("not_design", None)
        file_msa_flag = file.get("msa", 0)  # default to automatic MSA generation
        if (file_msa_flag is None) or (file_msa_flag == ""):
            file_msa_flag = 0
        design_insertions = file.get("design_insertions", None)
        binding_types = file.get("binding_types", None)
        secondary_structure = file.get("secondary_structure", None)
        if isinstance(include, list):
            for chain in include:
                if "id" not in chain:
                    msg = f"Misspecified chain in include with missing 'id' for file with path {path}."
                    raise ValueError(msg)
                chain_id = chain["id"]
                if "smiles" in chain:
                    mol = AllChem.MolFromSmiles(chain["smiles"])
                    mol = AllChem.AddHs(mol)
                    element_counts = defaultdict(int)
                    for i, atom in enumerate(mol.GetAtoms()):
                        symbol = atom.GetSymbol()
                        element_counts[symbol] += 1
                        atom_name = f"{symbol}{element_counts[symbol]}"
                        atom.SetProp("name", atom_name)
                    mols[f"LIG{ligand_id}"] = mol
                    success = compute_3d_conformer(mol)
                    if not success:
                        msg = f"Failed to compute 3D conformer for given smiles string"
                        raise ValueError(msg)
                    extra_mols[f"LIG{ligand_id}"] = mol

        # Get structure
        if ".cif" in str(path):
            parsed = parse_mmcif(
                path,
                mols=mols,
                moldir=mol_dir,
                use_assembly=False,
            )
        elif ".pdb" in str(path):
            parsed = parse_pdb(path, mols=mols, moldir=mol_dir, use_assembly=False)

        structure = parsed.data
        num_res = len(structure.residues)

        # Construct include mask from include entries
        file_chain_to_msa = {}
        if isinstance(include, str):
            if include == "all":
                include_mask = np.ones(num_res)
            else:
                msg = f"Include has to be a list or 'all' to include everything in the file."
                raise ValueError(msg)
        elif isinstance(include, list):
            include_mask = np.zeros(num_res)
            for chain in include:
                if "id" not in chain:
                    msg = f"Misspecified chain in include with missing 'id' for file with path {path}."
                    raise ValueError(msg)
                chain_id = chain["id"]
                if chain_id not in structure.chains["name"]:
                    msg = f"Specified chain id {chain_id} not in file {path}."
                if "msa" in chain:
                    file_chain_to_msa[chain_id] = chain["msa"]
                data_chain = structure.chains[structure.chains["name"] == chain_id]
                c_start = data_chain["res_idx"].item()
                c_end = c_start + data_chain["res_num"].item()

                # Set include_mask values to 1
                if "res_index" not in chain:
                    include_mask[c_start:c_end] = 1
                else:
                    indices = parse_range(chain["res_index"], c_start, c_end)
                    include_mask[indices] = 1
        else:
            msg = "Include entry has to be a list of chains or 'all'."
            raise ValueError(msg)

        proximity_mask = np.ones(num_res)
        if include_proximity is not None:
            coords = np.array(
                [
                    structure.atoms[r["atom_center"]]["coords"]
                    for r in structure.residues
                ]
            )

            for chain in include_proximity:
                if "id" not in chain:
                    msg = f"Misspecified chain in include_proximity with missing 'id' for file with path {path}."
                    raise ValueError(msg)
                if "radius" not in chain:
                    msg = f"Misspecified chain in include_proximity with missing 'radius' for file with path {path}."
                    raise ValueError(msg)
                chain_id = chain["id"]
                radius = chain["radius"]
                if chain_id not in structure.chains["name"]:
                    msg = f"Specified chain id {chain_id} not in file {path}."

                data_chain = structure.chains[structure.chains["name"] == chain_id]
                c_start = data_chain["res_idx"].item()
                c_end = c_start + data_chain["res_num"].item()

                proximity_spec_mask = np.zeros(num_res)
                if "res_index" not in chain:
                    proximity_spec_mask[c_start:c_end] = 1
                else:
                    indices = parse_range(chain["res_index"], c_start, c_end)
                    proximity_spec_mask[indices] = 1

                queries = coords[proximity_spec_mask.astype(bool)]

                distances = cdist(coords, queries)
                dist_mask = distances < radius
                dist_mask = dist_mask.sum(-1) > 0
                proximity_mask *= dist_mask
        include_mask *= proximity_mask

        # Build exclude mask
        exclude_mask = np.ones(num_res)
        if exclude is not None:
            for chain in exclude:
                if "id" not in chain:
                    msg = f"Misspecified chain in exclude with missing 'id' for file with path {path}."
                    raise ValueError(msg)
                chain_id = chain["id"]
                if chain_id not in structure.chains["name"]:
                    msg = f"Specified chain id {chain_id} not in file {path}."

                data_chain = structure.chains[structure.chains["name"] == chain_id]
                c_start = data_chain["res_idx"].item()
                c_end = c_start + data_chain["res_num"].item()

                # Set exclude_mask values to 0
                if "res_index" not in chain:
                    include_mask[c_start:c_end] = 0
                else:
                    indices = parse_range(chain["res_index"], c_start, c_end)
                    exclude_mask[indices] = 0
        include_mask = (include_mask * exclude_mask).astype(bool)

        # Get structure groups
        new_groups = np.zeros(num_res)
        if structure_spec is None or structure_spec == "all" or structure_spec == 1:
            new_groups = np.ones(num_res)
        else:
            for group in structure_spec:
                if "id" not in group:
                    msg = f"Misspecified group in structure_groups with missing 'id' for file with path {path}."
                    raise ValueError(msg)
                if "visibility" not in group:
                    msg = f"Misspecified group in structure_groups with missing 'visibility' for file with path {path}."
                    raise ValueError(msg)
                chain_id = group["id"]

                # Handle the "all" case where all chains are set to be specified
                if chain_id == "all":
                    new_groups = np.ones(num_res)
                    continue

                if chain_id not in structure.chains["name"]:
                    msg = f"Specified chain id {chain_id} not in file {path}."
                    raise ValueError(msg)

                data_chain = structure.chains[structure.chains["name"] == chain_id]
                c_start = data_chain["res_idx"].item()
                c_end = c_start + data_chain["res_num"].item()
                visibility = group["visibility"]

                # Set structure group values to the correct visibility
                if "res_index" not in group:
                    new_groups[c_start:c_end] = visibility
                else:
                    indices = parse_range(group["res_index"], c_start, c_end)
                    new_groups[indices] = visibility

        # Get design mask for file
        new_design_mask = np.zeros(num_res)
        if design is not None:
            for chain in design:
                if "id" not in chain:
                    msg = f"Misspecified chain in design with missing 'id' for file with path {path}."
                    raise ValueError(msg)
                chain_id = chain["id"]

                # Handle the "all" case where all chains are set to be designed
                if chain_id == "all":
                    # TODO: handle case where users specify non-protein residues to be designed.
                    new_design_mask = np.ones(num_res)
                    continue

                if chain_id not in structure.chains["name"]:
                    msg = f"Specified chain id {chain_id} not in file {path}."
                    raise ValueError(msg)

                data_chain = structure.chains[structure.chains["name"] == chain_id]
                c_start = data_chain["res_idx"].item()
                c_end = c_start + data_chain["res_num"].item()

                # Set values
                if "res_index" not in chain:
                    new_design_mask[c_start:c_end] = 1
                else:
                    indices = parse_range(chain["res_index"], c_start, c_end)
                    new_design_mask[indices] = 1

        # Get modification mask to turn previous design regions into non-design regions
        new_design_mask_mod = np.ones(num_res)
        if not_design is not None:
            for chain in not_design:
                if "id" not in chain:
                    msg = f"Misspecified chain in not_design with missing 'id' for file with path {path}."
                    raise ValueError(msg)
                chain_id = chain["id"]

                if chain_id not in structure.chains["name"]:
                    msg = f"Specified chain id {chain_id} not in file {path}."
                    raise ValueError(msg)

                data_chain = structure.chains[structure.chains["name"] == chain_id]
                c_start = data_chain["res_idx"].item()
                c_end = c_start + data_chain["res_num"].item()

                # Set values
                if "res_index" not in chain:
                    new_design_mask_mod[c_start:c_end] = 0
                else:
                    indices = parse_range(chain["res_index"], c_start, c_end)
                    new_design_mask_mod[indices] = 0
        new_design_mask = (new_design_mask * new_design_mask_mod).astype(bool)

        # Get file's binding types called fbind_types
        fbind_types = np.ones(num_res) * const.binding_type_ids["UNSPECIFIED"]
        fbind_types = fbind_types.astype(np.int32)
        if binding_types is not None:
            for chain in binding_types:
                if "id" not in chain:
                    msg = f"Misspecified chain in binding_types with missing 'id' for file with path {path}."
                    raise ValueError(msg)
                chain_id = chain["id"]

                if chain_id not in structure.chains["name"]:
                    msg = f"Specified chain id {chain_id} not in file {path}."
                    raise ValueError(msg)

                data_chain = structure.chains[structure.chains["name"] == chain_id]
                c_start = data_chain["res_idx"].item()
                c_end = c_start + data_chain["res_num"].item()

                # Set values
                if "not_binding" in chain:
                    not_binding = chain["not_binding"]
                    if not_binding == "all":
                        fbind_types[c_start:c_end] = const.binding_type_ids[
                            "NOT_BINDING"
                        ]
                    else:
                        indices = parse_range(not_binding, c_start, c_end)
                        fbind_types[indices] = const.binding_type_ids["NOT_BINDING"]
                elif "binding" in chain:
                    binding = chain["binding"]
                    if binding == "all":
                        fbind_types[c_start:c_end] = const.binding_type_ids["BINDING"]
                    else:
                        indices = parse_range(binding, c_start, c_end)
                        fbind_types[indices] = const.binding_type_ids["BINDING"]

        # Get file's secondary structure types called fss_types
        fss_type = np.ones(num_res) * const.ss_type_ids["UNSPECIFIED"]
        fss_type = fss_type.astype(np.int32)
        if secondary_structure is not None:
            for chain in secondary_structure:
                if "id" not in chain:
                    msg = f"Misspecified chain in secondary_structure with missing 'id' for file with path {path}."
                    raise ValueError(msg)
                chain_id = chain["id"]

                if chain_id not in structure.chains["name"]:
                    msg = f"Specified chain id {chain_id} not in file {path}."
                    raise ValueError(msg)

                data_chain = structure.chains[structure.chains["name"] == chain_id]
                c_start = data_chain["res_idx"].item()
                c_end = c_start + data_chain["res_num"].item()

                # Set values
                if "loop" in chain:
                    loop = chain["loop"]
                    if loop == "all":
                        fss_type[c_start:c_end] = const.ss_type_ids["LOOP"]
                    else:
                        indices = parse_range(loop, c_start, c_end)
                        fss_type[indices] = const.ss_type_ids["LOOP"]
                elif "helix" in chain:
                    helix = chain["helix"]
                    if helix == "all":
                        fss_type[c_start:c_end] = const.ss_type_ids["HELIX"]
                    else:
                        indices = parse_range(helix, c_start, c_end)
                        fss_type[indices] = const.ss_type_ids["HELIX"]
                elif "sheet" in chain:
                    sheet = chain["sheet"]
                    if sheet == "all":
                        fss_type[c_start:c_end] = const.ss_type_ids["SHEET"]
                    else:
                        indices = parse_range(sheet, c_start, c_end)
                        fss_type[indices] = const.ss_type_ids["SHEET"]

        # Parse and apply design insertions
        if design_insertions is not None:
            for insertion in design_insertions:
                if "id" not in insertion:
                    msg = f"Misspecified insertion in design_insertions with missing 'id' for file with path {path}."
                    raise ValueError(msg)
                if "res_index" not in insertion:
                    msg = f"Misspecified insertion in design_insertions with missing 'res_index' for file with path {path}."
                    raise ValueError(msg)
                chain_id = insertion["id"]
                res_index = insertion["res_index"] - 1  # 1 index input to 0 indexed
                ss_insert_type = insertion.get("secondary_structure", "UNSPECIFIED")
                num_residues = insertion["num_residues"]
                num_residues = parse_range(num_residues)
                num_residues = np.random.choice(num_residues).item()

                if chain_id not in structure.chains["name"]:
                    msg = f"Specified chain id {chain_id} not in file {path}."
                    raise ValueError(msg)

                target_chain = structure.chains[structure.chains["name"] == chain_id]
                res_insert_idx = target_chain["res_idx"] + res_index

                # Insert into structure
                structure = Structure.insert(
                    structure, chain_id, res_idx=res_index, num_residues=num_residues
                )

                # Insert into design specifications
                include_mask = np.insert(
                    include_mask, res_insert_idx, np.ones(num_residues)
                )
                new_groups = np.insert(
                    new_groups, res_insert_idx, np.zeros(num_residues)
                )
                new_design_mask = np.insert(
                    new_design_mask, res_insert_idx, np.ones(num_residues)
                )
                fbind_types = np.insert(
                    fbind_types,
                    res_insert_idx,
                    np.ones(num_residues) * const.binding_type_ids["UNSPECIFIED"],
                )
                fss_type = np.insert(
                    fss_type,
                    res_insert_idx,
                    np.ones(num_residues) * const.ss_type_ids[ss_insert_type],
                )

        # Apply mask to new structure groups. Update structure_groups by concatenating existing and new one
        new_groups = new_groups[include_mask].astype(np.int32)
        structure_groups = np.concatenate([structure_groups, new_groups])

        # Apply mask to new design_mask. Update design by concatenating existing and new one.
        new_design_mask = new_design_mask[include_mask]
        res_design_mask = np.concatenate([res_design_mask, new_design_mask])

        # Apply mask to new binding_types. Update binding_types by concatenating existing and new one.
        fbind_types = fbind_types[include_mask].astype(np.int32)
        res_bind_type = np.concatenate([res_bind_type, fbind_types])

        # Apply mask to new ss_type. Update ss_type by concatenating existing and new one.
        fss_type = fss_type[include_mask].astype(np.int32)
        ss_type = np.concatenate([ss_type, fss_type])

        # Apply mask to structrue
        if not all(include_mask):
            new_structure = Structure.extract_residues(
                structure, include_mask.astype(bool)
            )
        else:
            new_structure = structure

        # Update structure by concatenating existing and new one
        data, renaming = Structure.concatenate(
            data, new_structure, return_renaming=True
        )

        if len(renaming) > 0:
            msg = f"Chain ids in '{path}' conflict with existing chain ids. Renaming them {renaming}."
            print(msg)

        # Update chain_to_msa dictionary. Set MSAs that are specified in include entries.
        new_chain_to_msa = {}
        for chain_id, msa in file_chain_to_msa.items():
            renamed_id = renaming.get(chain_id, chain_id)
            if renamed_id in chain_to_msa:
                raise KeyError(f"Key '{renamed_id}' already exists in chain_to_msa.")
            new_chain_to_msa[renamed_id] = msa
        chain_to_msa.update(new_chain_to_msa)

        # Update chain_to_msa dictionary. Set defaults given by file_msa_flag for proteins. Insert -1 (no msa) for {dna, rna, ligand}.
        for chain in data.chains:
            chain_id = chain["name"].item()
            if chain_id not in chain_to_msa:
                if chain["mol_type"] == const.chain_type_ids["PROTEIN"]:
                    chain_to_msa[chain_id] = file_msa_flag
                else:
                    chain_to_msa[chain_id] = -1
    anchor_mask = np.concatenate(
        [anchor_mask, np.zeros(len(res_bind_type), dtype=np.int32)]
    )
    charge_info = []
    num_anchor = 0
    for item in schema["sequences"]:
        entity_type = next(iter(item.keys())).lower()
        if entity_type != "anchors":
            continue
        res_dict_list = item[entity_type]["residues"]
        residues = []
        for idx in range(len(res_dict_list)):
            parsed_atoms = []
            parsed_bonds = []
            for atom_idx in range(len(res_dict_list[idx]["residue"]["atoms"])):
                atom = ParsedAtom(
                    name=res_dict_list[idx]["residue"]["atoms"][atom_idx]["atom"][
                        "atomtype"
                    ],
                    element=const.element_to_atomic_num[
                        res_dict_list[idx]["residue"]["atoms"][atom_idx]["atom"][
                            "atomtype"
                        ]
                    ],
                    charge=res_dict_list[idx]["residue"]["atoms"][atom_idx]["atom"][
                        "charge"
                    ],
                    coords=res_dict_list[idx]["residue"]["atoms"][atom_idx]["atom"][
                        "coord"
                    ],
                    conformer=(0, 0, 0),
                    is_present=True,
                    chirality=0,
                )
                parsed_atoms.append(atom)
            if "bonds" in res_dict_list[idx]["residue"].keys():
                for bond_idx in range(len(res_dict_list[idx]["residue"]["bonds"])):
                    bond = ParsedBond(
                        atom_1=res_dict_list[idx]["residue"]["bonds"][bond_idx]["bond"][
                            "atom1"
                        ][0],
                        atom_2=res_dict_list[idx]["residue"]["bonds"][bond_idx]["bond"][
                            "atom2"
                        ][0],
                        type=res_dict_list[idx]["residue"]["bonds"][bond_idx]["bond"][
                            "bondtype"
                        ],
                    )
                    parsed_bonds.append(bond)
            residue = ParsedResidue(
                name="U",
                type=const.token_ids[const.unk_token["PROTEIN"]],
                idx=idx,
                atoms=parsed_atoms,
                bonds=parsed_bonds,
                orig_idx=None,
                atom_center=0,
                atom_disto=0,
                is_standard=False,
                is_present=True,
            )
            residues.append(residue)
        chain_type = const.chain_type_ids["NONPOLYMER"]
        anchor_chain = ParsedChain(
            entity=0,
            residues=residues,
            res_design_mask=[False] * len(residues),
            type=const.chain_type_ids["NONPOLYMER"],
            cyclic_period=0,
            sequence=None,
        )
        anchor_atom_data = []
        anchor_bond_data = []
        anchor_res_data = []
        anchor_coords = []
        atom_idx = 0
        res_idx = 0
        # Add residue, atom, bond, data
        for res in anchor_chain.residues:
            atom_center = atom_idx + res.atom_center
            atom_disto = atom_idx + res.atom_disto
            anchor_res_data.append(
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
                atom_1 = atom_idx + bond.atom_1
                atom_2 = atom_idx + bond.atom_2
                anchor_bond_data.append(
                    (
                        asym_id,
                        asym_id,
                        res_idx,
                        res_idx,
                        atom_1,
                        atom_2,
                        bond.type,
                    )
                )

            for atom in res.atoms:
                # Add atom to data
                anchor_atom_data.append(
                    (atom.name, atom.coords, atom.is_present, 0.0, 1.0)
                )
                atom_idx += 1
                anchor_coords.append(atom.coords)
                charge_info.append(atom.charge)
            res_idx += 1
        anchor_chain = np.array(
            [
                (
                    "A",
                    const.chain_type_ids["NONPOLYMER"],
                    0,
                    0,
                    0,
                    0,
                    len(anchor_atom_data),
                    0,
                    len(anchor_chain.residues),
                    0,
                )
            ],
            dtype=Chain,
        )
        anchor_mask = np.concatenate([anchor_mask, np.ones(anchor_chain[0]["res_num"])])
        res_design_mask = np.concatenate(
            [res_design_mask, np.zeros(anchor_chain[0]["res_num"])]
        )
        res_bind_type = np.concatenate(
            [
                res_bind_type,
                [const.binding_type_ids["NOT_BINDING"]] * anchor_chain[0]["res_num"],
            ]
        )
        ss_type = np.concatenate(
            [ss_type, [const.ss_type_ids["UNSPECIFIED"]] * anchor_chain[0]["res_num"]]
        )
        structure_groups = np.concatenate(
            [
                structure_groups,
                [item[entity_type]["structure_group"]] * anchor_chain[0]["res_num"],
            ]
        )
        anchor_atom_to_res_idx = []
        token_to_res = []
        anchor_residues = np.array(anchor_res_data, dtype=Residue)
        for res_idx, res in enumerate(anchor_residues):
            anchor_atom_to_res_idx.extend([res_idx] * res["atom_num"])
        anchor_atoms = np.array(anchor_atom_data, dtype=Atom)
        anchor_tokens = []
        for idx, atom in enumerate(anchor_atoms):
            anchor_token = TokenData(
                token_idx=idx,
                atom_idx=idx,
                atom_num=1,
                res_idx=anchor_atom_to_res_idx[idx],
                res_type=const.token_ids[const.unk_token["PROTEIN"]],
                res_name=const.unk_token["PROTEIN"],
                sym_id=0,
                asym_id=0,
                entity_id=0,
                mol_type=const.chain_type_ids["NONPOLYMER"],
                center_idx=idx,
                disto_idx=idx,
                center_coords=atom["coords"],
                disto_coords=atom["coords"],
                resolved_mask=True,
                disto_mask=True,
                modified=False,
                frame_rot=np.eye(3).flatten(),
                frame_t=np.zeros(3),
                frame_mask=False,
                min_dist_ligand=0,
                cyclic_period=0,
                is_standard=False,
                design=False,
                binding_type=const.binding_type_ids["UNSPECIFIED"],
                structure_group=item[entity_type]["structure_group"],
                ccd=0,
                target_msa_mask=0,
                design_ss_mask=0,
                feature_asym_id=0,
                feature_res_idx=idx,
                is_anchor=1,
                anchor_parent_idx=1,
            )
            anchor_tokens.append(astuple(anchor_token))
        anchor_tokens = np.array(anchor_tokens, dtype=Token)
        anchor_structure = Structure(
            atoms=anchor_atoms,
            bonds=np.array(anchor_bond_data, dtype=Bond),
            residues=np.array(anchor_res_data, dtype=Residue),
            chains=anchor_chain,
            interfaces=np.array([], dtype=Interface),
            mask=np.ones(1, dtype=bool),
            coords=np.array(
                [(coord,) for coord in anchor_coords], dtype=structure.coords.dtype
            ),
            ensemble=np.array([(0, len(anchor_coords))], dtype=Ensemble),
        )

        anchor_data = {
            "structure": anchor_structure,
            "tokens": anchor_tokens,
            "structure_group": item[entity_type]["structure_group"],
            "charge_info": charge_info,
            "token_to_res": np.array(anchor_atom_to_res_idx, dtype=np.int32),
        }
        num_anchor += 1
    # Create metadata
    struct_info = StructureInfo(num_chains=len(data.chains))
    chain_infos = []
    for chain in data.chains:
        chain_info = ChainInfo(
            chain_id=int(chain["asym_id"]),
            chain_name=chain["name"],
            mol_type=int(chain["mol_type"]),
            cluster_id=-1,
            msa_id=chain_to_msa[chain["name"]],
            num_residues=int(chain["res_num"]),
            valid=True,
            entity_id=int(chain["entity_id"]),
        )
        chain_infos.append(chain_info)
    record = Record(
        id=name,
        structure=struct_info,
        chains=chain_infos,
        interfaces=[],
    )

    design_info = DesignInfo(
        res_design_mask=res_design_mask,
        res_structure_groups=structure_groups,
        res_binding_type=res_bind_type,
        res_ss_types=ss_type,
        res_anchor_mask=anchor_mask,
    )
    DesignInfo.is_valid(design_info)
    if num_anchor > 0:
        return Target(
            record=record,
            structure=data,
            design_info=design_info,
            sequences=entity_to_seq,
            extra_mols=extra_mols,
            anchor_data=anchor_data,
        )
    else:
        return Target(
            record=record,
            structure=data,
            design_info=design_info,
            sequences=entity_to_seq,
            extra_mols=extra_mols,
        )


def parse_yaml(
    path: Path,
    mols: dict[str, Mol],
    mol_dir: Path,
) -> Target:
    """Parse a Boltz input yaml / json.

    The input file should be a yaml file with the following format:

    sequences:
        - protein:
            id: A
            sequence: "MADQLTEEQIAEFKEAFSLF"
        - protein:
            id: [B, C]
            sequence: "AKLSILPWGHC"
        - rna:
            id: D
            sequence: "GCAUAGC"
        - ligand:
            id: E
            smiles: "CC1=CC=CC=C1"
        - ligand:
            id: [F, G]
            ccd: []
    constraints:
        - bond:
            atom1: [A, 1, CA]
            atom2: [A, 2, N]
    templates:
        - path: /path/to/template.pdb
          ids: [A] # optional, specify which chains to template

    version: 1

    Parameters
    ----------
    path : Path
        Path to the YAML input format.
    components : Dict
        Dictionary of CCD components.

    Returns
    -------
    Target
        The parsed target.

    """
    with path.open("r") as file:
        data = yaml.safe_load(file)

    name = path.stem
    return parse_boltz_schema(name, data, mols, mol_dir)
