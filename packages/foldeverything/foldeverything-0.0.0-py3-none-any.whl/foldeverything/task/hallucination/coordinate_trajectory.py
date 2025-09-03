import os
import tempfile
import numpy as np


def pdb_strings_to_aligned_trajectory(pdb_strings):
    """Convert a list of PDB string contents to an aligned mdtraj trajectory with backbone + small molecules"""

    import mdtraj as md
    
    # Create temporary files for each frame
    temp_files = []
    try:
        for i, pdb_content in enumerate(pdb_strings):
            # Create a temporary file for this frame
            temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.pdb', delete=False)
            temp_file.write(pdb_content)
            temp_file.close()
            temp_files.append(temp_file.name)
        
        # Load the first frame to establish topology
        first_frame = md.load(temp_files[0])
        
        # Find backbone atoms and non-protein atoms (ligands/small molecules)
        backbone_indices = first_frame.topology.select('backbone')
        protein_indices = first_frame.topology.select('protein')
        all_indices = list(range(first_frame.n_atoms))
        non_protein_indices = [i for i in all_indices if i not in protein_indices]
        
        # Combine backbone + ligand atoms
        selected_indices = list(backbone_indices) + non_protein_indices
        selected_indices.sort()  # Keep in order
        
        print(f"Found {len(backbone_indices)} backbone atoms")
        print(f"Found {len(non_protein_indices)} non-protein atoms (ligands/small molecules)")
        print(f"Total selected atoms: {len(selected_indices)}")
        
        # Extract selected atoms from first frame
        selected_traj = first_frame.atom_slice(selected_indices)
        
        # Load remaining frames one by one and extract selected atoms
        all_coords = [selected_traj.xyz[0]]  # First frame coordinates
        valid_frames = [0]  # Track which frames were successfully loaded
        
        for i, temp_file in enumerate(temp_files[1:], 1):
            frame = md.load(temp_file)
            frame_backbone_indices = frame.topology.select('backbone')
            frame_protein_indices = frame.topology.select('protein')
            frame_all_indices = list(range(frame.n_atoms))
            frame_non_protein_indices = [j for j in frame_all_indices if j not in frame_protein_indices]
            
            frame_selected_indices = list(frame_backbone_indices) + frame_non_protein_indices
            frame_selected_indices.sort()
            
            if len(frame_selected_indices) == len(selected_indices):
                # Same number of selected atoms, extract them
                frame_selected = frame.atom_slice(frame_selected_indices)
                all_coords.append(frame_selected.xyz[0])
                valid_frames.append(i)
            else:
                raise ValueError(f"Frame {i}: Different atom count ({len(frame_selected_indices)} vs {len(selected_indices)})")
                    
        # Create trajectory with all coordinates
        all_coords = np.array(all_coords)
        
        # Create trajectory with selected topology and all coordinates
        trajectory = md.Trajectory(
            xyz=all_coords,
            topology=selected_traj.topology
        )
        
        # Align trajectory to first frame using backbone atoms
        # Find backbone atom indices in the reduced trajectory
        reduced_backbone_indices = []
        atom_idx = 0
        for original_idx in selected_indices:
            if original_idx in backbone_indices:
                reduced_backbone_indices.append(atom_idx)
            atom_idx += 1
        
        if len(reduced_backbone_indices) > 0:
            # Align all frames to the last frame
            trajectory.superpose(trajectory, frame=-1, atom_indices=reduced_backbone_indices)
        
        return trajectory
        
    finally:
        # Clean up temporary files
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.unlink(temp_file)