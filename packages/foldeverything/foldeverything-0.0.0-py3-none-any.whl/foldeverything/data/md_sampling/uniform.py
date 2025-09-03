from typing import List

import mdtraj as md
import numpy as np

from foldeverything.data.md_sampling.md_sampler import MDSampler


class UniformSampler(MDSampler):
    """Sample frames from a set of trajectories from MD uniformly."""

    def __init__(
        self,
        num_samples: int = 512,
        combine_replicas: bool = True,
        seed: int = 42,
        traj_frame_ratio_from_end: float = 1.0,
    ) -> None:
        """Initialize the UniformSampler."""
        self.rng = np.random.default_rng(seed)
        self.num_samples = num_samples
        self.combine_replicas = combine_replicas
        self.traj_frame_ratio_from_end = traj_frame_ratio_from_end

        assert num_samples > 0, "Number of samples must be greater than 0."

    def safe_superpose(
        self, traj: md.Trajectory, ref_frame: int = 0, eps=0.1
    ) -> md.Trajectory:
        ca_indices = traj.topology.select("name CA")

        # TODO expand to non CA
        if len(ca_indices) == 0:
            raise ValueError("No CA atoms found in the trajectory.")
        if len(ca_indices) < 3:
            raise ValueError("Not enough CA atoms for superposition.")

        # Check for NaN or infinite values
        if np.isnan(traj.xyz).any() or np.isinf(traj.xyz).any():
            msg = "Warning: Trajectory contains NaN or inf values."
            raise AssertionError(msg)

        # Compute RMSD before superposition
        rmsd_before = md.rmsd(traj, traj, frame=0, atom_indices=ca_indices)
        # print(f"RMSD before alignment: {rmsd_before.mean():.4f} nm")

        # Align all frames to the first frame
        traj.superpose(traj, frame=ref_frame, atom_indices=ca_indices)

        # Check if distances are too small (collapsed)
        distances = np.linalg.norm(traj.xyz[0] - traj.xyz[0].mean(axis=0), axis=1)
        if np.max(distances) < eps:  # Threshold depends on the system (in nm)
            msg = "Structure appears collapsed after transformation!"
            raise AssertionError(msg)

        # Check for NaN or infinite values
        if np.isnan(traj.xyz).any() or np.isinf(traj.xyz).any():
            msg = "Warning: Trajectory contains NaN or inf values."
            raise AssertionError(msg)

        # Compute RMSD after superposition
        rmsd_after = md.rmsd(traj, traj, frame=0, atom_indices=ca_indices)
        # print(f"RMSD after alignment: {rmsd_after.mean():.4f} nm")

        # If RMSD increased, transformation is likely wrong
        if rmsd_after.mean() > rmsd_before.mean() + 0.1:
            msg = "RMSD increased after alignment!"
            raise AssertionError(msg)

        return traj


    def sample(self, trajs: List[md.Trajectory]) -> List[md.Trajectory]:
        """Sample the input data.

        Parameters
        ----------
        coords : Inpput
            The input data.

        Returns
        -------
        The sampled trajectory.

        """
        trajs_new = []
        if self.combine_replicas:
            num_replicas = len(trajs)
            for i, traj in enumerate(trajs):
                # Sample equally from replicates
                N = self.num_samples // num_replicas  # noqa: N806
                num_samples = N + (self.num_samples % num_replicas) if i == 0 else N
                # msg = "Number of samples must be less than the number of frames."
                effective_frames = np.floor(
                    traj.n_frames * self.traj_frame_ratio_from_end
                )
                frame_start = np.ceil(
                    traj.n_frames * (1 - self.traj_frame_ratio_from_end)
                )
                # assert effective_frames >= num_samples, msg
                num_samples = int(min(num_samples, effective_frames))
                sampled_indices = self.rng.choice(
                    np.arange(frame_start, traj.n_frames), num_samples, replace=False
                ).astype(int)
                # print("sampled_indices", sampled_indices)

                T = traj[sampled_indices]
                # coord_matrix = T.xyz
                # print("coord_matrix 1-1", coord_matrix.shape, coord_matrix[0].shape, "\n", coord_matrix[0])
                trajs_new.append(T)

            # Combine the trajectories
            traj = md.join(trajs_new, check_topology=True)
            # print(traj)
            # coord_matrix = traj.xyz
            # print("coord_matrix 1-2", coord_matrix.shape, coord_matrix[0].shape, "\n", coord_matrix[0])

            # Superpose the combined trajectory
            traj = self.safe_superpose(traj, ref_frame=0)

            # coord_matrix = traj.xyz
            # print("coord_matrix 1-3", coord_matrix.shape, coord_matrix[0].shape, "\n", coord_matrix[0])

            trajs_new = [traj]
        else:
            raise NotImplementedError(
                "Sampling from multiple replicas is not yet implemented."
            )

        return trajs_new
