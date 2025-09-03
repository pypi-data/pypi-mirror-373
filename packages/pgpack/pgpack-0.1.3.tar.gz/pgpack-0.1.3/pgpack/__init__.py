"""Library for read and write storage format for PGCopy dump
packed into LZ4, ZSTD or uncompressed
with meta data information packed into zlib."""

from .enums import CompressionMethod
from .errors import (
    PGPackError,
    PGPackHeaderError,
    PGPackMetadataCrcError,
    PGPackModeError,
)
from .reader import PGPackReader
from .writer import PGPackWriter


__all__ = (
    "CompressionMethod",
    "PGPackError",
    "PGPackHeaderError",
    "PGPackMetadataCrcError",
    "PGPackModeError",
    "PGPackReader",
    "PGPackWriter",
)
__author__ = "0xMihalich"
__version__ = "0.1.3"
