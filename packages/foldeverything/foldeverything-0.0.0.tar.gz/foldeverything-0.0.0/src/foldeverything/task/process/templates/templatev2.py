import json
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path

from Bio import Align

from foldeverything.data.data import PFAM, PFamSet
from foldeverything.task.process.process import Resource, Source


@dataclass
class Candidate:
    """A candidate template."""

    id: str
    st: int
    en: int


@dataclass
class Alignment:
    """An alignment between a query and a template."""

    query_st: int
    query_en: int
    template_st: int
    template_en: int


@dataclass
class Template:
    """A template set."""

    query_st: int
    query_en: int
    template_pdb: str
    template_id: str
    template_st: int
    template_en: int


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


class TemplateSource(Source):
    """A template data source."""

    def __init__(
        self,
        entity_to_seqid: str,
        entity_metadata: str,
        templates_metadata: str,
        pfam_dir: str,
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
            Maximum number of templates per entity to include.
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
        self._entity_to_seqid = Path(entity_to_seqid)
        self._entity_metadata = Path(entity_metadata)
        self._templates_metadata = Path(templates_metadata)
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

    def fetch(self) -> list:
        """Get a list of raw data points.

        Returns
        -------
        List[A3M]
            A list of raw data points

        """
        data: dict[str, list[PFAM]] = {}

        with self._entity_to_seqid.open("r") as f:
            entity_to_seqid = json.load(f)

        for entity_id, seq_id in entity_to_seqid.items():
            pdb_id = entity_id.split("_")[0].lower()
            template = PFAM(entity_id, seq_id)
            data.setdefault(pdb_id, []).append(template)

        return [PFamSet(p, t) for p, t in data.items()]

    def resource(self) -> dict:
        """Return a shared resource needed for processing.

        Returns
        -------
        Dict
            The shared resource.

        """
        with Path(self._entity_metadata).open("r") as f:
            entity_metadata = json.load(f)

        with Path(self._templates_metadata).open("r") as f:
            templates_metadata = json.load(f)

        metadata = {**entity_metadata, **templates_metadata}
        return metadata

    def process(self, data: PFamSet, resource: Resource, outdir: Path) -> None:
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
        entity_to_templates = {}
        for entity in data.entities:
            # Get ids
            entity_id = entity.entity_id
            seq_id = entity.seq_id

            # Get metadata about this chain
            query_metadata = resource.get(entity_id)
            query_date = query_metadata["date"]
            query_date = datetime.strptime(query_date, "%Y-%m-%d")  # noqa: DTZ007
            query_seq = query_metadata["sequence"]

            # Get the PFAM file for this chain
            path = self._pfam_dir / f"{seq_id}.pfam"

            # Select valid candidates based on date
            entity_to_templates[entity_id] = []
            for candidate in parse_pfam(path):
                # Stop if we have enough candidates
                if len(entity_to_templates[entity_id]) >= self._max_templates:
                    break

                # Get candidate metadata
                candidate_metadata = resource.get(candidate.id)

                # Skip if no metadata
                if candidate_metadata is None:
                    continue

                # Skip if we have already processed this PDB
                pdb_id = candidate.id.split("_")[0].split("=")[1]

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

                # Add candidate to list
                template = Template(
                    query_st=query_st,
                    query_en=query_en,
                    template_pdb=pdb_id,
                    template_id=candidate.id,
                    template_st=candidate_st,
                    template_en=candidate_en,
                )
                entity_to_templates[entity_id].append(asdict(template))

        # Write a record for this pdb id
        record_path = outdir / "records" / f"{data.pdb_id}.json"
        with record_path.open("w") as f:
            json.dump(entity_to_templates, f)

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
