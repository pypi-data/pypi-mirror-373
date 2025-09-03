"""Parse hmmsearch output file."""

from typing import List, Tuple
import pandas as pd

from foldeverything.data.data import Template


def parse_pfam(path: str, max_templates: int) -> Template:
    """Parse the content of an HHR file."""
    return
