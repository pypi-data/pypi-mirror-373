import gzip
from typing import cast, TextIO


def open_maybe_gzipped(filename: str, mode: str = "rt") -> TextIO:
    return cast(
        TextIO, gzip.open(filename, mode) if filename.endswith(".gz") else open(filename, mode)
    )
