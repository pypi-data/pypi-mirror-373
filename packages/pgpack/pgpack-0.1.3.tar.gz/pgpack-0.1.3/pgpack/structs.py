from typing import NamedTuple


class PGParam(NamedTuple):
    """Length and scale params."""

    length: int
    scale: int
