import os
import re
import subprocess
from collections.abc import MutableMapping
from os import PathLike
from pathlib import Path
import tempfile
from typing import Dict, List, Tuple, Union, Optional, Any

import gemmi
import numpy as np
import pandas as pd

# from minifold.utils.openfold import from_pdb_string, get_atom_coords_b, parse
from tqdm import tqdm

from rdkit import Chem
from rdkit.Chem import AllChem

import networkx as nx

import foldeverything
from foldeverything.complex import Complex
from foldeverything.types import Polymer, Protein, RNA, DNA, Ligand
from foldeverything.eval import qcp

complex_polymer_fields = ["proteins", "dnas", "rnas"]


def parse_matrix(matrix: str) -> Tuple[np.ndarray, np.ndarray]:
    """Parse the rotation matrix from the given string.

    Output looks like this:

    - The rotation matrix to rotate Structure_1 to Structure_2 -
    m  t[m]          u[m][0]       u[m][1]       u[m][2]
    0  0.000000000   1.000000000   0.000000000   0.000000000
    1  0.000000000  -0.000000000   1.000000000  -0.000000000
    2 -0.000000000  -0.000000000   0.000000000   1.000000000

    Code for rotating Structure 1 from (x,y,z) to (X,Y,Z):
    for(i=0; i<L; i++)
    {
    X[i] = t[0] + u[0][0]*x[i] + u[0][1]*y[i] + u[0][2]*z[i];
    Y[i] = t[1] + u[1][0]*x[i] + u[1][1]*y[i] + u[1][2]*z[i];
    Z[i] = t[2] + u[2][0]*x[i] + u[2][1]*y[i] + u[2][2]*z[i];
    }

    Parameters
    ----------
    matrix : str
        The string representation of the  USalign output

    Returns
    -------
    Tuple[np.ndarray, np.ndarray]
        A tuple containing the translation and the rotation

    """
    lines = matrix.strip().splitlines()
    lines = lines[1:4]
    R = np.zeros((3, 3))
    t = np.zeros(3)

    for i, line in enumerate(lines):
        values = line.strip().split()
        t[i] = float(values[1])
        R[i] = [float(value) for value in values[2:]]

    return t, R


def parse_USalign_output(output: str, mirror: bool = False) -> Dict:
    """Parse the output of the USalign tool.

    Parameters
    ----------
    output : str
        The string output of the USalign tool
    mirror : bool
        Whether the output is mirrored

    Returns
    -------
    Dict
        A dictionary containing the parsed output

    """
    # Split the output into groups (i.e chains)
    groups = output.strip().split("}")[:-1]

    # Parse each group
    output = {}
    for group in groups:
        # Parse sequences
        lines = group.strip().splitlines()
        if lines[0].startswith("There is no alignment"):
            continue

        p_seq = lines[1].strip()
        t_seq = lines[3].strip()
        p_chain = lines[0].split()[0].split(":")[-1].strip()
        t_chain = lines[2].split()[0].split(":")[-1].strip()
        tm = float(lines[2].split("TM-score=")[1].strip())
        L = re.search(r"L=(\d+)", lines[2])
        L = int(L.group(1)) if L else -1

        # If the query chain is the same as the target chain, assume they are supposed to match
        # Otherwise pick the alignment with the highest TM-score
        chains_match = p_chain == t_chain
        if not chains_match and t_chain in output:
            if not chains_match and tm < output[t_chain]["tm"]:
                continue

        # Parse transformation matrix
        matrix_str = "\n".join(lines[8:])
        t, R = parse_matrix(matrix_str)

        output[t_chain] = {
            "p_chain": p_chain,
            "t_chain": t_chain,
            "p_seq": p_seq,
            "t_seq": t_seq,
            "L": L,
            "t": t,
            "R": R,
            "tm": tm,
            "mirror": mirror,
        }

    return output


def polymer_to_gemmi_chain(polymer: Polymer) -> gemmi.Chain:
    chain = gemmi.Chain(polymer.chain)

    atom_to_element = lambda x: x[0]
    atom_types_ = polymer.atom_types()
    if isinstance(polymer, Protein):
        # atom_types_ = foldeverything.data.const.protein.atom_types
        residue_name_mapper = foldeverything.data.const.protein.restype_1to3
    elif isinstance(polymer, RNA) or isinstance(polymer, DNA):
        # atom_types_ = foldeverything.data.const.nucleic.atom_types
        residue_name_mapper = {
            x: x for x in foldeverything.data.const.nucleic.residue_atoms.keys()
        }
        if isinstance(polymer, DNA):
            residue_name_mapper.update({"A": "DA", "C": "DC", "G": "DG", "T": "DT"})
    else:
        raise ValueError(f"Invalid polymer type: {type(polymer)}")

    for i, (res_idx, res_coords, res_mask) in enumerate(
        zip(polymer.indices, polymer.coords, polymer.mask)
    ):
        res = gemmi.Residue()
        res.seqid = gemmi.SeqId(str(i))  # Set the residue sequence number
        res.name = residue_name_mapper[polymer.sequence[i]]
        for j, (atom_coords, atom_mask) in enumerate(zip(res_coords, res_mask)):
            atom_type = atom_types_[j]
            element = atom_to_element(atom_type)
            if atom_mask:
                atom = gemmi.Atom()
                atom.name = atom_type
                atom.element = gemmi.Element(element)
                if not isinstance(atom.element, int):
                    print(f"Invalid element: {atom.element}, not resulting in an int")
                atom.pos = gemmi.Position(*atom_coords)
                res.add_atom(atom)
        chain.add_residue(res)

    return chain


def ligand_to_gemmi_chain(ligand: Ligand, seq_id="1"):
    # Note that this won't include bond information
    chain = gemmi.Chain(ligand.chain)
    # Add a new hetero residue to the chain
    residue = gemmi.Residue()
    residue.name = ligand.name
    residue.seqid = gemmi.SeqId(str(seq_id))
    # https://gemmi.readthedocs.io/en/latest/mol.html#residue
    residue.entity_type = gemmi.EntityType.NonPolymer
    residue.het_flag = "H"
    # Loop through all atoms in the RDKit molecule
    mol = ligand.mol
    for atom in mol.GetAtoms():
        # Add each atom to the gemmi residue
        gatom = gemmi.Atom()
        gatom.name = atom.GetSymbol()
        gatom.element = gemmi.Element(atom.GetSymbol())
        if not isinstance(atom.element, int):
            print(f"Invalid element: {atom.element}, not resulting in an int")
        atom_coords = mol.GetConformer().GetAtomPosition(atom.GetIdx())
        gatom.pos = gemmi.Position(*atom_coords)
        residue.add_atom(gatom)

    chain.add_residue(residue)
    return chain


def build_gemmi_structure(fe_complex: Complex, model_num=1) -> gemmi.Structure:
    model = gemmi.Model(
        str(model_num)
    )  # model_num should be a number but needs to be a string
    polymer_type_dicts = [
        {
            "polymer_type": gemmi.PolymerType.PeptideL,
            "polymer_list": fe_complex.proteins,
            "residue_kind": gemmi.ResidueKind.AA,
        },
        {
            "polymer_type": gemmi.PolymerType.Dna,
            "polymer_list": fe_complex.dnas,
            "residue_kind": gemmi.ResidueKind.DNA,
        },
        {
            "polymer_type": gemmi.PolymerType.Rna,
            "polymer_list": fe_complex.rnas,
            "residue_kind": gemmi.ResidueKind.RNA,
        },
    ]

    result_dicts = []
    for polymer_type_dict in polymer_type_dicts:
        polymer_list = polymer_type_dict["polymer_list"]
        polymer_type = polymer_type_dict["polymer_type"]
        residue_kind = polymer_type_dict["residue_kind"]
        for polymer in polymer_list:
            sequence = polymer.sequence
            result_dicts.append(
                {
                    "sequence": sequence,
                    "residue_kind": residue_kind,
                    "polymer_type": polymer_type,
                }
            )
            chain = polymer_to_gemmi_chain(polymer)
            model.add_chain(chain)

    for ligand in fe_complex.ligands:
        chain = ligand_to_gemmi_chain(ligand)
        model.add_chain(chain)

    structure = gemmi.Structure()
    structure.add_model(model)

    # IMPORTANT!
    # https://gemmi.readthedocs.io/en/latest/mol.html#entity
    structure.setup_entities()
    structure.clear_sequences()
    for ii, seq_info in enumerate(result_dicts):
        seq, residue_kind = seq_info["sequence"], seq_info["residue_kind"]
        polymer_type = seq_info["polymer_type"]
        seq1 = gemmi.expand_one_letter_sequence(seq, residue_kind)
        structure.entities[ii].polymer_type = polymer_type
        structure.entities[ii].full_sequence = seq1

    return structure


def write_complex(fe_complex: Complex, path: str, output_format: str = None):
    """
    Write a complex to a file.
    Either PDB or mmCIF format is supported.
    """
    structure = build_gemmi_structure(fe_complex)
    if output_format is None:
        output_format = "pdb" if path.endswith(".pdb") else "mmcif"

    if output_format == "pdb":
        structure.write_pdb(path)
    elif output_format == "mmcif":
        structure.make_mmcif_document().write_file(path)
    else:
        raise ValueError(f"Invalid format: {output_format}")


def apply_transform_complex(
    fe_complex: Complex, R: np.ndarray, t: np.ndarray, mirror: bool = False
) -> Complex:
    """Apply the given transformation to the protein.

    Parameters
    ----------
    fe_complex : Complex
        The protein to transform
    R : np.ndarray
        The rotation matrix
    t : np.ndarray
        The translation vector
    mirror : bool, default False
        Whether to mirror the complex first

    Returns
    -------
    Complex
        A new Complex, with transformed coordinates. Other graph features are left empty.

    """
    # Apply the rotation and translation to the coordinates
    kwargs = {
        "resolution": fe_complex.resolution,
        "deposited": fe_complex.deposited,
        "revised": fe_complex.revised,
    }
    polymer_fields = complex_polymer_fields
    for field in polymer_fields:
        polymers = getattr(fe_complex, field)
        new_polymers = []
        for polymer in polymers:
            new_polymers.append(polymer.apply_transform(R, t, mirror=mirror))
        kwargs[field] = new_polymers

    # TODO Ligands
    kwargs["ligands"] = []
    return Complex(**kwargs)


def generate_conformer(mol):
    ps = AllChem.ETKDGv2()
    id = AllChem.EmbedMolecule(mol, ps)
    if id == -1:
        # print('rdkit coords could not be generated without using random coords. using random coords now.')
        ps.useRandomCoords = True
        AllChem.EmbedMolecule(mol, ps)
        AllChem.MMFFOptimizeMolecule(mol, confId=0)

    return id


def mol_to_props(mol):
    anums = [a.GetAtomicNum() for a in mol.GetAtoms()]
    num_atoms = len(anums)

    one_hot_anums = np.zeros((num_atoms, foldeverything.data.const.ligand.atomtype_num))
    one_hot_anums[np.arange(num_atoms), anums] = 1

    pos = mol.GetConformer().GetPositions()

    coords = np.zeros((num_atoms, 3))
    for i in range(num_atoms):
        coords[i] = pos[i]

    adj_matr = Chem.rdmolops.GetAdjacencyMatrix(mol, useBO=True)

    return coords, one_hot_anums, adj_matr


def one_hot_to_index(one_hot: np.ndarray, axis=-1) -> np.ndarray:
    """Convert a one-hot matrix to an index vector

    Parameters
    ----------
    one_hot : np.ndarray
        The one-hot vector
    axis : int, default -1
        Axis over which the matrix is one-hot

    Returns
    -------
    ndarray

    """
    return np.argmax(one_hot, axis=axis)


def center_of_geometry(coordinates: np.ndarray) -> np.ndarray:
    """
    Center of geometry.

    Parameters
    ----------
    coordinates: np.ndarray
        Coordinates

    Returns
    -------
    np.ndarray
        Center of geometry
    """

    assert coordinates.shape[1] == 3

    return np.mean(coordinates, axis=0)


def center_coords(coordinates: np.ndarray) -> np.ndarray:
    """
    Center coordinates.

    Parameters
    ----------
    coordinates: np.ndarray
        Coordinates

    Returns
    -------
    np.ndarray
        Centred coordinates
    """

    return coordinates - center_of_geometry(coordinates)


def rmsd_isomorphic_core(
    coords1: np.ndarray,
    coords2: np.ndarray,
    aprops1: np.ndarray,
    aprops2: np.ndarray,
    am1: np.ndarray,
    am2: np.ndarray,
    center: bool = False,
    minimize: bool = False,
    atol: float = 1e-9,
):
    """
    Compute RMSD using graph isomorphism.

    Parameters
    ----------
    coords1: np.ndarray
        Coordinate of molecule 1
    coords2: np.ndarray
        Coordinates of molecule 2
    aprops1: np.ndarray
        Atomic properties for molecule 1
    aprops2: np.ndarray
        Atomic properties for molecule 2
    am1: np.ndarray
        Adjacency matrix for molecule 1
    am2: np.ndarray
        Adjacency matrix for molecule 2
    center: bool
        Centering flag
    minimize: bool
        Compute minized RMSD
    atol: float
        Absolute tolerance parameter for QCP (see :func:`qcp_rmsd`)

    Returns
    -------
    float
        RMSD
    Tuple[List, List]
    """

    assert coords1.shape == coords2.shape

    n = coords1.shape[0]

    # Center coordinates if required
    c1 = center_coords(coords1) if center or minimize else coords1
    c2 = center_coords(coords2) if center or minimize else coords2

    # Convert molecules to graphs
    G1 = graph_from_adjacency_matrix(am1, aprops1)
    G2 = graph_from_adjacency_matrix(am2, aprops2)

    # Get all the possible graph isomorphisms
    isomorphisms = match_graphs(G1, G2)

    # Minimum result
    # Squared displacement (not minimize) or RMSD (minimize)
    min_result = np.inf
    min_isomorphisms = None

    # Loop over all graph isomorphisms to find the lowest RMSD
    for idx1, idx2 in isomorphisms:
        # Use the isomorphism to shuffle coordinates around (from original order)
        c1i = c1[idx1, :]
        c2i = c2[idx2, :]

        if not minimize:
            # Compute square displacement
            # Avoid dividing by n and an expensive sqrt() operation
            result = np.sum((c1i - c2i) ** 2)
        else:
            # Compute minimized RMSD using QCP
            result = qcp.qcp_rmsd(c1i, c2i, atol)

        if result < min_result:
            min_result = result
            min_isomorphisms = (idx1, idx2)

    if not minimize:
        # Compute actual RMSD from square displacement
        min_result = np.sqrt(min_result / n)

    # Return the actual RMSD
    return min_result, isomorphisms, min_isomorphisms


def graph_from_adjacency_matrix(
    adjacency_matrix: Union[np.ndarray, List[List[int]]],
    aprops: Optional[Union[np.ndarray, List[Any]]] = None,
) -> nx.Graph:
    """
    Graph from adjacency matrix.

    Parameters
    ----------
    adjacency_matrix: Union[np.ndarray, List[List[int]]]
        Adjacency matrix
    aprops: Union[np.ndarray, List[Any]], optional
        Atomic properties

    Returns
    -------
    Graph
        Molecular graph

    Notes
    -----
    It the atomic numbers are passed, they are used as node attributes.
    """

    G = nx.Graph(adjacency_matrix)

    if aprops is not None:
        attributes = {idx: aprops for idx, aprops in enumerate(aprops)}
        nx.set_node_attributes(G, attributes, "aprops")

    return G


def match_graphs(G1, G2) -> List[Tuple[List[int], List[int]]]:
    """
    Compute graph isomorphisms.

    Parameters
    ----------
    G1:
        Graph 1
    G2:
        Graph 2

    Returns
    -------
    List[Tuple[List[int],List[int]]]
        All possible mappings between nodes of graph 1 and graph 2 (isomorphisms)

    Raises
    ------
    NonIsomorphicGraphs
        If the graphs `G1` and `G2` are not isomorphic
    """

    def match_aprops(node1, node2):
        """
        Check if atomic properties for two nodes match.
        """
        return np.all(node1["aprops"] == node2["aprops"])

    if (
        nx.get_node_attributes(G1, "aprops") == {}
        or nx.get_node_attributes(G2, "aprops") == {}
    ):
        # Nodes without atomic number information
        # No node-matching check
        node_match = None

    else:
        node_match = match_aprops

    GM = nx.algorithms.isomorphism.GraphMatcher(G1, G2, node_match)

    return [
        (list(isomorphism.keys()), list(isomorphism.values()))
        for isomorphism in GM.isomorphisms_iter()
    ]
