from collections import defaultdict
from random import sample as sample_fn
from typing import Iterator, List, Literal

import numpy as np
from numpy.random import RandomState

from foldeverything.data.const import activity_types
from foldeverything.data.data import Record
from foldeverything.data.sample.sampler import Sample, Sampler


class AffinitySampler(Sampler):
    def __init__(
        self,
        num_consecutive_actives: int = 2,
        num_filter_actives: int = 2,
        weight_K: float = 1.0,
        weight_IC: float = 1.0,
        cluster_fnc: Literal["uniform", "sqrt", "cbcrt", "log", "linear"] = "uniform",
        protein_fnc: Literal["uniform", "sqrt", "cbcrt", "log", "linear"] = "uniform",
        aid_fnc: Literal["uniform", "sqrt", "cbcrt", "log", "linear"] = "uniform",
    ) -> None:
        self.num_consecutive_actives = num_consecutive_actives
        self.num_filter_actives = num_filter_actives
        self.list_names_K = [key for key, value in activity_types.items() if value == 0]
        self.weight_K = weight_K
        self.weight_IC = weight_IC
        if cluster_fnc == "uniform":
            self.fnc_cluster_id = lambda x: 1
        elif cluster_fnc == "sqrt":
            self.fnc_cluster_id = lambda x: x**0.5
        elif cluster_fnc == "cbcrt":
            self.fnc_cluster_id = lambda x: x ** (1 / 3)
        elif cluster_fnc == "log":
            self.fnc_cluster_id = lambda x: np.log(x + 1)
        elif cluster_fnc == "linear":
            self.fnc_cluster_id = lambda x: x
        else:
            raise ValueError("Invalid cluster_fnc")

        if protein_fnc == "uniform":
            self.fnc_protein_id = lambda x: 1
        elif protein_fnc == "sqrt":
            self.fnc_protein_id = lambda x: x**0.5
        elif protein_fnc == "cbcrt":
            self.fnc_protein_id = lambda x: x ** (1 / 3)
        elif protein_fnc == "log":
            self.fnc_protein_id = lambda x: np.log(x + 1)
        elif protein_fnc == "linear":
            self.fnc_protein_id = lambda x: x
        else:
            raise ValueError("Invalid protein_fnc")

        if aid_fnc == "uniform":
            self.fnc_aid_id = lambda x: 1 * float(x >= self.num_filter_actives)
        elif aid_fnc == "sqrt":
            self.fnc_aid_id = lambda x: x**0.5 * float(x >= self.num_filter_actives)
        elif aid_fnc == "cbcrt":
            self.fnc_aid_id = lambda x: x ** (1 / 3) * float(
                x >= self.num_filter_actives
            )
        elif aid_fnc == "log":
            self.fnc_aid_id = lambda x: np.log(x + 1) * float(
                x >= self.num_filter_actives
            )
        elif aid_fnc == "linear":
            self.fnc_aid_id = lambda x: x * float(x >= self.num_filter_actives)
        else:
            raise ValueError("Invalid aid_fnc")

    def sample(
        self,
        records: List[Record],
        random: RandomState,
    ) -> Iterator[Sample]:
        """Sample a structure from the dataset infinitely.

        Parameters
        ----------
        records : List[Record]
            The records to sample from.
        random : RandomState
            The random state for reproducibility.

        Yields
        ------
        Sample
            A data sample.

        """
        # Compute weights
        # same code as below but with the following structure cluster --> protein --> aids --> [(record, chain_id, outcome, activity_name)]
        items = {}
        cluster_id_count = defaultdict(int)
        aid_to_weight = {}

        for record in records:
            if record.affinity.outcome == 0:
                continue
            cluster_id = record.chains[0].cluster_id
            normalized_protein_accession = record.affinity.normalized_protein_accession
            aid = record.affinity.aid
            cluster_id_count[cluster_id] += 1
            if cluster_id not in items:
                items[cluster_id] = {normalized_protein_accession: {aid: []}}
            elif normalized_protein_accession not in items[cluster_id]:
                items[cluster_id][normalized_protein_accession] = {aid: []}
            elif aid not in items[cluster_id][normalized_protein_accession]:
                items[cluster_id][normalized_protein_accession][aid] = []
            for chain_id, chain in enumerate(record.chains):
                if not chain.valid:
                    continue
                if chain.mol_type == 3:
                    items[cluster_id][normalized_protein_accession][aid].append(
                        (record, chain_id)
                    )
                    weight_type = (
                        self.weight_K
                        if record.affinity.activity_name in self.list_names_K
                        else self.weight_IC
                    )
                    aid_to_weight[aid] = weight_type

        # Compute weights to sample clusters
        cluster_id_weights = []
        cluster_ids = []
        for key in cluster_id_count:
            cluster_id_weights.append(self.fnc_cluster_id(cluster_id_count[key]))
            cluster_ids.append(key)
        cluster_id_weights = np.array(cluster_id_weights) / np.sum(cluster_id_weights)
        cluster_ids = np.array(cluster_ids)
        # Sample infinitely
        while True:
            # Sample cluster
            cluster_id = random.choice(cluster_ids, p=cluster_id_weights)
            items_cluster = items[cluster_id]

            # Sample protein within cluster uniformly at random
            normalized_protein_accessions = list(items_cluster.keys())
            normalized_protein_accessions_weights = np.array(
                [
                    self.fnc_protein_id(
                        sum([len(aid_list) for aid_list in items_cluster[key].values()])
                    )
                    for key in normalized_protein_accessions
                ]
            )
            if np.sum(normalized_protein_accessions_weights) == 0:
                continue
            else:
                normalized_protein_accessions_weights = (
                    normalized_protein_accessions_weights
                    / np.sum(normalized_protein_accessions_weights)
                )
            normalized_protein_accession = random.choice(
                normalized_protein_accessions,
                p=normalized_protein_accessions_weights,
            )
            items_protein = items_cluster[normalized_protein_accession]

            # Sample aid within protein following weights
            aids = list(items_protein.keys())
            aids_weights = np.array(
                [
                    aid_to_weight[aid] * self.fnc_aid_id(len(items_protein[aid]))
                    for aid in aids
                ]
            )
            if np.sum(aids_weights) == 0:
                continue
            else:
                aids_weights = aids_weights / np.sum(aids_weights)

            aid = random.choice(aids, p=aids_weights)
            items_list = items_protein[aid]
            sample_items = sample_fn(
                items_list,
                k=min(self.num_consecutive_actives, len(items_list)),
            )
            for sample in sample_items:
                record, chain_id = sample
                yield Sample(record=record, chain_id=chain_id)

    def get_sample_validation(self, record: Record) -> Sample:  # noqa: D102
        for chain_id, chain in enumerate(record.chains):  # noqa: B007
            if not chain.valid:
                continue
            if chain.mol_type == 3:  # noqa: PLR2004
                break
        return Sample(record=record, chain_id=chain_id)
