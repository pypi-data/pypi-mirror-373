from typing import List

import mdtraj as md
import numpy as np

from foldeverything.data.md_sampling.md_sampler import MDSampler


class MSMSampler(MDSampler):
    """Tokenize an input structure for training."""

    def __init__(
        self, num_samples: int = 512, combine_replicas: bool = True, seed: int = 42
    ) -> None:
        """Initialize the UniformSampler."""
        self.rng = np.random.default_rng(seed)
        self.num_samples = num_samples
        self.combine_replicas = combine_replicas

        assert num_samples > 0, "Number of samples must be greater than 0."

    def sample(self, trajs: List[md.Trajectory]) -> List[md.Trajectory]:
        """Sample the input data.

        Parameters
        ----------
        traj : Input
            The input trajectory data.

        Returns
        -------
        The sampled trajectory.

        """
        msg = "This method is not implemented yet."
        raise NotImplementedError(msg)
