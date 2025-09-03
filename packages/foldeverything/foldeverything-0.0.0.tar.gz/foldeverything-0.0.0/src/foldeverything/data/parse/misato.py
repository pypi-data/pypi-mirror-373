import pickle
from pathlib import Path
from typing import Dict, Tuple

import h5py
import mdtraj as md
import numpy as np
import torch
from moldf import read_mol2

from foldeverything.data.md_sampling.md_sampler import MDSampler
from foldeverything.data.parse.md import MDrawParser

"""MISATO, a database for protein-ligand interactions
    Copyright (C) 2023
                        Till Siebenmorgen  (till.siebenmorgen@helmholtz-munich.de)
                        Sabrina Benassou   (s.benassou@fz-juelich.de)
                        Filipe Menezes     (filipe.menezes@helmholtz-munich.de)
                        Erinç Merdivan     (erinc.merdivan@helmholtz-munich.de)

    This library is free software; you can redistribute it and/or
    modify it under the terms of the GNU Lesser General Public
    License as published by the Free Software Foundation; either
    version 2.1 of the License, or (at your option) any later version.

    This library is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
    Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public
    License along with this library; if not, write to the Free Software
    Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA"""


histidines = ["HSD", "HIS", "HIE", "HID", "HSE", "HSP"]

cysteines = ["CYX", "CYS"]


atomic_numbers_Map = {
    1: "H",
    5: "B",
    6: "C",
    7: "N",
    8: "O",
    9: "F",
    11: "Na",
    12: "Mg",
    13: "Al",
    14: "Si",
    15: "P",
    16: "S",
    17: "Cl",
    19: "K",
    20: "Ca",
    34: "Se",
    35: "Br",
    53: "I",
}


def get_maps(mapdir: Path) -> Tuple[dict, dict, dict]:
    """Load the maps.

    Args:
        mapdir: path to the maps
    """

    def load_pickle(file_path: Path) -> dict:
        with file_path.open("rb") as file:
            return pickle.load(file)  # noqa: S301

    residueMap = load_pickle(mapdir / "atoms_residue_map.pickle")
    typeMap = load_pickle(mapdir / "atoms_type_map.pickle")
    nameMap = load_pickle(mapdir / "atoms_name_map_for_pdb.pickle")
    return residueMap, typeMap, nameMap


def get_entries(struct, f, frame):
    """Get the entries of the hdf5 file.

    Args:
        struct: pdb code
        f: hdf5 file
        frame: frame of the trajectory
    """
    trajectory_coordinates = f.get(struct + "/" + "trajectory_coordinates")[frame]
    atoms_type = f.get(struct + "/" + "atoms_type")
    atoms_number = f.get(struct + "/" + "atoms_number")
    atoms_residue = f.get(struct + "/" + "atoms_residue")
    molecules_begin_atom_index = f.get(struct + "/" + "molecules_begin_atom_index")
    return (
        trajectory_coordinates,
        atoms_type,
        atoms_number,
        atoms_residue,
        molecules_begin_atom_index,
    )


def get_atom_name(
    i, atoms_number, residue_atom_index, residue_name, type_string, nameMap
):
    """Get the atom name.

    Args:
        i: atom index
        atoms_number: number of the atoms
        residue_atom_index: atom index within the residue
        residue_name: residue name
        type_string: type of the atom
        nameMap: dictionary
    """
    # print("residue_atom_index", residue_atom_index)
    if residue_name == "MOL":
        try:
            atom_name = atomic_numbers_Map[atoms_number[i]] + str(residue_atom_index)
        except KeyError:
            # print('KeyError', (residue_name, residue_atom_index-1, type_string))
            atom_name = atomic_numbers_Map[atoms_number[i]] + str(residue_atom_index)
    else:
        try:
            atom_name = nameMap[(residue_name, residue_atom_index - 1, type_string)]
        except KeyError:
            # print('KeyError', (residue_name, residue_atom_index-1, type_string))
            atom_name = atomic_numbers_Map[atoms_number[i]] + str(residue_atom_index)

    # Hydrogen atoms have long names (HH21) which get trimmed when read by md.traj. This causes duplicates
    # (HH21 == HH22) which resultsin mdtraj skipping atoms and misalinging the entire thing.
    # Since we don't care about hydrogens at all in Boltz, we just rename them to H1, H2, H3, etc.
    if atom_name[0] == "H":
        atom_name = atom_name[0] + str(residue_atom_index)
    return atom_name


def update_residue_indices(
    residue_number,
    i,
    type_string,
    atoms_type,
    atoms_residue,
    residue_name,
    residue_atom_index,
    residue_Map,
    typeMap,
):
    """If the atom sequence has O-N icnrease the residueNumber.

    Args:
        residue_number: residue number
        i: atom index
        type_string: type of the atom
        atoms_type: type of the atoms
        atoms_residue: residue of the atoms
        residue_name: residue name
        residue_atom_index: atom index within the residue
        residue_Map: dictionary
        typeMap: dictionary
    """
    if i < len(atoms_type) - 1:
        if (
            type_string[0] == "O" and typeMap[atoms_type[i + 1]][0] == "N"
        ):  # or residue_Map[atoms_residue[i+1]]=='MOL'
            # GLN and ASN have a O-N sequence within the AA. See nameMap (atoms_name_map_for_pdb.pickle)
            if not (
                (residue_name == "GLN" and residue_atom_index in [12, 14])
                or (residue_name == "ASN" and residue_atom_index in [9, 11])
            ):
                residue_number += 1
                residue_atom_index = 0
    return residue_number, residue_atom_index


def insert_TERS(
    i, molecules_begin_atom_index, residue_number, residue_atom_index, lines
):
    """Add TER line if the next atom is the first atom of a new molecule.

    Args:
        i: atom index
        molecules_begin_atom_index: list of atom indices where a new molecule starts
        residue_number: residue number
        residue_atom_index: atom index within the residue
        lines: list of pdb lines.
    """
    if i + 1 in molecules_begin_atom_index:
        lines.append("TER")
        residue_number += 1
        residue_atom_index = 0
    return residue_number, residue_atom_index, lines


def create_pdb_lines_MD(
    trajectory_coordinates,
    atoms_type,
    atoms_number,
    atoms_residue,
    molecules_begin_atom_index,
    typeMap,
    residue_Map,
    nameMap,
    ligand_code,
    is_mer,
    mol2,
):
    """Go through each atom line and bring the inputs in the pdb format.

    Args:
        trajectory_coordinates: coordinates of the atoms
        atoms_type: type of the atoms
        atoms_number: number of the atoms
        atoms_residue: residue of the atoms
        molecules_begin_atom_index: list of atom indices where a new molecule starts
        typeMap: dictionary of atom types
        residue_Map: dictionary of residue names
        nameMap: dictionary.

    """
    lines = []
    residue_number = 1
    residue_atom_index = 0
    mol_atom_idx = 0
    for i in range(len(atoms_type)):
        residue_atom_index += 1
        type_string = typeMap[atoms_type[i]]
        residue_name = residue_Map[atoms_residue[i]]

        if residue_name == "MOL":
            if is_mer:
                # This ligand is a polymer, but contains ambiguous residues
                # (a glycan attached to it, etc...) so we cannot continue.
                msg = "Cannot generate topology file for ambiguous ligand."
                raise ValueError(msg)
            else:
                # Replace unknown MOL residue with the ligand code
                residue_name = ligand_code

                atom_name_md = get_atom_name(
                    i,
                    atoms_number,
                    residue_atom_index,
                    residue_name,
                    type_string,
                    nameMap,
                )
                atom_name = mol2["atom_name"].iloc[mol_atom_idx]
                # print("   (mol)", i, atom_name_md, atom_name)
                assert atom_name_md[0] == atom_name[0], (
                    f"Atom name mismatch: {atom_name_md} != {atom_name}"
                )
                mol_atom_idx += 1
        else:
            atom_name = get_atom_name(
                i, atoms_number, residue_atom_index, residue_name, type_string, nameMap
            )

        x, y, z = (
            trajectory_coordinates[i][0],
            trajectory_coordinates[i][1],
            trajectory_coordinates[i][2],
        )
        fmt = "ATOM{0:7d}  {1:<4}{2:<4}{3:>5}    {4:8.3f}{5:8.3f}{6:8.3f}  1.00  0.00           {7:<5}"
        line = fmt.format(
            i + 1,
            atom_name,
            residue_name,
            residue_number,
            x,
            y,
            z,
            atomic_numbers_Map[atoms_number[i]],
        )
        residue_number, residue_atom_index = update_residue_indices(
            residue_number,
            i,
            type_string,
            atoms_type,
            atoms_residue,
            residue_name,
            residue_atom_index,
            residue_Map,
            typeMap,
        )
        lines.append(line)
        residue_number, residue_atom_index, lines = insert_TERS(
            i, molecules_begin_atom_index, residue_number, residue_atom_index, lines
        )
    return lines


def write_pdb(path_out, struct, specification, lines):
    """Write the pdb file.

    Args:
        struct: pdb code
        specification: specification of the pdb file
        lines: list of pdb lines.
    """
    with open(path_out + "/" + struct + specification + ".pdb", "w") as of:
        for line in lines:
            of.write(line + "\n")


class MISATO_RawMD(MDrawParser):  # noqa: N801
    """Parser for raw MD data from MISATO."""

    def __init__(
        self,
        md_sampler: MDSampler,
        map_dir: Path,
        path_temp: str,
        path_md_hdf5: Path,
        ligand_map: Dict[str, Tuple[str, bool]],
        mol2_dir: Path,
    ) -> None:
        """Initialize the raw MD parser."""
        super().__init__(md_sampler=md_sampler)

        # Get maps to decode hdf5 data
        residue_map, type_map, name_map = get_maps(map_dir)
        self.residue_map = residue_map
        self.type_map = type_map
        self.name_map = name_map

        # Folder to write topologies
        self.path_temp = path_temp

        # Folder with MD data
        self.path_md_hdf5 = path_md_hdf5

        # Mapping between PDB and ligand codes
        self.ligand_map = ligand_map

        # Atom names for ligands do not follow the standard naming scheme
        # We take the mol2 files to map the atom names to the PDB format
        self.mol2_dir = mol2_dir

    def parse(self, name: str) -> Tuple[np.ndarray, md.Topology]:  # noqa: C901, PLR0912, PLR0915
        """Parse the raw MD data.

        Returns
        -------
        Tuple[np.ndarray, md.Topology]
            The coordinate matrix and the topology.
        """
        if name.lower() not in self.ligand_map:
            msg = f"Could not find ligand information for {name}"
            raise ValueError(msg)
        ligand_code, is_mer = self.ligand_map[name.lower()]

        # Get mol2 file for ligand
        mol2_file = self.mol2_dir / f"{name.lower()}_ligand.mol2"
        mol2 = read_mol2(mol2_file)["ATOM"]

        with h5py.File(self.path_md_hdf5, "r") as f:
            frame = 0
            (
                trajectory_coordinates,
                atoms_type,
                atoms_number,
                atoms_residue,
                molecules_begin_atom_index,
            ) = get_entries(name, f, frame)

            lines = create_pdb_lines_MD(
                trajectory_coordinates,
                atoms_type,
                atoms_number,
                atoms_residue,
                molecules_begin_atom_index,
                self.type_map,
                self.residue_map,
                self.name_map,
                ligand_code,
                is_mer,
                mol2,
            )
            # Convert coords to (replicates, frames, atoms, 3)
            coord_matrix = f.get(name + "/" + "trajectory_coordinates")[:]

        # Load the topology and coordinates into trajectory
        write_pdb(self.path_temp, name, "_MD_frame" + str(frame), lines)

        pdb_obj = md.load_pdb(self.path_temp + name + "_MD_frame" + str(frame) + ".pdb")
        trajectory = md.Trajectory(
            coord_matrix, pdb_obj.topology
        )

        # Sample the trajectory
        trajectory = self.md_sampler.sample([trajectory])[0]

        # Convert aligned coords to (replicates, frames, atoms, 3)
        coord_matrix = trajectory.xyz[None]

        L = coord_matrix.shape[2]
        mol_index_mask = torch.zeros(L)
        atom_mask = np.ones(coord_matrix.shape[2], dtype=bool)
        with h5py.File(self.path_md_hdf5, "r") as f:
            frame = 0
            (
                trajectory_coordinates,
                atoms_type,
                atoms_number,
                atoms_residue,
                molecules_begin_atom_index,
            ) = get_entries(name, f, frame)

            i = 0
            for chain_md in trajectory.topology.chains:
                for res_md in chain_md.residues:
                    for atom_md in res_md.atoms:
                        symbol_raw = atomic_numbers_Map[atoms_number[i]]
                        residue_name_raw = self.residue_map[atoms_residue[i]]

                        # Make sure the atom names in the raw file match the parsed atom
                        # names from the written pdb
                        assert atom_md.element.symbol == symbol_raw[0]

                        # Make sur residue names match
                        if residue_name_raw != "MOL":
                            # Histidines have a different naming scheme in MD
                            if res_md.name in histidines:
                                assert residue_name_raw in histidines, (
                                    f"{residue_name_raw}, {res_md.name}"
                                )
                            # Cysteines have a different naming scheme in MD
                            # (disulfide bridge)
                            elif res_md.name in cysteines:
                                assert residue_name_raw in cysteines, (
                                    f"{residue_name_raw}, {res_md.name}"
                                )
                            else:
                                assert residue_name_raw == res_md.name, (
                                    f"{residue_name_raw}, {res_md.name}"
                                )
                            # print(atom_md.name, atom_md.element.symbol, symbol, atom_md.element.symbol == symbol[0])
                        else:
                            mol_index_mask[i] = 1

                        # Make sure the atom indices are consistent in md traj
                        assert atom_md.index == i
                        i += 1

            assert i == len(atoms_number), "Mismatch of atoms"

        # Some ligands in MISATO get way too far from the protein
        # So we filter them out
        if not is_mer:
            mol_index_mask = mol_index_mask.bool()

            # Compute pairwise distances between all atoms
            M = torch.Tensor(coord_matrix[0])
            distances = torch.cdist(M, M)  # (frames, atoms, atoms)
            sub_dist = distances[:, mol_index_mask, :][:, :, ~mol_index_mask]
            try:
                min_dists = sub_dist.min(dim=1).values.min(dim=1).values
            except:
                print(
                    "NO MOL HERE: ",
                    name,
                    coord_matrix.shape,
                    sub_dist.shape,
                    mol_index_mask.sum(),
                )
                assert False

            # If the minimum distance between the ligand and the protein is too large
            # we save it to manually check
            if min_dists[0] > 12:
                # Save trajectory
                print("Saving trajectory for", name)
                trajectory2 = md.Trajectory(coord_matrix[0], trajectory.topology)
                trajectory2.save(
                    "/afs/csail.mit.edu/u/m/mreveiz/"
                    + name
                    + "_MD_frame"
                    + str(frame)
                    + ".dcd"
                )

            if min_dists.max() > 12:
                trajectory2 = md.Trajectory(coord_matrix[0], trajectory.topology)
                trajectory2.save(
                    "/afs/csail.mit.edu/u/m/mreveiz/"
                    + name
                    + "_MD_frame"
                    + str(frame)
                    + ".dcd"
                )
                assert False

        return coord_matrix, trajectory.topology, atom_mask
