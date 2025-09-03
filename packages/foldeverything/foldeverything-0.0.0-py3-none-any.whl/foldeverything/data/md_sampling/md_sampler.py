from abc import ABC, abstractmethod
from typing import List

import mdtraj as md


class MDSampler(ABC):
    """Sample frames from an MD trajectory and returns sampled trajectory."""

    @abstractmethod
    def sample(self, trajs: List[md.Trajectory]) -> List[md.Trajectory]:
        """Sample the input data.

        Parameters
        ----------
        data : Inpput
            The input trajectory replicas to sample from.

        Returns
        -------
        The sampled trajectories.

        """
        raise NotImplementedError
