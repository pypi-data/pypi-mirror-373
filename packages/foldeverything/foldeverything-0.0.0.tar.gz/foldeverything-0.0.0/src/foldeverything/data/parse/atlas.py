from pathlib import Path
from typing import Tuple

import mdtraj as md
import numpy as np

from foldeverything.data.md_sampling.md_sampler import MDSampler
from foldeverything.data.parse.md import MDrawParser


class ATLAS_RawMD(MDrawParser):

    def __init__(self, md_sampler: MDSampler) -> None:
        """Initialize the raw MD parser."""
        super().__init__(md_sampler)

    def parse(self, path: Path, name: str) -> Tuple[np.ndarray, md.Topology]:
        """Parse the raw MD data.

        Returns
        -------
        Tuple[np.ndarray, md.Topology]
            The coordinate matrix and the topology.
        """
        # Parse PDB to be used as topology for md_traj
        file_pdb = path / f"{name}.pdb"
        pdb_obj = md.load_pdb(file_pdb)

        # Loop through triplicate trajectory files, extract
        trajectories = []
        for replicate in range(3):
            file_xtc = path / f"{name}_R{replicate + 1}.xtc"
            trajectory = md.load(file_xtc, top=pdb_obj)
            trajectories.append(trajectory)

        # Sample the trajectories
        trajectory = self.md_sampler.sample(trajectories)[0]

        # path = "/afs/csail.mit.edu/u/m/mreveiz/rbg/temp_while_cp_rsg/Boltz_MD/David/ATLAS_examples"
        # trajectory.save(path + f"/{name}_sampled.xtc")
        # trajectory.save_pdb(path + f"/{name}_sampled.pdb")

        # Coordinates are in nanometers, transform to angstroms and add replicate
        # dimension
        coord_matrix = trajectory.xyz[None] * 10

        i = 0
        atom_mask = np.ones(coord_matrix.shape[2], dtype=bool)
        for chain in pdb_obj.topology.chains:
            for residue in chain.residues:
                for atom in residue.atoms:
                    assert atom.index == i
                    i += 1

        return coord_matrix, pdb_obj.topology, atom_mask
