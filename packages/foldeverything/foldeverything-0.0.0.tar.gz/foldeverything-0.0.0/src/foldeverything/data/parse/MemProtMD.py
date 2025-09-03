from pathlib import Path
from typing import Dict, Tuple

import mdtraj as md
import numpy as np
import pandas as pd

from foldeverything.data import const
from foldeverything.data.md_sampling.md_sampler import MDSampler
from foldeverything.data.parse.md import MDrawParser


class MemProtMD_RawMD(MDrawParser):
    def __init__(self, md_sampler: MDSampler) -> None:
        """Initialize the raw MD parser."""
        super().__init__(md_sampler)

        self.ccd_code_mapping = {
            "DPPC": "PCF", # 1,2-DIACYL-SN-GLYCERO-3-PHOSHOCHOLINE ? 1,2-Dipalmitoylphosphatidylcholine ?
            "DPP": "PCF",
        }

        self.atom_mapping = {
            "NC3": "N",
            "C12": "C12",
            "C11": "C11",
            "O12": "O13",
            "P": "P",
            "O11": "O11",
            "O13": "O12",
            "O14": "O14",
            "C13": "C13",
            "C14": "C14",
            "C15": "C15",
            "C1": "C1",
            "C2": "C2",
            "C3": "C3",
            "O31": "O31",
            "C31": "C31",
            "O32": "O32",
            "C32": "C32",
            "C33": "C33",
            "C34": "C34",
            "C35": "C35",
            "C36": "C36",
            "C37": "C37",
            "C38": "C38",
            "C39": "C39",
            "0C31": "C40",
            "1C31": "C41",
            "2C31": "C42",
            "3C31": "C43",
            "O21": "O21",
            "C21": "C21",
            "O22": "O22",
            "C22": "C22",
            "C23": "C23",
            "C24": "C24",
            "C25": "C25",
            "C26": "C26",
            "C27": "C27",
            "C28": "C28",
            "C29": "C29",
            "0C21": "C30",
            "1C21": "C47",
            "2C21": "C48",
            "3C21": "C49",
            "4C21": "C50",
            "5C21": "C51",
            "6C21": "C52",
            "4C31": "C44",
            "5C31": "C45",
            "6C31": "C46",
        }

    def _reindex(self, traj: md.Trajectory) -> md.Trajectory:
        """
        Reindex the atoms in the given trajectory.

        Parameters
        ----------
        traj : md.Trajectory
            The original trajectory.

        Returns
        -------
        md.Trajectory
            The new trajectory with reindexed atoms.
        """
        assert traj.xyz.shape[0] == 1, "Only one frame is supported."

        # Create a new topology
        new_top = md.Topology()

        # Iterate over chains and create new entities in the new topology
        coords = []
        for old_chain in traj.top.chains:
            new_chain = new_top.add_chain()
            for old_res in old_chain.residues:
                new_res = new_top.add_residue(old_res.name, new_chain)
                for old_atom in old_res.atoms:
                    # Add the atom to the new topology
                    new_top.add_atom(old_atom.name, old_atom.element, new_res)

                    # Add the coordinates
                    coords.append(
                        traj.xyz[0, old_atom.index]
                    )  # extend code for many frames

        # Assign new topology to trajectory
        coords = np.array(coords)
        new_traj = md.Trajectory(coords, new_top)
        return new_traj

    def _split_chains(
        self, old_traj: md.Trajectory, mapper: Dict[str, Dict[int, str]]
    ) -> md.Trajectory:
        """
        Split the chains in the given trajectory based on the provided mapper.

        Parameters
        ----------
        old_traj (md.Trajectory): The original trajectory.
        mapper (dict): A dictionary mapping residue indices to chain IDs.

        Returns
        -------
        md.Trajectory: The new trajectory with split chains.
        chain_type_map: Dict[Tuple[int, str], int]
            A dictionary mapping chain index / ID to chain types.
        """
        assert old_traj.xyz.shape[0] == 1, "Only one frame is supported."

        old_topology = old_traj.topology

        # Create a new topology
        new_topology = md.Topology()

        # Create new chains
        chain_names = set(mapper["chainID"].values())
        new_chains = {k: new_topology.add_chain() for k in chain_names}

        # Iterate through residues and assign to new chains
        coords = []
        chain_type_map = {}

        # Get residues in old topology
        old_residues = [
            residue for chain in old_topology.chains for residue in chain.residues
        ]

        # Loop through resiudes, add to new topology by using the metadata
        # about chains for protein and split lipids into individual chains
        for old_res in old_residues:
            new_chain_id = mapper["chainID"].get(old_res.index + 1, None)  # 1-indexed
            new_res_name = mapper["resName"].get(old_res.index + 1, None)

            if new_chain_id is not None:
                msg = f"Residue name mismatch: {new_res_name} vs {old_res.name}"
                assert new_res_name == old_res.name, msg

                # Add the residue to the new chain
                chain = new_chains[new_chain_id]
                chain_type_map[(chain.index, chain.chain_id)] = {
                    "type": const.chain_type_ids["PROTEIN"],
                    "match_rcsb": True,
                    "entity_name": None
                }
                new_res = new_topology.add_residue(
                    old_res.name, chain
                )
                for atom in old_res.atoms:
                    new_topology.add_atom(atom.name, atom.element, new_res)

                    # Add the coordinates
                    coords.append(
                        old_traj.xyz[0, atom.index]
                    )  # extend code for many frames
            else:
                # This should be a lipid chain #

                # Make sure the resname is in the lipid mapping
                assert old_res.name in self.ccd_code_mapping, f"Residue name is {old_res.name}"

                # Map to a CCD code
                resname = self.ccd_code_mapping[old_res.name]

                # Create a new chain for each lipid
                chain = new_topology.add_chain()
                chain_type_map[(chain.index, chain.chain_id)] = {
                    "type": const.chain_type_ids["NONPOLYMER"],
                    "match_rcsb": False,
                    "entity_name": resname, # chain only has a single residue
                }

                # Add the residue to the new chain
                new_res = new_topology.add_residue(resname, chain)
                for atom in old_res.atoms:
                    new_topology.add_atom(self.atom_mapping.get(atom.name, atom.name), atom.element, new_res)

                    # Add the coordinates
                    coords.append(old_traj.xyz[0, atom.index])

        # Create a new trajectory with the updated topology and reindex atoms
        coords = np.array(coords)
        new_traj = self._reindex(md.Trajectory(coords, new_topology))

        return new_traj, chain_type_map

    def parse(self, path: Path, entry_id: str) -> Tuple[np.ndarray, md.Topology]:
        """Parse the raw MD data.

        Returns
        -------
        Tuple[np.ndarray, md.Topology]
            The coordinate matrix and the topology.
        """
        # Check if the metadata exists and open csv file
        metadata = path / f"metadata/{entry_id}.csv"
        if not metadata.exists():
            msg = f"Metadata file {metadata} not found."
            raise FileNotFoundError(msg)

        # Load the metadata
        df_meta = pd.read_csv(metadata).rename({"Unnamed: 0": "res_index"}, axis=1)
        mapper = df_meta.set_index("res_index")[["chainID", "resName"]].to_dict()

        # Get the PDB file
        pdb_file = path / f"structures/{entry_id}.pdb"
        if not pdb_file.exists():
            msg = f"PDB file {pdb_file} not found."
            raise FileNotFoundError(msg)

        # Load the PDB file
        trajectory = md.load(pdb_file)

        # Remove water molecules
        trajectory = trajectory.atom_slice(
            trajectory.top.select(
                "(not resname HOH) and (not resname SOL) and (not resname NA) and (not resname CL)"
            )
        )

        # Split the chains: proteins are split into chains based on the
        # metadata, while lipids are split into individual chains
        trajectory, chain_type_map = self._split_chains(trajectory, mapper)

        # Get the topology
        topology = trajectory.topology

        # Get the coordinates
        coord_matrix = trajectory.xyz[None]  # (replicate=1, frames, atoms, 3)

        i = 0
        # Atom_mask defines which atoms to treat as present
        atom_mask = np.zeros(coord_matrix.shape[2], dtype=bool)
        for chain in topology.chains:
            for residue in chain.residues:
                for atom in residue.atoms:
                    assert atom.index == i
                    i += 1

        return coord_matrix, topology, atom_mask, chain_type_map
