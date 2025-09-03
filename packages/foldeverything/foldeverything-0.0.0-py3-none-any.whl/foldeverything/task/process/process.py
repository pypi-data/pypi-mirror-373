import hashlib
import multiprocessing
import pickle
from abc import ABC, abstractmethod
from functools import partial
from itertools import islice
from pathlib import Path
from typing import Any, Callable, Dict, Generic, List, TypeVar

import numpy as np
from omegaconf import OmegaConf
from redis import Redis
from tqdm import tqdm

from foldeverything.task.task import Task

####################################################################################################
# RESOURCE
####################################################################################################


class Resource:
    """A shared resource for processing.

    The resource is a shared dictionary that can be used
    to store data that is too large to be shared across
    many workers. It is implemented as a Redis database.
    This class implements a simple dictionary interface
    to interact with the Redis database, including the
    automatic serialization and deserialization of data.

    """

    def __init__(self, host: str, port: int) -> None:
        """Initialize the resource.

        Parameters
        ----------
        host : str
            The Redis host.
        port : int
            The Redis port.

        """
        self._redis = Redis(host=host, port=port)

    def get(self, key: str) -> Any:  # noqa: ANN401
        """Get an item from the resource.

        Parameters
        ----------
        key : str
            The key to get.

        Returns
        -------
        Any
            The value associated with the key.

        """
        value = self._redis.get(key)
        if value is not None:
            value = pickle.loads(value)  # noqa: S301
        return value

    def set(self, key: str, value: Any) -> None:  # noqa: ANN401
        """Set an item on the resource.

        Parameters
        ----------
        key : str
            The key to set.
        value : Any
            The value to set.
        """
        self._redis.set(key, pickle.dumps(value))

    def fill(self, data: Dict) -> None:
        """Initialize the resource.

        Parameters
        ----------
        data : Dict
            The shared dictionary.

        """
        size = 100000
        it = iter(data.items())
        for _ in tqdm(range(0, len(data), size), total=len(data) // size):
            chunk = {k: pickle.dumps(v) for k, v in islice(it, size)}
            self._redis.mset(chunk)

    def flush(self) -> None:
        """Flush the resource."""
        self._redis.flushdb()

    def __getitem__(self, key: str) -> Any:  # noqa: ANN401
        """Get an item from the resource."""
        out = self.get(key)
        if out is None:
            raise KeyError(key)
        return out


####################################################################################################
# SOURCE
####################################################################################################

T = TypeVar("T")


class Source(ABC, Generic[T]):
    """A data source interface.

    The interface is designed to fetch and process data
    in parallel. This is achieved by first fetching the
    list of raw data points and running processing in
    parallel across many workers. In some cases, this
    requires a shared resource that is too large to be
    replicated across workers. In this case, the setup
    method is used to create the shared resource, as a
    Redis database which can be used during processing.

    """

    @abstractmethod
    def fetch(self) -> List[T]:
        """Get the list of raw datapoints.

        Returns
        -------
        List[T]
            The raw datapoints, in any format.

        """
        raise NotImplementedError

    @abstractmethod
    def process(self, data: T, resource: Resource, outdir: Path) -> None:
        """Run processing in a worker thread.

        Parameters
        ----------
        data : T
            The raw input data.
        resource: Resource
            The shared resource.
        outdir : Path
            The output directory.

        """
        raise NotImplementedError

    def resource(self) -> Dict:
        """Get the shared resource for processing.

        Returns
        -------
        Dict
            The shared resource, as a dictionary.

        """
        return {}

    def setup(self, outdir: Path) -> None:  # noqa: ARG002
        """Run pre-processing in main thread.

        Parameters
        ----------
        outdir : Path
            The output directory.

        """
        return

    def finalize(self, outdir: Path) -> None:  # noqa: ARG002
        """Run post-processing in main thread.

        Parameters
        ----------
        outdir : Path
            The output directory.

        """
        return


####################################################################################################
# PROCESSING
####################################################################################################


def get_subfolder(name: str) -> str:
    """Get a subfolder name by hashing the input name.

    Parameters
    ----------
    name : str
        The name to hash.

    Returns
    -------
    str
        The first 2 characters of the SHA256 hash of the name.

    """
    return hashlib.sha256(name.encode()).hexdigest()[:2]


def helper(
    data: List[T],
    fn: Callable,
    host: str,
    port: int,
    outdir: str,
) -> None:
    """Run processing in a worker thread.

    Parameters
    ----------
    data : List[T]
        The raw input data.
    fn : Callable
        The processing function.
    host : str
        The Redis host.
    port : int
        The Redis port.
    outdir : str
        The output directory.

    """
    outdir = Path(outdir)
    resource = Resource(host=host, port=port)
    for item in tqdm(data, total=len(data)):
        fn(data=item, resource=resource, outdir=outdir)


class Processing(Task):
    """A data processing task.

    The task is designed to fetch and process data in
    parallel. It uses a custom source object to fetch
    the raw data points, run pre-processing, setting
    up a shared resource, run processing in parallel,
    and define post-processing logic. It can be run in
    debug mode which limits the number of data points.
    Note that a redis server must be running for use.

    """

    def __init__(
        self,
        source: Source,
        outdir: str,
        num_processes: int,
        redis_host: str,
        redis_port: int,
        debug: bool = False,
    ) -> None:
        """Initialize the processing.

        Parameters
        ----------
        source : Source
            The data source.
        outdir : str
            The output directory.
        num_processes : int
            The number of processes.
        redis_host : str
            The Redis host.
        redis_port : int
            The Redis port.

        """
        self.source = source
        self.outdir = outdir
        self.num_processes = num_processes
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.debug = debug

    def run(self, config: OmegaConf) -> None:
        """Run the data processing task.

        Parameters
        ----------
        config : OmegaConf
            The configuration for the task, for bookkeeping.

        """
        # Create output directory
        outdir = Path(self.outdir)
        outdir.mkdir(parents=True, exist_ok=True)

        # Dump configuration
        with Path.open(outdir / "config.yaml", "w") as f:
            OmegaConf.save(config, f)

        # Check if we can run in parallel
        num_processes = min(self.num_processes, multiprocessing.cpu_count())
        parallel = (not self.debug) and num_processes > 1

        # Setup source
        self.source.setup(outdir)

        shared_data = self.source.resource()
        if shared_data and num_processes > 1:
            # Setup shared resource
            resource = Resource(host=self.redis_host, port=self.redis_port)
            resource.flush()
            resource.fill(shared_data)
            redis_init = True
            del shared_data
        else:
            resource = shared_data
            redis_init = False

        # Get data points
        data = self.source.fetch()

        # Randomly permute the data
        random = np.random.RandomState()
        permute = random.permutation(len(data))
        data = [data[i] for i in permute]

        # Limit the number of data points if debug
        if self.debug:
            data = data[: min(100, len(data))]

        # Run processing
        if parallel:
            # Create processing function
            fn = partial(
                helper,
                fn=self.source.process,
                host=self.redis_host,
                port=self.redis_port,
                outdir=self.outdir,
            )

            # Split the data into random chunks
            size = len(data) // num_processes
            chunks = [data[i : i + size] for i in range(0, len(data), size)]

            # Run processing in parallel
            with multiprocessing.Pool(num_processes) as pool:  # noqa: SIM117
                with tqdm(total=len(chunks)) as pbar:
                    for _ in pool.imap_unordered(fn, chunks):
                        pbar.update()
        else:
            for item in tqdm(data, total=len(data)):
                self.source.process(item, resource, outdir)

        # Finalize
        self.source.finalize(outdir)

        # Cleanup
        if redis_init:
            resource.flush()
