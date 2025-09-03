import logging
import tempfile
import traceback
import typing as T
from pathlib import Path
import urllib.request
from Bio.PDB import MMCIFParser, PDBIO


def setup_logger(name: str, level=logging.DEBUG):
    """Set up a logger with console output.

    Parameters
    ----------
    name : str
        Name of the logger to create
    level : int, optional
        Logging level to use, by default logging.DEBUG

    Returns
    -------
    logging.Logger
        Configured logger instance with console handler and formatter

    Notes
    -----
    Creates a logger with the specified level that outputs to console with timestamp and level formatting
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Add console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)

    # Create formatter and add it to the handler
    formatter = logging.Formatter("[%(asctime)s %(levelname)s] %(message)s")
    console_handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(console_handler)

    return logger


def get_partition(lst: list, beg: float, end: float):
    """Get a partition of a list based on fractional indices.

    Parameters
    ----------
    lst : list
        Input list to partition
    beg : float
        Beginning fraction in range [0, 1]
    end : float
        Ending fraction in range [0, 1]

    Returns
    -------
    list
        Sublist containing elements from index floor(len(lst) * beg) to floor(len(lst) * end)

    Raises
    ------
    ValueError
        If beg or end are not in [0, 1] range or if beg > end

    Notes
    -----
    Returns the half-open interval [beg, end) partition of the input list
    """
    if not 0.0 <= beg <= end <= 1.0:
        raise ValueError(
            "Invalid range. beg must be less than or equal to end,"
            "and both must be between 0 and 1."
        )

    n = len(lst)
    start_index = int(n * beg)
    end_index = int(n * end)

    return lst[start_index:end_index]


def download_pdb(
    pdb_id: str, output_path: Path, logger: T.Optional[logging.Logger] = None
) -> None:
    """Download PDB file in either PDB or mmCIF format and save to output_path.

    Parameters
    ----------
    pdb_id : str
        The PDB ID to download.
    output_path : Path
        The path where the PDB file should be saved.

    Returns
    -------
    None

    Raises
    ------
    RuntimeError
        If both PDB and mmCIF format downloads fail.

    Notes
    -----
    First attempts to download in PDB format. If that fails, tries mmCIF format
    and converts to PDB. Uses a temporary directory for intermediate files.
    """
    try:
        # Try downloading PDB format first
        urllib.request.urlretrieve(
            f"http://files.rcsb.org/download/{pdb_id}.pdb", str(output_path)
        )
        if logger:
            logger.info(f"Downloaded {pdb_id} in PDB format")
    except Exception as e:
        # Try downloading and converting CIF format
        with tempfile.TemporaryDirectory() as tmp_dir:
            cif_path = Path(tmp_dir) / f"{pdb_id}.cif"
            try:
                urllib.request.urlretrieve(
                    f"http://files.rcsb.org/download/{pdb_id}.cif", str(cif_path)
                )

                # Convert CIF to PDB
                parser = MMCIFParser()
                structure = parser.get_structure("structure", cif_path)
                io = PDBIO()
                io.set_structure(structure)
                io.save(output_path)
                if logger:
                    logger.info(
                        f"Downloaded {pdb_id} in mmCIF format and converted to PDB"
                    )
            except Exception as e:
                if logger:
                    logger.error(
                        f"Failed to download {pdb_id} in either PDB or mmCIF format"
                    )
                    logger.error(traceback.format_exc())
                raise RuntimeError(f"Failed to download {pdb_id}: {e}")
