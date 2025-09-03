import pickle
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import mdtraj as md
import numpy as np
from Bio import Align
from rdkit.Chem import AllChem, MolStandardize
from rdkit.Chem.rdchem import Mol

from foldeverything.data import const
from foldeverything.data.data import (
    Atom,
    Bond,
    Chain,
    Coords,
    Ensemble,
    Residue,
    Structure,
)
from foldeverything.data.md_sampling.md_sampler import MDSampler
from foldeverything.data.parse.mmcif import (
    ParsedBond,
    ParsedChain,
    ParsedResidue,
    compute_interfaces,
    get_conformer,
    get_mol,
)
from foldeverything.task.process.process import Resource

####################################################################################################
# Class definitions
####################################################################################################

DEBUG = False

class MDCoarseFullAtomParser(ABC):
    """A coarse-grained MD parser interface.

    Takes coarse-grained MD data and outputs a coordinate matrix and topology.

    """

    def __init__(
        self,
        working_dir: str,
        timeout: int = 15,
        patience: int = 4,
        pdb_fixer_threads: int = 1,
    ) -> None:
        """Initialize the coarse-grained MD parser."""
        super().__init__()
        self.working_dir = Path(working_dir)
        self.working_dir.mkdir(parents=True, exist_ok=True)
        self.timeout = timeout
        self.patience = patience
        self.pdb_fixer_threads = pdb_fixer_threads

    @abstractmethod
    def parse(
        self, trajectory: md.Trajectory, name: str
    ) -> Tuple[np.ndarray, md.Topology]:
        """Parse the coarse-grained MD data.

        Returns
        -------
        Tuple[np.ndarray, md.Topology]
            The coordinate matrix and the topology.

        """
        raise NotImplementedError


class MDrawParser(ABC):
    """A raw MD parser interface.

    Takes raw MD data in multiple formats and outputs the a coordinate matrix and
    topology.

    """

    def __init__(self, md_sampler: MDSampler) -> None:
        """Initialize the raw MD parser."""
        super().__init__()
        self.md_sampler = md_sampler

    @abstractmethod
    def parse(self) -> Tuple[np.ndarray, md.Topology]:
        """Parse the raw MD data.

        Returns
        -------
        Tuple[np.ndarray, md.Topology]
            The coordinate matrix, the topology.

        """
        raise NotImplementedError


@dataclass(frozen=True, slots=True)
class ParsedAtom:
    """A parsed atom object."""

    name: str
    coords: Tuple[float, float, float]
    is_present: bool
    topology_idx: int
    bfactor: int


####################################################################################################
# Helper functions
####################################################################################################


def next_label(label):
    """Generate the next lexicographical string in a base-26 system."""
    if not label:
        return "A"

    label = list(label)  # Convert string to list of characters
    i = len(label) - 1

    while i >= 0:
        if label[i] != "Z":  # Increment current character
            label[i] = chr(ord(label[i]) + 1)
            return "".join(label)
        label[i] = "A"  # Reset to 'A' if it was 'Z'
        i -= 1

    return "A" + "".join(label)  # Prepend 'A' if all were 'Z'


def find_first_missing(existing_labels):
    """Find the first missing string by checking gaps in lexicographical order."""
    current = "A"
    while current in existing_labels:
        current = next_label(current)  # Generate the next lexicographical string
    return current


def find_non_overlapping_chains(
        md_chains_info: List[Dict[str, Any]],
        reference_seq: str,
        chain_counter: int
    ):
    """Identify non-overlapping chains that are substrings of the reference."""
    # Find positions of chains as substrings
    last_start = 0
    last_end = -1
    for c_info in md_chains_info:
        seq = c_info["seq_md"]
        if seq in reference_seq:
            start_pos = reference_seq.index(seq)

            if start_pos < last_start:
                chain_counter += 1
            if start_pos < last_end:
                chain_counter += 1
                print("Warning: start_pos > last_end, 'Overlapping chains detected.'")
                # assert start_pos > last_end, "Overlapping chains detected."

            last_start = start_pos
            last_end = start_pos + len(seq)
            c_info["start_pos"] = start_pos
            c_info["end_pos"] = last_end
            c_info["old_chain_id"] = c_info["chain_md"].index
            c_info["new_chain_id"] = chain_counter
        else:
            msg = "MD chain sequence not found in reference sequence."
            raise AssertionError(msg)

    return chain_counter + 1


def merge_chains(topology: md.Topology, chain_matching_data):
    # Group chains by entity_id
    entity_chains = defaultdict(list)
    references = {}
    mappings = {}
    for c_info in chain_matching_data:
        entity_id = c_info["entity_id"]
        entity_chains[entity_id].append(
            {"chain_md": c_info["chain_md"], "seq_md": c_info["seq_md"]}
        )
        if entity_id in references:
            assert references[entity_id] == c_info["ref_seq"], (
                "Different reference sequences for the same entity_id."
            )
        references[entity_id] = c_info["ref_seq"]

    if DEBUG:
        for k,v in entity_chains.items():
            print(k, v)

    # Find non-overlapping chains for each entity
    chain_counter = 0
    for entity_id, c_info_list in entity_chains.items():
        chain_counter = find_non_overlapping_chains(
            c_info_list, references[entity_id], chain_counter
        ) # entity_chains[entity_id] =
        for c_info in entity_chains[entity_id]:
            if c_info["old_chain_id"] in mappings:
                assert False
            mappings[c_info["old_chain_id"]] = c_info["new_chain_id"]

    if DEBUG:
        print("mappings", mappings)

    # Convert topology to dataframe
    df, bonds = topology.to_dataframe()

    # Map chains
    df["chainID"] = df["chainID"].apply(lambda x: mappings[x])

    # Create new topology and assign it
    new_top = md.Topology.from_dataframe(df, bonds)
    return new_top


def align_helper(aligner, rcsb_seqs, rcsb_struct_path, chain_md, chain_info, local_alg):
    best_score = float("-inf")
    info = None
    pattern = ""
    alignments = None
    for mol_type, items in chain_info.items():
        mol_type = int(mol_type)
        if DEBUG: print("\n\nMol type = ", mol_type)
        if items is not None:
            for item in items:
                entity_id = int(item["entity_id"])
                entity_name = item["entity_name"]
                subchains = item["subchains"]
                seq_rcsb = item["seq"]

                if mol_type != const.chain_type_ids["NONPOLYMER"]:
                    try:
                        # Attempt to parse as polymer
                        if DEBUG: print("  Parsing md as polymer.")
                        seq_md = "".join(
                            [
                                const.prot_token_to_letter[res.name]
                                for res in chain_md.residues
                            ]
                        )
                    except KeyError:
                        # MD chain is likely not a polymer and mol_type is polymer so not a good match
                        if DEBUG: print("  SKIP")
                        continue
                else:
                    if local_alg:
                        # Local alignment only works for polymer chains
                        continue
                    if DEBUG: print("Parsing as nonpolymer")
                    seq_md = "_".join([res.name for res in chain_md.residues])

                seq_rcsb = str(seq_rcsb)
                if rcsb_struct_path is not None:
                    try:
                        seq_struct = rcsb_seqs[(entity_id, mol_type)]
                        score_struct = aligner.score(seq_struct, seq_md) / len(seq_md)
                    except KeyError:
                        rcsb_struct_path = None
                        score_struct = -1
                else:
                    score_struct = -1
                score_rcsb = aligner.score(seq_rcsb, seq_md) / len(seq_md)
                if DEBUG:
                    print("---")
                    print("  Seq MD      =", seq_md)
                    print("  Seq RCSB    =", seq_rcsb)
                if rcsb_struct_path is not None:
                    if DEBUG: print("  Seq Struct  =", seq_struct)
                if DEBUG:
                    print("  score_rcsb   ", score_rcsb, score_rcsb > best_score)
                    print("  score_struct ", score_struct, score_struct > best_score)
                if score_rcsb > best_score or score_struct > best_score:
                    if DEBUG: print("  Updating score")
                    best_score = max(score_rcsb, score_struct)

                    # Compute mapping between best matching sequence and the MD sequence
                    alignments = aligner.align(seq_rcsb, seq_md)
                    if DEBUG: print("  ", alignments)
                    pattern = ""
                    if not local_alg:
                        assert len(alignments[0][0]) == len(alignments[0][1])
                    for idx, (c1, c2) in enumerate(
                        zip(alignments[0][0], alignments[0][1])
                    ):
                        if c1 == c2:
                            c = "|"
                        elif c1 == "-" or c2 == "-":
                            c = "-"
                        else:  # noqa: PLR5501
                            # Some reference RCSB sequences have X instead of M
                            # We correct this here.
                            if c1 == "X" and c2 == "M":
                                c = "|"
                                target_pos = alignments[0].inverse_indices[0][idx]
                                assert seq_rcsb[target_pos] == "X", (
                                    "Indexing error for X->M correction"
                                )
                                seq_rcsb = (
                                    seq_rcsb[:target_pos]
                                    + "M"
                                    + seq_rcsb[target_pos + 1 :]
                                )
                            else:
                                c = "."  # Mismatch
                        pattern += c

                    if local_alg:
                        # Extract start and end of aligned region
                        best_alignment = alignments[0]
                        target_start = best_alignment.coordinates[0][0]
                        target_end = best_alignment.coordinates[0][-1]

                        # Insert gaps for unmatched regions before/after
                        pattern = (
                            "-" * target_start
                            + pattern
                            + "-" * (len(seq_rcsb) - target_end)
                        )

                    info = (
                        mol_type,
                        entity_id,
                        entity_name,
                        subchains,
                        pattern,
                        seq_rcsb,
                        seq_md,
                    )
                    if DEBUG: print("  info", info)
    return best_score, pattern, info, alignments


def detect_chain_type(
    chain_md,
    chain_info,
    rcsb_struct_path=None,
    match_th=0.95,
    local_alg=False,
):
    # print("\n\n\n\n\n\n\n\nNew detect_chain_type")

    # Load RCSB structure
    rcsb_seqs = {}
    if rcsb_struct_path is not None:
        structure_rcsb = Structure(**np.load(rcsb_struct_path))
        for chain in structure_rcsb.chains:
            # We rename the chains in alphabetical order
            mol_type = int(chain["mol_type"])
            entity_id = int(chain["entity_id"])
            res_start = chain["res_idx"]
            res_end = chain["res_idx"] + chain["res_num"]
            residues = structure_rcsb.residues[res_start:res_end]
            if mol_type == const.chain_type_ids["PROTEIN"]:
                try:
                    seq_struct = "".join(
                        [
                            const.prot_token_to_letter[res["name"]]
                            for res in residues
                            if res["is_present"]
                        ]
                    )
                except KeyError:
                    # Failed to parse as polymer, ignore RCSB structure
                    rcsb_struct_path = None
                    break
            elif mol_type == const.chain_type_ids["DNA"]:
                try:
                    seq_struct = "".join(
                        [
                            const.dna_token_to_letter[res["name"]]
                            for res in residues
                            if res["is_present"]
                        ]
                    )
                except KeyError:
                    # Failed to parse as DNA, ignore RCSB structure
                    rcsb_struct_path = None
                    break
            elif mol_type == const.chain_type_ids["RNA"]:
                try:
                    seq_struct = "".join(
                        [
                            const.rna_token_to_letter[res["name"]]
                            for res in residues
                            if res["is_present"]
                        ]
                    )
                except KeyError:
                    # Failed to parse as RNA, ignore RCSB structure
                    rcsb_struct_path = None
                    break
            else:
                seq_struct = "_".join(
                    [res["name"] for res in residues if res["is_present"]]
                )
            rcsb_seqs[(entity_id, mol_type)] = seq_struct
        if DEBUG: print("rcsb_seqs", rcsb_seqs)

    aligner = Align.PairwiseAligner(
        scoring="blastp",
        match_score=1.0,
        mismatch_score=-1,
        open_gap_score=-1,
        extend_gap_score=-1,
    )
    modes = ["local", "global"]
    if local_alg:
        modes = ["local"]

    # Attempt local alignment first
    found_match = False
    for mode in modes:
        aligner.mode = mode

        if DEBUG: print("Running mode", mode)
        best_score, pattern, info, alignments = align_helper(
            aligner=aligner,
            rcsb_seqs=rcsb_seqs,
            rcsb_struct_path=rcsb_struct_path,
            chain_md=chain_md,
            chain_info=chain_info,
            local_alg=mode == "local",
        )
        if DEBUG: print("best_score", best_score, mode)

        # If only running local alignment, we either find a match or not and return
        if local_alg:
            if best_score >= match_th:
                found_match = True
        elif mode == "local":
            if DEBUG: print("local 1", best_score, best_score == 1.0)
            if best_score == 1.0:
                # If perfect local match, we can skip global alignment
                # Return the best match
                found_match = True
                break

            # Did not find a perfect match, try global alignment
            if DEBUG: print("Attempting global alignment")
            continue
        elif best_score >= match_th:
            found_match = True

    if found_match:
        if DEBUG:
            print("pattern", pattern)
            print("best_score", best_score)
            print(alignments[0])
        return info

    if alignments is not None:
        if DEBUG: print(alignments[0])

    msg = "MD sequence does not match any of the correspoding PDB sequences."
    raise AssertionError(msg)


def make_tables(chains, md_coords, topology, entity_ids) -> Structure:
    # Create tables
    atom_data = []
    bond_data = []
    res_data = []
    chain_data = []
    topo_atom_idxs = []

    # Map indices in topology file to indices in our atom table
    atom_mapper = {}
    chain_to_seq = {}

    # Convert parsed chains to tables
    atom_idx = 0
    res_idx = 0
    sym_count = {}
    chain_to_idx = {}
    res_to_idx = {}

    for asym_id, chain in enumerate(chains):
        # Compute number of atoms and residues
        res_num = len(chain.residues)
        atom_num = sum(len(res.atoms) for res in chain.residues)

        entity_id = entity_ids[chain.name]
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
            res_to_idx[(chain.name, i)] = (res_idx, atom_idx)

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
                        1.0,  # plddt is 1 for MD
                    )
                )
                atom_mapper[atom.topology_idx] = atom_idx
                topo_atom_idxs.append(atom.topology_idx)
                atom_idx += 1

            res_idx += 1

    # Rearange md_coords and sample frames uniformly across trajectory and replicates
    topo_atom_idxs = np.array(topo_atom_idxs)

    # Replica stuff handled in MDRawParsers
    """
    # Only select replicas
    if replica_masks is not None:
        # Only select certain frames within replicas
        md_coords = md_coords[
            replica_masks, :, :
        ]  # combines replicas and frames into single dimension
        md_coords = md_coords[:, topo_atom_idxs, :]
    else:
        md_coords = md_coords[:, :, topo_atom_idxs, :]
        md_coords = md_coords.reshape(
            -1, len(topo_atom_idxs), 3
        )  # combines replicas and frames into single dimension
    """
    msg = "Multiple replicas not supported."
    assert md_coords.shape[0] == 1, msg
    num_samples = md_coords.shape[1]

    # Order atom table by topology, combine replicas and frames into single dimension
    md_coords = md_coords[:, :, topo_atom_idxs, :].reshape(-1, 3)

    # Sampling moved to MDRawParsers
    # num_samples = min(num_samples, md_coords.shape[0])
    # rng = np.random.default_rng()
    # sampled_indices = rng.choice(md_coords.shape[0], num_samples, replace=False)
    # coords_data = [(x,) for x in md_coords[sampled_indices].reshape(-1, 3)]
    coords_data = [(x,) for x in md_coords]

    # Create ensemble data
    ensemble_data = [(e_idx * atom_idx, atom_idx) for e_idx in range(num_samples)]

    # Make numpy arrays
    atoms = np.array(atom_data, dtype=Atom)
    bonds = np.array(bond_data, dtype=Bond)
    residues = np.array(res_data, dtype=Residue)
    chains = np.array(chain_data, dtype=Chain)
    mask = np.ones(len(chain_data), dtype=bool)
    ensemble = np.array(ensemble_data, dtype=Ensemble)
    coords = np.array(coords_data, dtype=Coords)

    # Compute interface chains (find chains with a heavy atom within 5A)
    interfaces = compute_interfaces(atoms, chains)

    """
    # Bond data
    bond_data = []
    for bond in topology.bonds:
        print(bond)
        if bond[0].index in atom_mapper and bond[1].index in atom_mapper:
            idx1, idx2 = atom_mapper[bond[0].index], atom_mapper[bond[1].index]
            unk_bond = const.bond_type_ids[const.unk_bond_type]
            print(bond.type, bond.order)
            if bond.type is None:
                bond_type = unk_bond
            else:
                print("bond.type", bond.type)
                bond_type = const.bond_type_ids.get(bond.type, unk_bond)
                print("bond_type", bond_type)
            bond_data.append((idx1, idx2, bond_type))
        else:
            print(" Bond not found")
    """

    # Return parsed structure
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


def mol_to_pdb(mol: md.core.topology.Residue, coords) -> str:
    """Dump a molecule to a PDB string.

    Parameters
    ----------
    mol : gemmi.Residue
        The molecule to dump.

    Returns
    -------
    str
        The output PDB string.

    """
    pdb_lines = ["PARENT N/A", "MODEL     1"]
    for i, atom in enumerate(mol.atoms):
        # PDB is a columnar format, every space matters here!
        index = atom.index
        atom_line = (
            f"{'HETATM':<6}{i + 1:>5} {atom.name:<4}{'':>1}"
            f"{'PDB':>3} {'A':>1}"
            f"{1:>4}{'':>1}   "
            f"{coords[0, 0, index, 0]:>8.3f}{coords[0, 0, index, 1]:>8.3f}{coords[0, 0, index, 2]:>8.3f}"
            f"{1.00:>6.2f}{0.00:>6.2f}          "
            f"{atom.element.name.upper():>2}{'':>2}"
        )
        pdb_lines.append(atom_line)

    pdb_lines.extend(["ENDMDL", "END"])
    pdb_lines = [line.ljust(80) for line in pdb_lines]
    pdb_string = "\n".join(pdb_lines) + "\n"
    return pdb_string


def match_template(
    mol: md.core.topology.Residue, template: Mol, coords
) -> Optional[Mol]:  # noqa: PLR0912
    """Match a Gemmi PDB molecule onto an RDkit tempalte.

    Inspired by Neural-plexer:
    github.com/zrqiao/NeuralPLexer/blob/main/neuralplexer/data/pdb_ligand_parsing.py

    Parameters
    ----------
    mol : gemmi.Residue
        The gemmi molecule to match.
    template : Mol
        The RDKit template to match.

    Returns
    -------
    Mol, optional
        The matched molecule.

    """
    # Create fake PDB of molecule
    pdb_string = mol_to_pdb(mol, coords)

    # print("pdb_string", pdb_string)

    # Use RDKit to get the right bond ordering
    new_mol = None

    # Try to parse the PDB
    try:
        rd_mol = AllChem.MolFromPDBBlock(pdb_string, proximityBonding=True)
        new_mol = AllChem.AssignBondOrdersFromTemplate(template, rd_mol)
    except Exception:  # noqa: S110, BLE001
        pass
    if new_mol is None:
        try:
            # Attempt without sanitization
            rd_mol = AllChem.MolFromPDBBlock(pdb_string, sanitize=False)
            new_mol = AllChem.AssignBondOrdersFromTemplate(template, rd_mol)
        except Exception:  # noqa: S110, BLE001
            pass
    if new_mol is None:
        try:
            # Attempt uncharging
            rd_mol = AllChem.MolFromPDBBlock(pdb_string, proximityBonding=True)
            uncharger = MolStandardize.rdMolStandardize.Uncharger()
            rd_mol = uncharger.uncharge(rd_mol)
            template = uncharger.uncharge(mol)
            new_mol = AllChem.AssignBondOrdersFromTemplate(template, rd_mol)
        except Exception:  # noqa: S110, BLE001
            pass
    if new_mol is None:
        try:
            # Retry parsing without proximity bondings
            rd_mol = AllChem.MolFromPDBBlock(pdb_string, proximityBonding=False)
            new_mol = AllChem.AssignBondOrdersFromTemplate(template, rd_mol)
        except Exception:  # noqa: S110, BLE001
            pass
    if new_mol is None:
        try:
            # Fallback to simple SMILES identity checkings
            rd_mol = AllChem.MolFromPDBBlock(pdb_string)
            new_mol = uncharger.uncharge(rd_mol)
            template = uncharger.uncharge(template)
            assert AllChem.MolToSmiles(new_mol) == AllChem.MolToSmiles(template)
        except Exception:  # noqa: S110, BLE001
            pass

    return new_mol


def get_atom_rmsf(coord_matrix, index):
    coords_pos = coord_matrix[0, :, index, :]
    mean_positions = np.mean(coords_pos, axis=0)
    bfactor = np.sqrt(np.mean((coords_pos - mean_positions) ** 2, axis=(0, 1)))
    return bfactor


def parse_ccd_residue(
    name: str,
    ref_mol: Mol,
    res_idx: int,
    coord_matrix,
    md_mol: Optional[md.core.topology.Residue] = None,
    atom_match_th: Optional[float] = 0.2,
    is_covalent: bool = False,
    atom_mask: Optional[np.ndarray] = None,
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
    md_mol : Optional[mdtraj.core.topology.Residue]
        The PDB molecule, as a gemmi Residue object, if any.

    Returns
    -------
    ParsedResidue, optional
       The output ParsedResidue, if successful.

    """
    # print("\n parse_ccd_residue", name)
    # print("md_mol", md_mol, md_mol.name)

    # Check if we have a PDB structure for this residue,
    # it could be a missing residue from the sequence
    is_present = md_mol is not None

    # Save original index (required for parsing connections)
    orig_idx = md_mol.index if is_present else None

    # Remove hydrogens
    ref_mol = AllChem.RemoveHs(ref_mol, sanitize=False)

    # Check if this is a single atom CCD residue
    if ref_mol.GetNumAtoms() == 1:
        pos = (0, 0, 0)
        ref_atom = ref_mol.GetAtoms()[0]
        index = 0
        bfactor = 0
        if is_present:
            # Get the index of the atom in the MD topology
            index = md_mol.atoms[0].index
            pos = tuple(coord_matrix[0, 0, index, :])

            # For MD, replace bfactor with RMSF. Assumes global alignment of frames.
            bfactor = get_atom_rmsf(coord_matrix, index)

        # Override is_present if MD parser masks this atom
        # Generally used when transforming coarsed grained to full atom
        # and want to ignore predicted all atoms
        if atom_mask is not None:
            is_present = is_present and atom_mask[index]

        atom = ParsedAtom(
            name=ref_atom.GetProp("name"),
            coords=pos,
            is_present=is_present,
            topology_idx=index,
            bfactor=bfactor,
        )
        unk_prot_id = const.unk_token_ids["PROTEIN"]
        residue = ParsedResidue(
            name=name,
            type=unk_prot_id,
            atoms=[atom],
            bonds=[],
            idx=res_idx,
            orig_idx=orig_idx,
            atom_center=0,  # Placeholder, no center
            atom_disto=0,  # Placeholder, no center
            is_standard=False,
            is_present=is_present,
        )
        return residue

    # Check if the reference molecule has the same heavy atoms as the MD molecule
    if is_present:
        ref_mol_atom_names = {
            atom.GetProp("name")
            for atom in ref_mol.GetAtoms()
            if atom.GetProp("name")[0] != "H"
        }
        md_mol_atom_names = {atom.name for atom in md_mol.atoms if atom.name[0] != "H"}
        diff = ref_mol_atom_names - md_mol_atom_names
        if len(diff) > 0:
            """
            # Try to match substructure

            new_mol = match_template(mol=md_mol, template=ref_mol, coords=coord_matrix)
            new_mol_atom_names = {atom.name for atom in new_mol.atoms if atom.name[0] != "H"}
            print("md_mol_atom_names", new_mol_atom_names)
            matches = ref_mol.GetSubstructMatch(new_mol)
            matches = {m: i for i, m in enumerate(matches)}
            print("matches", matches)
            if not matches:
                return None
            """

            # If more than threshold % of atoms are missing, skip
            if len(diff) / len(ref_mol_atom_names) > atom_match_th:
                print(f"Skipping CCD={name} as atom mismatch > {atom_match_th}.")
                return None

    # If multi-atom, start by getting the PDB coordinates
    pdb_pos = {}
    pdb_index = {}
    bfactor = {}
    if is_present:
        # Match atoms based on names
        for atom in md_mol.atoms:
            atom: md.core.topology.Atom
            index = atom.index
            pos = tuple(coord_matrix[0, 0, index, :])
            pdb_pos[atom.name] = pos
            pdb_index[atom.name] = index
            bfactor[atom.name] = get_atom_rmsf(coord_matrix, index)
    # print("pdb_pos", sorted(list(pdb_pos.keys())))

    # Parse each atom in order of the reference mol
    atoms = []
    atom_idx = 0
    idx_map = {}  # Used for bonds later

    for i, atom in enumerate(ref_mol.GetAtoms()):
        # Get atom name, charge, element and reference coordinates
        atom_name = atom.GetProp("name")

        # If the atom is a leaving atom, skip if not in the PDB and is_covalent
        if (
            atom.HasProp("leaving_atom")
            and int(atom.GetProp("leaving_atom")) == 1
            and is_covalent
            and (atom_name not in pdb_pos)
        ):
            continue

        # Get PDB coordinates, if any
        coords = pdb_pos.get(atom_name)
        topology_idx = pdb_index.get(atom_name)
        if coords is None:
            atom_is_present = False
            coords = (0, 0, 0)
            topology_idx = 0
            # raise AssertionError
        else:
            atom_is_present = True

        # Override is_present if MD parser masks this atom
        # Generally used when transforming coarsed grained to full atom
        # and want to ignore predicted all atoms
        if atom_mask is not None:
            atom_is_present = atom_is_present and atom_mask[topology_idx]

        # Add atom to list
        atoms.append(
            ParsedAtom(
                name=atom_name,
                coords=coords,
                is_present=atom_is_present,
                topology_idx=topology_idx,
                bfactor=bfactor.get(atom_name, 0),
            )
        )
        idx_map[i] = atom_idx
        atom_idx += 1

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
        orig_idx=orig_idx,
        is_standard=False,
        is_present=is_present,
    )


def parse_polymer(
    chain_name: str,
    entity_name: str,
    chain_md: md.core.topology.Chain,
    chain_type: int,
    coord_matrix: np.ndarray,
    mols: Resource,
    pattern: str,
    ref_seq: str,
    moldir: str,
    atom_match_th: Optional[float] = 0.2,
    atom_mask: Optional[np.ndarray] = None,
) -> ParsedChain:
    ref_res = set(const.tokens)

    md_residues = list(chain_md.residues)
    parsed = []
    i = 0
    for j, match in enumerate(pattern):

        # Get residue name from sequence
        if chain_type == const.chain_type_ids["PROTEIN"]:
            res_name = const.prot_letter_to_token[ref_seq[j]]
        elif chain_type == const.chain_type_ids["RNA"]:
            res_name = const.rna_letter_to_token[ref_seq[j]]
        elif chain_type == const.chain_type_ids["DNA"]:
            res_name = const.dna_letter_to_token[ref_seq[j]]
        else:
            raise ValueError("Unknown chain type.")

        # if DEBUG: print("\nj", j, ref_seq[j], res_name)

        # Check if we have a match in the structure
        res = None
        name_to_atom = {}

        if match == "|":
            # Get MD residue
            res = md_residues[i]
            # if DEBUG: print("res", res.name, res.index, i)
            name_to_atom = {a.name.upper(): a for a in res.atoms}

            # Double check the match
            if res_name != res.name:
                msg = f"Alignment mismatch! MD residue {res.name} does not match sequence residue {res_name}."
                raise ValueError(msg)

            # Increment polymer index
            i += 1
        # else:
        #    print("Skipping residue", res_name, i, j)

        # Map MSE to MET, put the selenium atom in the sulphur column
        if res_name == "MSE":
            res_name = "MET"
            if "SE" in name_to_atom:
                name_to_atom["SD"] = name_to_atom["SE"]

        # Handle non-standard residues
        elif res_name not in ref_res:
            # Try to parse as a ligand
            # print("parse_ccd_residue in polymer")
            modified_mol = get_mol(res_name, mols, moldir)
            if modified_mol is not None:
                residue = parse_ccd_residue(
                    name=res_name,
                    ref_mol=modified_mol,
                    res_idx=j,
                    md_mol=res,
                    coord_matrix=coord_matrix,
                    atom_match_th=atom_match_th,
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

            # Get coordinates from PDB
            if atom_name in name_to_atom:
                atom = name_to_atom[atom_name]
                index = atom.index
                atom_is_present = True
                coords = tuple(coord_matrix[0, 0, index, :])

                # For MD, replace bfactor with RMSF. Assumes global alignment of frames.
                bfactor = get_atom_rmsf(coord_matrix, index)
            else:
                atom_is_present = False
                coords = (0, 0, 0)
                # coords table will have nonzero coords at atom_is_present=False
                index = 0
                bfactor = 0

            # Override is_present if MD parser masks this atom
            # Generally used when transforming coarsed grained to full atom
            # and want to ignore predicted all atoms
            if atom_mask is not None:
                atom_is_present = atom_is_present and atom_mask[index]

            # Add atom to list
            atoms.append(
                ParsedAtom(
                    name=atom_name,
                    coords=coords,
                    is_present=atom_is_present,
                    topology_idx=index,
                    bfactor=bfactor,
                )
            )

        # Fix naming errors in arginine residues where NH2 is
        # incorrectly assigned to be closer to CD than NH1
        if (res is not None) and (res_name == "ARG"):
            ref_atoms: List[str] = const.ref_atoms["ARG"]
            cd = atoms[ref_atoms.index("CD")]
            nh1 = atoms[ref_atoms.index("NH1")]
            nh2 = atoms[ref_atoms.index("NH2")]

            cd_coords = np.array(cd.coords)
            nh1_coords = np.array(nh1.coords)
            nh2_coords = np.array(nh2.coords)

            if all(atom.is_present for atom in (cd, nh1, nh2)) and (
                np.linalg.norm(nh1_coords - cd_coords)
                > np.linalg.norm(nh2_coords - cd_coords)
            ):
                atoms[ref_atoms.index("NH1")] = replace(nh1, coords=nh2.coords)
                atoms[ref_atoms.index("NH2")] = replace(nh2, coords=nh1.coords)

        # Add residue to parsed list
        orig_idx = res.index if res is not None else None
        atom_center = const.res_to_center_atom_id[res_name]
        atom_disto = const.res_to_disto_atom_id[res_name]
        parsed.append(
            ParsedResidue(
                name=res_name,
                type=const.token_ids[res_name],
                atoms=atoms,
                bonds=[],
                idx=j,
                atom_center=atom_center,
                atom_disto=atom_disto,
                is_standard=True,
                is_present=res is not None,
                orig_idx=orig_idx,
            )
        )

    # Return polymer object
    chain_p = ParsedChain(
        name=chain_name,
        entity=entity_name,
        residues=parsed,
        type=chain_type,
        sequence=ref_seq,
    )

    return chain_p


def handle_chain_matchings(
    topology,
    chain_info,
    chain_type_map,
    rcsb_struct_path,
    chain_match_th,
    local_alg,
    get_subchain=True,
):
    chain_matching_data = []

    # Get chains from topology file
    chains_md = list(topology.chains)
    # print("There are", len(chains_md), "md chains")

    # Get chain info from RCSB
    max_entity_id_rcsb = 0
    all_entity_names_rcsb = set()
    all_subchains_rcsb = set()
    for items in chain_info.values():
        if items is not None:
            for item in items:
                entity_id = item["entity_id"]
                entity_name = item["entity_name"]
                subchains = item["subchains"].split(",")
                max_entity_id_rcsb = max(max_entity_id_rcsb, entity_id)
                all_entity_names_rcsb.add(entity_name)
                for subchain in subchains:
                    all_subchains_rcsb.add(subchain)

    def get_new_name(entity_id):
        # If we can treat the entity names as integers,
        # we can find the next available name easily
        all_entity_names_rcsb_int = set()
        for x in all_entity_names_rcsb:
            if x.isdigit():
                all_entity_names_rcsb_int.add(int(x))
            else:
                all_entity_names_rcsb_int = None
                break

        if all_entity_names_rcsb_int is not None:
            max_ = max(all_entity_names_rcsb_int)
            new_name = str(max_ + entity_id)
            return new_name
        else:
            i = 0
            while i < 99:
                name = f"{entity_id}_{i}"
                if name not in all_entity_names_rcsb:
                    return name
                i += 1
            raise AssertionError("Could not find a new name")

    entity_id_counter = {}  # counter for RCSB entities
    entity_ids_new_md = {}  # new entity ids for MD chains NOT matched to RCSB chains

    c_counter = 1  # new entity id counter for MD chains NOT matched to RCSB chains
    for chain_md in chains_md:
        # Check if we have metadata from the MD parser on how to match to RCSB
        if (
            chain_type_map is not None
            and chain_type_map.get((chain_md.index, chain_md.chain_id), None)
            is not None
        ):
            chain_md_meta = chain_type_map.get(
                (chain_md.index, chain_md.chain_id), None
            )
            if chain_md_meta["match_rcsb"]:
                # Detect chain type from chain sequence
                (
                    chain_type,
                    entity_id,
                    entity_name,
                    subchains,
                    pattern,
                    ref_seq,
                    seq_md,
                ) = detect_chain_type(
                    chain_md,
                    chain_info,  # from RCSB
                    rcsb_struct_path,
                    match_th=chain_match_th,
                    local_alg=local_alg,
                )
                idx = entity_id_counter.get(entity_id, 0)
                entity_id_counter[entity_id] = idx + 1
                chain_name = subchains.split(",")[idx]
            else:
                # We do not want to match this chain to an RCSB chain, treat as a
                # brand new chain. Only allowed if non polymer that does not need MSA.
                assert chain_md_meta["type"] == const.chain_type_ids["NONPOLYMER"]

                chain_type = const.chain_type_ids["NONPOLYMER"]

                # Get entity ID for this new MD chain
                entity_adjust = entity_ids_new_md.get(
                    chain_md_meta["entity_name"], c_counter
                )

                # Save the new entity id for this entity name
                entity_ids_new_md[chain_md_meta["entity_name"]] = entity_adjust

                # Set final entity ID for this new MD chain
                entity_id = max_entity_id_rcsb + entity_adjust

                # Get an entity name that is not in the RCSB data
                entity_name = get_new_name(entity_id)

                # Find next subchain name that is not in the RCSB data
                # Add subchain, as we want different chain name for each MD chain
                chain_name = find_first_missing(all_subchains_rcsb)
                all_subchains_rcsb.add(chain_name)

                # Increment counter for new MD chains
                c_counter += 1
        else:
            # Detect chain type from chain sequence
            chain_type, entity_id, entity_name, subchains, pattern, ref_seq, seq_md = (
                detect_chain_type(
                    chain_md,
                    chain_info,  # from RCSB
                    rcsb_struct_path,
                    match_th=chain_match_th,
                    local_alg=local_alg,
                )
            )
            idx = entity_id_counter.get(entity_id, 0)
            entity_id_counter[entity_id] = idx + 1
            # print("subchains", subchains)
            # print("idx", idx)

            chain_name = subchains.split(",")[idx] if get_subchain else None

        chain_matching_data.append(
            {
                "chain_md": chain_md,
                "chain_type": chain_type,
                "entity_id": entity_id,
                "entity_name": entity_name,
                "chain_name": chain_name,
                "pattern": pattern,
                "ref_seq": ref_seq,
                "seq_md": seq_md,
            }
        )

    return chain_matching_data


def parse_md(
    topology: md.Topology,
    coord_matrix: np.ndarray,
    mols: Resource,
    chain_info: Dict[str, Dict[str, Optional[str]]],
    chain_type_map: Dict,
    moldir: str,
    chain_match_th: Optional[float] = 0.95,
    atom_match_th: Optional[float] = 0.2,
    rcsb_struct_path: Optional[str] = None,
    local_alg: Optional[bool] = False,
    atom_mask: Optional[np.ndarray] = None,
) -> Structure:
    """Parse molecular dynamics data into ParsedStructure.

    Args:
        topology (md.Topology): The topology object.
        coord_matrix (np.ndarray): The coordinate matrix (duplicates, frames, atoms, 3).
        mols (Dict[str, Mol]): The components dictionary.
        atom_mask (np.ndarray): We might want to set certain present atoms as missing (in cg2all cases).

    Returns
    -------
        ParsedStructure: The parsed structure data.
    """
    chain_matching_data = handle_chain_matchings(
        topology,
        chain_info,
        chain_type_map,
        rcsb_struct_path,
        chain_match_th,
        local_alg,
        get_subchain=False,
    )

    # Merge chains with same entity ID
    if DEBUG: print("\n\n\n\n\n\n\n\nMerging chains with same entity ID")
    topology = merge_chains(topology, chain_matching_data)

    # Match chains again with new topology
    chain_matching_data = handle_chain_matchings(
        topology,
        chain_info,
        chain_type_map,
        rcsb_struct_path,
        chain_match_th,
        local_alg,
        get_subchain=True,
    )

    # Loop through topology chains and parse
    entity_ids = {}  # final entity ids mapping
    chains: List[ParsedChain] = []

    for c_data in chain_matching_data:
        chain_md = c_data["chain_md"]
        chain_type = c_data["chain_type"]
        entity_id = c_data["entity_id"]
        entity_name = c_data["entity_name"]
        chain_name = c_data["chain_name"]
        pattern = c_data["pattern"]
        ref_seq = c_data["ref_seq"]

        # Parse the chain depending on the type
        if (
            chain_type == const.chain_type_ids["PROTEIN"]
            or chain_type == const.chain_type_ids["DNA"]
            or chain_type == const.chain_type_ids["RNA"]
        ):
            chain_p = parse_polymer(
                chain_name,
                entity_name,
                chain_md,
                chain_type,
                coord_matrix,
                mols,
                pattern,
                ref_seq,
                moldir,
                atom_match_th,
                atom_mask,
            )

        elif chain_type == const.chain_type_ids["NONPOLYMER"]:
            # print("Parsing as nonpolymer")

            if any(lig.name == "UNL" for lig in chain_md.residues):
                print("Skipping as ligand names None found", chain_md.residues)
                for lig in chain_md.residues:
                    print(lig.name)
                continue

            is_covalent = (
                False  # TODO(mreveiz) MD doesnt have covalent info, how to handle this?
            )
            # Must change when adding datasets with covalents

            residues = []
            for lig_idx, ligand in enumerate(chain_md.residues):
                ligand: md.Residue
                ligand_mol = get_mol(ligand.name, mols, moldir)
                # print("ligand", ligand.name)
                residue = parse_ccd_residue(
                    name=ligand.name,
                    ref_mol=ligand_mol,
                    res_idx=lig_idx,
                    md_mol=ligand,
                    coord_matrix=coord_matrix,
                    atom_match_th=atom_match_th,
                    is_covalent=is_covalent,
                    atom_mask=atom_mask,
                )
                if residue is not None:
                    residues.append(residue)

            if residues:
                chain_p = ParsedChain(
                    name=chain_name,
                    entity=entity_id,
                    residues=residues,
                    type=chain_type,
                )
        else:
            raise AssertionError

        if chain_p is not None:
            chains.append(chain_p)
            entity_ids[chain_p.name] = entity_id

    return make_tables(chains, coord_matrix, topology, entity_ids)
