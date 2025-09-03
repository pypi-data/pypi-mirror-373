import concurrent.futures
from pathlib import Path
from typing import Tuple

import mdtraj as md
import numpy as np
from openmm import Platform, unit
from openmm.app import PDBFile
from pdbfixer import PDBFixer
from tqdm import tqdm

from foldeverything.data.parse.md import MDCoarseFullAtomParser, MDrawParser


class IDRome_FullAtom(MDCoarseFullAtomParser):
    def helper(self, pdb_name: str) -> None:
        # Load into PDBFixer
        platform = Platform.getPlatform("CPU")
        platform.setPropertyDefaultValue("Threads", str(self.pdb_fixer_threads))
        fixer = PDBFixer(pdb_name, platform=platform)

        # Find and add missing atoms
        fixer.findMissingResidues()
        fixer.findMissingAtoms()
        fixer.addMissingAtoms()

        return fixer

    def add_missing_atoms_with_timeout(self, pdb_name: str, timeout: int = 60) -> bool:
        """
        Run fixer.addMissingAtoms() with a timeout inside a multiprocessing worker.

        Args:
            fixer (PDBFixer): The PDBFixer object.
            timeout (int): Max time allowed (seconds) before termination.

        Returns
        -------
            bool: True if successful, False if timeout occurs.
        """
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(self.helper, pdb_name)
            try:
                return future.result(timeout=timeout)
            except concurrent.futures.TimeoutError:
                return None

    def parse(self, traj: md.Trajectory, name: str) -> Tuple[np.ndarray, md.Topology]:
        """Convert coarse grained IDRome data to full atom data.

        Returns
        -------
        Tuple[np.ndarray, md.Topology]
            The coordinate matrix and the topology.
        """
        new_coords = []
        patience = self.patience
        topology = None
        for f_idx in range(traj.n_frames):
            # Break if number of attempts exceeds patience
            if patience == 0:
                break

            # Extract frame
            frame = traj[f_idx]

            # Save the frame as a temporary PDB file
            pdb_name = str(self.working_dir / f"temp_{name}_{f_idx}.pdb")
            frame.save_pdb(pdb_name)

            # Use timeout-protected PDBFixer
            fixer = self.add_missing_atoms_with_timeout(pdb_name, timeout=self.timeout)
            if fixer is not None:
                pass
                print(f"Successfully fixed {pdb_name}")
            else:
                print(f"Failed:skipping atom fixing for {pdb_name} due to timeout.")
                patience -= 1
                continue

            # Store coordintes in angstroms as floats
            new_coords.append(np.array(fixer.positions.value_in_unit(unit.angstrom)))

            # Remove temporary PDB file
            Path(pdb_name).unlink()

            # Save the topology once
            if topology is None:
                # Save fixed structure to a temporary PDB file
                pdb_name_out = str(self.working_dir / f"temp_{name}_{f_idx}_fixed.pdb")
                with Path(pdb_name_out).open("w") as f:
                    PDBFile.writeFile(fixer.topology, fixer.positions, f)

                # Load last frame to get the topology
                topology = md.load_pdb(pdb_name_out).topology

                # Remove temporary PDB file
                # Path(pdb_name_out).unlink()

        if topology is None:
            raise ValueError("No valid topology was built.")

        # Stack the new coordinates, add a replicate dimension
        new_coords = np.stack(new_coords, axis=0)[
            None
        ]  # (replicate=1, frames, atoms, 3)

        return new_coords, topology


class IDRome_RawMD(MDrawParser):
    def __init__(
        self,
        md_sampler,
        cg2all_working_dir,
        timeout: int = 10,
        patience: int = 4,
        pdb_fixer_threads: int = 1,
    ) -> None:
        """Initialize the raw MD parser."""
        super().__init__(md_sampler)

        self.cg2all = IDRome_FullAtom(
            working_dir=cg2all_working_dir, timeout=timeout, patience=patience, pdb_fixer_threads=pdb_fixer_threads
        )

    def parse(
        self, path: Path, uid_name: str
    ) -> Tuple[np.ndarray, md.Topology, np.ndarray]:
        """Parse the raw MD data.

        Returns
        -------
        Tuple[np.ndarray, md.Topology]
            The coordinate matrix and the topology.
        """
        # Parse PDB to be used as topology for md_traj
        file_pdb = str(path / "top.pdb")
        pdb_obj = md.load_pdb(file_pdb)

        # Load trajectory
        file_xtc = str(path / "traj.xtc")
        trajectory = md.load(file_xtc, top=pdb_obj)

        initial_num_residues = trajectory.xyz.shape[1]

        #if initial_num_residues > self.max_length:
        #    raise AssertionError("Too many residues")

        # Sample the trajectory
        trajectory = self.md_sampler.sample([trajectory])[0]

        # Convert coarse grained to full atom
        coord_matrix, topology = self.cg2all.parse(trajectory, uid_name)

        allowed_atoms = ("CA", "CB")

        i = 0
        atom_mask = np.zeros(coord_matrix.shape[2], dtype=bool)
        num_gly = 0
        for chain in topology.chains:
            for residue in chain.residues:
                if residue.name == "GLY":
                    num_gly += 1
                for atom in residue.atoms:
                    # We will set non-CA atoms as non resolved: they should
                    # be masked in model
                    if atom.name in allowed_atoms:
                        atom_mask[atom.index] = True
                    assert atom.index == i
                    i += 1

        # Make sure we have the right number of atoms. Glycine has no CB.
        adjusted = num_gly if "CB" in allowed_atoms else 0
        assert atom_mask.sum() == initial_num_residues * len(allowed_atoms) - adjusted

        return coord_matrix, topology, atom_mask
