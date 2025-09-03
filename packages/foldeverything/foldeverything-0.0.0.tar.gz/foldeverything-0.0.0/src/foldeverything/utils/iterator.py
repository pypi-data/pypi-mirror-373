# Code taken from https://github.com/enricobacis/infinite
import itertools
import pdb


class GeneratorExhausted(Exception):
    pass


class GenCacher:
    """Cache the generator values to permit random accesses."""

    def __init__(self, generator):
        self._g = generator
        self._cache = []

    def __getitem__(self, idx):
        while len(self._cache) <= idx:
            try:
                self._cache.append(next(self._g))
            except StopIteration:
                raise GeneratorExhausted  # stop iteration gets converted to runtime error inside generators
        return self._cache[idx]


def _summations(sumTo, n=2):
    """yields all the n-uples that sum to sumTo."""

    if n == 1:
        yield (sumTo,)

    else:
        for head in range(sumTo + 1):
            for tail in _summations(sumTo - head, n - 1):
                yield (head,) + tail


def product(*generators):
    """generate the cartesian product of infinite generators."""

    generators = list(map(GenCacher, generators))
    for distance in itertools.count(0):
        for idxs in _summations(distance, len(generators)):
            try:
                ret = tuple(gen[idx] for gen, idx in zip(generators, idxs))
            except GeneratorExhausted:
                return
            yield ret