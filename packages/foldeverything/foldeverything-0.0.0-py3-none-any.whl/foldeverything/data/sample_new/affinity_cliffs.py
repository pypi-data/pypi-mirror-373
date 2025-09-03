from collections import defaultdict
from random import sample as sample_fn
from typing import Iterator, List, Literal, Dict, Optional
from dataclasses import replace
import pickle

import numpy as np
from numpy.random import RandomState

from foldeverything.data.const import activity_types
from foldeverything.data.data import Record
from foldeverything.data.sample.sampler import Sample, Sampler


class AffinityCliffsSampler(Sampler):
    def __init__(
        self,
        num_consecutive_actives: int = 2,
        num_decoys_per_active: int = 0,
        num_filter_actives: int = 0,
        id_to_cid_decoys: Optional[str] = None,
        id_to_affinity_smooth: Optional[str] = None,
        aid_to_cliff: Optional[str] = None,
        cliff_fnc: Literal[
            "uniform", "sqr", "sqrt", "cbc", "4th", "cbcrt", "log", "linear"
        ] = "uniform",
        cluster_fnc: Literal["uniform", "sqrt", "cbcrt", "log", "linear"] = "uniform",
        aid_fnc: Literal["uniform", "sqrt", "cbcrt", "log", "linear"] = "uniform",
        weight_IC: float = 1.0,
        weight_K: float = 1.0,
    ) -> None:
        self.num_consecutive_actives = num_consecutive_actives
        self.num_filter_actives = num_filter_actives
        self.num_decoys_per_active = num_decoys_per_active
        self.list_names_K = [key for key, value in activity_types.items() if value == 0]
        if id_to_cid_decoys:
            with open(id_to_cid_decoys, "rb") as f:
                self.id_to_cid_decoys = pickle.load(f)
        if id_to_affinity_smooth:
            with open(id_to_affinity_smooth, "rb") as f:
                self.id_to_affinity_smooth = pickle.load(f)
        else:
            self.id_to_affinity_smooth = None
        if aid_to_cliff:
            with open(aid_to_cliff, "rb") as f:
                self.aid_to_cliff = pickle.load(f)
        else:
            self.aid_to_cliff = None

        if cliff_fnc == "uniform":
            self.fnc_cliff_id = lambda x: 1 + 1e-5
        elif cliff_fnc == "sqr":
            self.fnc_cliff_id = lambda x: x**2 + 1e-5
        elif cliff_fnc == "cbc":
            self.fnc_cliff_id = lambda x: x**3 + 1e-5
        elif cliff_fnc == "4th":
            self.fnc_cliff_id = lambda x: x**4 + 1e-5
        elif cliff_fnc == "sqrt":
            self.fnc_cliff_id = lambda x: x**0.5 + 1e-5
        elif cliff_fnc == "cbcrt":
            self.fnc_cliff_id = lambda x: x ** (1 / 3) + 1e-5
        elif cliff_fnc == "log":
            self.fnc_cliff_id = lambda x: np.log(x + 1) + 1e-5
        elif cliff_fnc == "linear":
            self.fnc_cliff_id = lambda x: x + 1e-5
        else:
            raise ValueError("Invalid fnc_cliff")

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

        if aid_fnc == "uniform":
            self.fnc_aid_id = lambda x: 1
        elif aid_fnc == "sqrt":
            self.fnc_aid_id = lambda x: x**0.5
        elif aid_fnc == "cbcrt":
            self.fnc_aid_id = lambda x: x ** (1 / 3)
        elif aid_fnc == "log":
            self.fnc_aid_id = lambda x: np.log(x + 1)
        elif aid_fnc == "linear":
            self.fnc_aid_id = lambda x: x
        else:
            raise ValueError("Invalid aid_fnc")

        self.prob_K = weight_K / (weight_K + weight_IC)

    def sample(
        self,
        records: List[Record],
        random: RandomState,
    ) -> Iterator[Record]:
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
        items_K = defaultdict(list)
        cluster_id_count_K = defaultdict(int)
        items_IC = defaultdict(list)
        cluster_id_count_IC = defaultdict(int)

        for record in records:
            record.affinity.activity_name
            if record.affinity.activity_name in self.list_names_K:
                cluster_id = record.chains[0].cluster_id
                aid = record.affinity.assay_prot_id
                cluster_id_count_K[cluster_id] += self.fnc_cliff_id(
                    self.aid_to_cliff[aid]
                )
                if cluster_id not in items_K:
                    items_K[cluster_id] = {aid: []}
                elif aid not in items_K[cluster_id]:
                    items_K[cluster_id][aid] = []
                items_K[cluster_id][aid].append(record)
            else:
                cluster_id = record.chains[0].cluster_id
                aid = record.affinity.assay_prot_id
                cluster_id_count_IC[cluster_id] += self.fnc_cliff_id(
                    self.aid_to_cliff[aid]
                )
                if cluster_id not in items_IC:
                    items_IC[cluster_id] = {aid: []}
                elif aid not in items_IC[cluster_id]:
                    items_IC[cluster_id][aid] = []
                items_IC[cluster_id][aid].append(record)

        cluster_id_weights_K = []
        cluster_ids_K = []
        for key, value in cluster_id_count_K.items():
            cluster_id_weights_K.append(self.fnc_cluster_id(value))
            cluster_ids_K.append(key)
        cluster_id_weights_K = np.array(cluster_id_weights_K) / np.sum(
            cluster_id_weights_K
        )
        cluster_ids_K = np.array(cluster_ids_K)

        cluster_id_weights_IC = []
        cluster_ids_IC = []
        for key, value in cluster_id_count_IC.items():
            cluster_id_weights_IC.append(self.fnc_cluster_id(value))
            cluster_ids_IC.append(key)
        cluster_id_weights_IC = np.array(cluster_id_weights_IC) / np.sum(
            cluster_id_weights_IC
        )
        cluster_ids_IC = np.array(cluster_ids_IC)

        while True:
            try:
                if random.random() < self.prob_K:
                    cluster_id = random.choice(cluster_ids_K, p=cluster_id_weights_K)
                    items_cluster = items_K[cluster_id]
                else:
                    cluster_id = random.choice(cluster_ids_IC, p=cluster_id_weights_IC)
                    items_cluster = items_IC[cluster_id]
            except:
                continue

            aid_weights = []
            aids = []
            for key, value in items_cluster.items():
                if self.aid_to_cliff is None:
                    cliff_weight = 1
                else:
                    cliff_weight = self.fnc_cliff_id(self.aid_to_cliff[key])
                filter_aid_mask = 0 if len(value) < self.num_filter_actives else 1
                aid_weights.append(
                    self.fnc_aid_id(len(value) * cliff_weight) * filter_aid_mask
                )
                aids.append(key)
            if np.sum(aid_weights).item() == 0:
                continue
            aid_weights = np.array(aid_weights) / np.sum(aid_weights)
            aids = np.array(aids)

            aid = random.choice(aids, p=aid_weights)

            records_aid = items_cluster[aid]

            sample_records = sample_fn(
                records_aid,
                k=min(self.num_consecutive_actives, len(records_aid)),
            )

            for record in sample_records:
                # pick a random record
                if self.id_to_affinity_smooth is None:
                    yield record
                else:
                    affinity_smooth = self.id_to_affinity_smooth[record.id]
                    record = replace(
                        record,
                        affinity=replace(record.affinity, affinity=affinity_smooth),
                    )
                    yield record
                for _ in range(self.num_decoys_per_active):
                    record_decoy = self.get_decoy(record, random)
                    yield record_decoy

    def get_decoy(self, record: Record, random: RandomState) -> Record:
        """Get a decoy record.

        Parameters
        ----------
        record : Record
            The record to sample from.
        random : RandomState
            The random state for reproducibility.

        Returns
        -------
        Record
            The decoy record.

        """
        # get record and affinity_record
        record_decoy = record
        record_affinity_decoy = record.affinity

        # modify ligand_id and affinity_record
        record_id = record.id
        decoy_ligand_cid = random.choice(self.id_to_cid_decoys[record_id])
        record_affinity_decoy = replace(
            record_affinity_decoy, outcome=0, affinity=10.0, cid=decoy_ligand_cid
        )
        record_decoy = replace(
            record_decoy, ligand_id=decoy_ligand_cid, affinity=record_affinity_decoy
        )

        return record_decoy
