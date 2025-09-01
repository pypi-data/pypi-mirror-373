"""URL to BibTeX converter."""

from .core import (
    doi2bibtex,
    isbn2bibtex,
    parse_bibtex,
    set_verbosity,
    url2bibtex,
)
from .version import __version__

__all__ = [
    "url2bibtex",
    "doi2bibtex",
    "isbn2bibtex",
    "parse_bibtex",
    "set_verbosity",
    "__version__",
]
