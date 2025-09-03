import hashlib
from pathlib import Path
from typing import List

from foldeverything.data import const
from foldeverything.data.data import (
    PDB,
    ChainInfo,
    Record,
    StructureInfo,
    Target,
)
from foldeverything.data.parse.fasta import parse_fasta
from foldeverything.task.process.process import Resource
from foldeverything.task.process.targets.target import TargetsSource


def hash_sequence(seq: str) -> str:
    """Hash the sequence."""
    return hashlib.sha256(seq.encode()).hexdigest()


class CASP15SeqsTargets(TargetsSource):
    """The RCSB target data source."""

    def __init__(
        self,
        data_dir: str,
        msa_dir: str,
        components: str,
    ) -> None:
        """Initialize the data source.

        Parameters
        ----------
        data_dir : str
            Path to the directory containing the PDB archive.
        components : str
            Path to the processed CCD components dictionary.

        """
        filters = []
        self._msas = {x.stem for x in Path(msa_dir).rglob("*.npz")}
        super().__init__(data_dir, components, filters)

    def fetch(self) -> List[PDB]:
        """Get a list of raw data points.

        Returns
        -------
        List[Raw]
            A list of raw data points

        """
        data: List[PDB] = []

        for path in Path(self._data_dir).iterdir():
            target_id = path.stem
            target = PDB(id=target_id, path=str(path))
            data.append(target)

        return data

    def parse(self, data: PDB, resource: Resource) -> Target:
        """Process a structure.

        Parameters
        ----------
        data : PDB
            The raw input data.
        resource: Resource
            The shared resource.

        Returns
        -------
        Target
            The processed data.

        """
        structure = parse_fasta(Path(data.path), resource)

        # Create chain metadata
        chain_info = []
        for chain in structure.chains:
            # Get one letter code
            res_start = chain["res_idx"]
            res_end = res_start + chain["res_num"]
            residues = structure.residues[res_start:res_end]

            if chain["mol_type"] == const.chain_type_ids["PROTEIN"]:
                token_map = const.prot_token_to_letter
                seq = [token_map[str(res["name"])] for res in residues]
                msa_id = hash_sequence("".join(seq))
                assert msa_id in self._msas
            else:
                msa_id = -1

            chain_info.append(
                ChainInfo(
                    chain_id=int(chain["asym_id"]),
                    chain_name=chain["name"],
                    msa_id=msa_id,
                    template_id=-1,
                    mol_type=int(chain["mol_type"]),
                    cluster_id=-1,
                    num_residues=int(chain["res_num"]),
                )
            )

        structure_info = StructureInfo(
            num_chains=len(structure.chains),
        )

        # Create record
        record = Record(
            id=data.id,
            structure=structure_info,
            chains=chain_info,
            interfaces=[],
        )

        return Target(structure=structure, record=record)
