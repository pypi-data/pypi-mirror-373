import fcntl
import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import numpy as np
from Bio import Align

from foldeverything.data.data import PFAM, Structure, Template, TemplateCoordinates
from foldeverything.task.process.process import Resource, Source


@dataclass
class Alignment:
    """An alignment between a query and a template."""

    query_st: int
    query_en: int
    template_st: int
    template_en: int


@dataclass
class Candidate:
    """A candidate template."""

    id: str
    st: int
    en: int


def shorten_name(name: str) -> str:
    """Get the shorted candidate ID.

    Parameters
    ----------
    name : str
        The candidate ID.

    Returns
    -------
    str
        The shorted candidate ID.
    """
    return "_".join(name.split("_")[0:2])


def align_sequences(query: str, template: str) -> Alignment:
    """Align a sequence to a template.

    Parameters
    ----------
    query : str
        The query sequence.
    template : str
        The template sequence.

    Returns
    -------
    Alignment
        The alignment between the query and template.

    """
    aligner = Align.PairwiseAligner(scoring="blastp")
    aligner.mode = "local"
    aligner.open_gap_score = -1000
    aligner.extend_gap_score = -1000
    result = aligner.align(query, template)[0].coordinates
    return Alignment(
        query_st=int(result[0][0]),
        query_en=int(result[0][1]),
        template_st=int(result[1][0]),
        template_en=int(result[1][1]),
    )


def parse_pfam(path: Path) -> list[Candidate]:
    """Parse a PFAM file.

    Parameters
    ----------
    path : Path
        The path to the PFAM file.

    Returns
    -------
    list[Candidate]
        The list of candidate templates.

    """
    candidates = []

    with path.open("r") as f:
        for line in f:
            if not line.startswith("# Domain scores"):
                continue
            break
        for line in f:
            if not line.startswith("PDB"):
                continue

            info = line.split()
            candidates.append(
                Candidate(
                    id=info[0],
                    st=int(info[7]) - 1,
                    en=int(info[8]),
                )
            )

    return candidates


def compute_frame(
    n: np.ndarray,
    ca: np.ndarray,
    c: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Compute the frame for a residue.

    Parameters
    ----------
    n : np.ndarray
        The N atom.
    ca : np.ndarray
        The C atom.
    c : np.ndarray
        The CA atom.

    Returns
    -------
    np.ndarray
        The frame.

    """
    v1 = c - ca
    v2 = n - ca
    e1 = v1 / np.linalg.norm(v1)
    u2 = v2 - e1 * np.dot(e1.T, v2)
    e2 = u2 / np.linalg.norm(u2)
    e3 = np.cross(e1, e2)
    rot = np.column_stack([e1, e2, e3])
    t = ca
    return rot, t


def process_template(
    struct: Structure,
    candidate_id: str,
    candidate_st: int,
    candidate_en: int,
    query_st: int,
) -> Optional[Template]:
    """Process a template.

    Parameters
    ----------
    struct : Structure
        The PDB structure.
    candidate_id : str
        The candidate ID.
    candidate_st : int
        The candidate start index.
    candidate_en : int
        The candidate end index.
    query_st : int
        The query start index.

    Returns
    -------
    Template
        The processed template.

    """
    # Get the relevant chain using entity id
    entity_id = int(candidate_id.split("_")[1].split("=")[1])
    try:
        chain = struct.chains[struct.chains["entity_id"] == entity_id][0]
    except:  # noqa: E722
        # This may fail if the chain is not in assembly 1.
        return None

    # Get candidates residues for this chain
    res_st = chain["res_idx"]
    res_en = chain["res_idx"] + chain["res_num"]
    residues = struct.residues[res_st:res_en]
    residues = residues[candidate_st:candidate_en]

    # Populate feature tables
    data = []
    for idx, res in enumerate(residues):
        # Get residue index in query
        query_idx = idx + query_st

        # Get residue type
        res_type = res["res_type"]

        # Get center atoms
        atom_ca = struct.atoms[res["atom_center"]]
        atom_cb = struct.atoms[res["atom_disto"]]

        coords_ca = atom_ca["coords"]
        coords_cb = atom_cb["coords"]

        mask_ca = atom_ca["is_present"]
        mask_cb = atom_cb["is_present"]

        # Get frame atoms
        atom_st = res["atom_idx"]
        atom_en = res["atom_idx"] + res["atom_num"]
        atoms = struct.atoms[atom_st:atom_en]

        # Atoms are always in the order N, CA, C
        atom_n = atoms[0]
        atom_ca = atoms[1]
        atom_c = atoms[2]

        # Compute frame and mask
        frame_mask = atom_ca["is_present"]
        frame_mask &= atom_c["is_present"]
        frame_mask &= atom_n["is_present"]

        if bool(frame_mask):
            frame_rot, frame_t = compute_frame(
                atom_n["coords"],
                atom_ca["coords"],
                atom_c["coords"],
            )
            frame_rot = frame_rot.flatten()
        else:
            frame_rot = np.eye(3).flatten()
            frame_t = np.zeros(3)

        data.append(
            (
                query_idx,
                res_type,
                frame_rot,
                frame_t,
                coords_cb,
                coords_ca,
                frame_mask,
                mask_cb,
                mask_ca,
            )
        )

    # Create template
    data = np.array(data, dtype=TemplateCoordinates)
    return Template(coordinates=data)


class TemplateSource(Source):
    """A template data source."""

    def __init__(
        self,
        chain_mapping: str,
        chains_metadata: str,
        templates_metadata: str,
        pfam_dir: str,
        struct_dir: str,
        max_templates: int = 20,
        min_date_diff: int = 60,
        min_residues: int = 10,
        min_coverage: float = 0.1,
        max_coverage_identical: float = 0.95,
    ) -> None:
        """Initialize the data source.

        Parameters
        ----------
        data_dir : str
            Path to the directory containing template files.
        metadata : str
            Path to the template metadata file.
        max_templates : int, optional
            Maximum number of templates to include.
        min_date_diff : int, optional
            Minimum date difference between query and candidate.
        min_residues : int, optional
            Minimum number of aligned residues required.
        min_coverage : float, optional
            Minimum coverage of query sequence required.
        max_coverage_identical : float, optional
            Maximum coverage of identical residues allowed.

        """
        self._pfam_dir = Path(pfam_dir)
        self._chain_mapping = Path(chain_mapping)
        self._chains_metadata = Path(chains_metadata)
        self._templates_metadata = Path(templates_metadata)
        self._struct_dir = Path(struct_dir)
        self._max_templates = max_templates
        self._min_date_diff = min_date_diff
        self._min_residues = min_residues
        self._min_coverage = min_coverage
        self._max_coverage_identical = max_coverage_identical

    def setup(self, outdir: Path) -> None:
        """Run pre-processing in main thread.

        Parameters
        ----------
        outdir : Path
            The output directory.

        """
        records_dir = outdir / "records"
        records_dir.mkdir(parents=True, exist_ok=True)

        templates_dir = outdir / "templates"
        templates_dir.mkdir(parents=True, exist_ok=True)

    def fetch(self) -> list:
        """Get a list of raw data points.

        Returns
        -------
        List[A3M]
            A list of raw data points

        """
        data: list = []

        with self._chain_mapping.open("r") as f:
            chain_mapping = json.load(f)

        for chain_id, seq_id in chain_mapping.items():
            template = PFAM(chain_id, seq_id)
            data.append(template)

        return data

    def resource(self) -> dict:
        """Return a shared resource needed for processing.

        Returns
        -------
        Dict
            The shared resource.

        """
        with Path(self._chains_metadata).open("r") as f:
            chains_metadata = json.load(f)

        with Path(self._templates_metadata).open("r") as f:
            templates_metadata = json.load(f)

        metadata = {**chains_metadata, **templates_metadata}
        return metadata

    def process(self, data: PFAM, resource: Resource, outdir: Path) -> None:
        """Run processing in a worker thread.

        Parameters
        ----------
        data : Any
            The raw input data.
        resource: Resource
            The shared resource.
        outdir : Path
            The output directory.

        """
        # Get metadata about this chain
        query_metadata = resource.get(data.entity_id)
        query_date = query_metadata["date"]
        query_date = datetime.strptime(query_date, "%Y-%m-%d")  # noqa: DTZ007
        query_seq = query_metadata["sequence"]

        # Get the PFAM file for this chain
        path = self._pfam_dir / f"{data.seq_id}.pfam"

        # Select valid candidates based on date
        templates = []
        pdb_visited = set()
        for candidate in parse_pfam(path):
            # Stop if we have enough candidates
            if len(templates) >= self._max_templates:
                break

            # Get candidate metadata
            candidate_metadata = resource.get(candidate.id)

            # Skip if no metadata
            if candidate_metadata is None:
                continue

            # Skip if we have already processed this PDB
            pdb_id = candidate.id.split("_")[0].split("=")[1]
            if pdb_id in pdb_visited:
                continue
            pdb_visited.add(pdb_id)

            # Extract the candidate subsequence
            candidate_seq = candidate_metadata["sequence"]
            candidate_subseq = candidate_seq[candidate.st : candidate.en]

            # Note: we cannot rely on the start and end indices
            # from hmmbuild for the query sequence, because it
            # might have shifted its start so we must realign the
            # sequences to get the correct start and end indices
            try:
                aln = align_sequences(query_seq, candidate_subseq)
            except:  # noqa: E722, S112
                continue

            # Extract the query subsequence
            query_st, query_en = aln.query_st, aln.query_en
            query_subseq = query_seq[query_st:query_en]

            # Extract the candidate subsequence again because the
            # above might also have shifted the start, end indices
            candidate_st = candidate.st + aln.template_st
            candidate_en = candidate_st + aln.template_en
            candidate_subseq = candidate_seq[candidate_st:candidate_en]

            # Ensure minimum length and length matching
            alignment_len = query_en - query_st

            # Skip too small alignments
            if alignment_len < self._min_residues:
                continue

            # Skip too low coverage
            if alignment_len < (0.1 * len(query_seq)):
                continue

            # Skip too high identity coverage
            if (query_subseq == candidate_subseq) and (
                alignment_len > (self._max_coverage_identical * len(query_seq))
            ):
                continue

            # Skip less than 60 days old
            candidate_date = candidate_metadata["date"]
            candidate_date = datetime.strptime(candidate_date, "%Y-%m-%d")  # noqa: DTZ007
            if candidate_date >= (query_date - timedelta(days=self._min_date_diff)):
                continue

            # Now process the candidate if it hasn't been processed yet
            # To check, we index using the seq_id and candidate id and
            # create a locked file to prevent possible race conditions
            file_name = f"{data.seq_id}|{shorten_name(candidate.id)}"
            file_path = outdir / "templates" / f"{file_name}.npz"

            # Check if the file exists
            if file_path.exists():
                templates.append(file_name)
                continue

            # Open the file in write mode
            with file_path.open("w") as f:
                # Acquire a lock on the file, skip if already locked
                try:
                    fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                except BlockingIOError:
                    continue

                # Process the candidate
                pdb_path = self._struct_dir / f"{pdb_id}.npz"
                pdb_struct = Structure.load(pdb_path)
                try:
                    template = process_template(
                        pdb_struct,
                        candidate.id,
                        candidate_st,
                        candidate_en,
                        query_st,
                    )
                    if template is not None:
                        template: Template
                        template.dump(f.name)
                        templates.append(file_name)
                except:  # noqa: S110, E722
                    pass

                # Release the lock
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

        # Write a record for the chain
        record_path = outdir / "records" / f"{data.chain_id}.json"
        with record_path.open("w") as f:
            json.dump(templates, f)

    def finalize(self, outdir: Path) -> None:
        """Run post-processing in main thread.

        Parameters
        ----------
        outdir : Path
            The output directory.

        """
        # Group records into a manifest
        records_dir = outdir / "records"

        failed_count = 0
        records = {}
        for record in records_dir.iterdir():
            path = records_dir / record
            name = path.stem
            try:
                with path.open("r") as f:
                    records[name] = json.load(f)
            except:  # noqa: E722
                failed_count += 1
                print(f"Failed to parse {record}")
        print(f"Failed to parse {failed_count} entries)")

        # Save manifest
        outpath = outdir / "manifest.json"
        with outpath.open("w") as f:
            json.dump(records, f)
