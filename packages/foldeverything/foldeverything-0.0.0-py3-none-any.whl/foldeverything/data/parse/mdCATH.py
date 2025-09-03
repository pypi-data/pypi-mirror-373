import argparse
import os
import tempfile
from pathlib import Path
from typing import Tuple

import h5py
import mdtraj as md
import numpy as np

from foldeverything.data.md_sampling.md_sampler import MDSampler
from foldeverything.data.parse.md import MDrawParser


def _open_h5_file(h5):
    if isinstance(h5, str):
        h5 = h5py.File(h5, "r")
    code = [_ for _ in h5][0]
    return h5, code


def _extract_structure_and_coordinates(h5, code, temp, replica):
    """Extract the structure in PDB fmt and coords from an H5 file based on T and replica.

    Parameters
    ----------
    h5 : h5py.File
        An opened H5 file object containing protein structures and simulation data.
    code : str
        The identifier for the dataset in the H5 file.
    temp : int or float
        The temperature (in Kelvin).
    replica : int
        The replica number.

    Returns
    -------
    tuple
        A tuple containing the PDB data as bytes and the coordinates as a numpy array.
    """
    with tempfile.NamedTemporaryFile(suffix=".pdb", delete=False) as pdbfile:
        pdb = h5[code]["pdbProteinAtoms"][()]
        pdbfile.write(pdb)
        pdbfile.flush()
        coords = h5[code][f"{temp}"][f"{replica}"]["coords"][:]
    coords = coords / 10.0
    return pdbfile.name, coords


def convert_to_mdtraj(h5, temp, replica):
    """
    Convert data from an H5 file to an MDTraj trajectory object.

    This function extracts the first protein atom structure and coordinates
    for a given temperature and replica from an H5 file and creates an MDTraj
    trajectory object. This object can be used for further molecular dynamics
    analysis.

    Parameters
    ----------
    h5 : h5py.File
        An opened H5 file object containing protein structures and simulation data.
    temp : int or float
        The temperature (in Kelvin) at which the simulation was run. This is used
        to select the corresponding dataset within the H5 file.
    replica : int
        The replica number of the simulation to extract data from. This is used
        to select the corresponding dataset within the H5 file.

    Returns
    -------
    md.Trajectory
        An MDTraj trajectory object containing the loaded protein structure and
        simulation coordinates.

    Example:
    -------
    import h5py
    import mdtraj as md

    # Open the H5 file
    with h5py.File('simulation_data.h5', 'r') as h5file:
        traj = convert_to_mdtraj(h5file, 300, 1)

    # Now 'traj' can be used for analysis with MDTraj
    """
    h5, code = _open_h5_file(h5)
    pdb_file_name, coords = _extract_structure_and_coordinates(h5, code, temp, replica)
    trj = md.load(pdb_file_name)
    os.unlink(pdb_file_name)
    trj.xyz = coords.copy()
    trj.time = np.arange(1, coords.shape[0] + 1)
    return trj


class MDCATH_RawMD(MDrawParser):

    def __init__(self, h5_dir: str, topology_dir: str, md_sampler: MDSampler) -> None:
        """Initialize the raw MD parser."""
        super().__init__(md_sampler=md_sampler)
        self.h5_dir = h5_dir
        self.replica_list = [0, 1, 2, 3, 4]
        self.topology_dir = topology_dir

    def parse(self, name: str, temperature) -> Tuple[np.ndarray, md.Topology]:
        """Parse the raw MD data.

        Returns
        -------
        Tuple[np.ndarray, md.Topology]
            The coordinate matrix and the topology.
        """
        domain_id = name.split("_")[0]

        # Parse PDB to be used as topology for md_traj
        file_h5 = str(self.h5_dir / f"{domain_id}.h5")

        h5, code = _open_h5_file(file_h5)

        file_pdb = self.topology_dir / f"{name}.pdb"
        with open(file_pdb, "wb") as pdbfile:
            pdb = h5[code]["pdbProteinAtoms"][()]
            pdbfile.write(pdb)
        pdb_obj = md.load_pdb(file_pdb)

        trajectories = []
        for replica in self.replica_list:
            trajectory = convert_to_mdtraj(h5, temperature, replica)
            trajectories.append(trajectory)

        # Sample the trajectories
        trajectory = self.md_sampler.sample(trajectories)[0]

        """
        # Some replicates have different number of frames, pad with zeros and create mask
        pad_length = max(lengths)
        replica_masks = np.zeros((len(coord_matrix), pad_length))
        for i in range(len(coord_matrix)):
            length = lengths[i]
            if length < pad_length:
                pad = np.zeros((pad_length - length, coord_matrix[i].shape[1], 3))
                coord_matrix[i] = np.concatenate([coord_matrix[i], pad], axis=0)
            replica_masks[i, 0:length] = 1

        coord_matrix = np.array(coord_matrix)  # (replicas, frames, atoms, 3)

        # coord_matrix = coord_matrix[:, 0:10, :, :] # TODO remove this line
        # replica_masks = replica_masks[:, 0:10] # TODO remove this line"
        """

        # Coordinates are in nanometers, transform to angstroms
        coord_matrix = trajectory.xyz[None] * 10

        i = 0
        atom_mask = np.ones(coord_matrix.shape[2], dtype=bool)
        for chain in pdb_obj.topology.chains:
            for residue in chain.residues:
                for atom in residue.atoms:
                    assert atom.index == i
                    i += 1

        return coord_matrix, pdb_obj.topology, atom_mask

