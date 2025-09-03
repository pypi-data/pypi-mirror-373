from typing import Union

from lz4.frame import LZ4FrameFile

from .errors import PGPackError
from .enums import CompressionMethod
from .offset import OffsetOpener
from .zstdstream import (
    zstd_file,
    ZstdDecompressionReader,
    ZstdCompressionWriter,
)


def pgcopy_compressor(
    offset_opener: OffsetOpener,
    compression_method: CompressionMethod,
) -> Union[
    OffsetOpener,
    LZ4FrameFile,
    ZstdDecompressionReader,
    ZstdCompressionWriter,
]:
    """Select uncompressor."""

    if compression_method == CompressionMethod.NONE:
        return offset_opener

    if compression_method == CompressionMethod.LZ4:
        return LZ4FrameFile(offset_opener, offset_opener.mode)

    if compression_method == CompressionMethod.ZSTD:
        return zstd_file(offset_opener, offset_opener.mode)

    raise PGPackError()
