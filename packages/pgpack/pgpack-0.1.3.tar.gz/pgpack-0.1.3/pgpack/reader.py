from io import BufferedReader
from struct import unpack
from typing import (
    Any,
    Union,
    Optional,
)
from zlib import (
    crc32,
    decompress,
)

from lz4.frame import LZ4FrameFile
from pandas import DataFrame as PdFrame
from pgcopylib import (
    PGCopy,
    PGOid,
)
from polars import DataFrame as PlFrame

from .compressor import pgcopy_compressor
from .errors import (
    PGPackHeaderError,
    PGPackMetadataCrcError,
)
from .enums import CompressionMethod
from .header import HEADER
from .metadata import metadata_reader
from .offset import OffsetOpener
from .structs import PGParam
from .zstdstream import ZstdDecompressionReader


class PGPackReader:
    """Class for read PGPack format."""

    fileobj: BufferedReader
    columns: list[str]
    pgtypes: list[PGOid]
    pgparam: list[PGParam]
    pgcopy: PGCopy
    header: bytes
    metadata_crc: int
    metadata_length: int
    metadata_zlib: bytes
    compression_method: CompressionMethod
    pgcopy_compressed_length: int
    pgcopy_data_length: int
    offset_opener: OffsetOpener
    pgcopy_compressor: Union[
        OffsetOpener,
        LZ4FrameFile,
        ZstdDecompressionReader,
    ]
    _str: Optional[str]

    def __init__(
        self,
        fileobj: BufferedReader,
    ) -> None:
        """Class initialization."""

        self.fileobj = fileobj
        self.header = self.fileobj.read(8)

        if self.header != HEADER:
            raise PGPackHeaderError()

        self.metadata_crc, self.metadata_length = unpack(
            "!2L",
            self.fileobj.read(8),
        )
        self.metadata_zlib = self.fileobj.read(self.metadata_length)

        if crc32(self.metadata_zlib) != self.metadata_crc:
            raise PGPackMetadataCrcError()

        self.columns, self.pgtypes, self.pgparam = metadata_reader(
            decompress(self.metadata_zlib)
        )
        (
            compression_method,
            self.pgcopy_compressed_length,
            self.pgcopy_data_length,
        ) = unpack(
            "!B2Q",
            self.fileobj.read(17),
        )

        self.compression_method = CompressionMethod(compression_method)
        self.offset_opener = OffsetOpener(self.fileobj)
        self.pgcopy_compressor = pgcopy_compressor(
            self.offset_opener,
            self.compression_method,
        )
        self.pgcopy = PGCopy(
            self.pgcopy_compressor,
            self.pgtypes,
        )
        self._str = None

    def __repr__(self) -> str:
        """String representation in interpreter."""

        return self.__str__()

    def __str__(self) -> str:
        """String representation of PGPackReader."""

        def to_col(text: str) -> str:
            """Format string element."""

            text = text[:14] + "…" if len(text) > 15 else text
            return f" {text: <15} "

        if not self._str:
            empty_line = (
                "│-----------------+-----------------│"
            )
            end_line = (
                "└─────────────────┴─────────────────┘"
            )
            _str = [
                "<PostgreSQL/GreenPlum compressed dump>",
                "┌─────────────────┬─────────────────┐",
                "│ Column Name     │ PostgreSQL Type │",
                "╞═════════════════╪═════════════════╡",
            ]

            for column, pgtype in zip(self.columns, self.pgtypes):
                _str.append(
                    f"│{to_col(column)}│{to_col(pgtype.name)}│",
                )
                _str.append(empty_line)

            _str[-1] = end_line
            self._str = "\n".join(_str) + f"""
Total columns: {len(self.columns)}
Compression method: {self.compression_method.name}
Unpacked size: {self.pgcopy_data_length} bytes
Compressed size: {self.pgcopy_compressed_length} bytes
Compression rate: {round(
    (self.pgcopy_compressed_length / self.pgcopy_data_length) * 100, 2
)} %
"""
        return self._str

    def to_python(self, size: int = -1) -> list[Any]:
        """Convert to python objects."""

        return self.pgcopy.read(size)

    def to_pandas(self, size: int = -1) -> PdFrame:
        """Convert to pandas.DataFrame."""

        return PdFrame(
            data=self.to_python(size),
            columns=self.columns,
        )

    def to_polars(self, size: int = -1) -> PlFrame:
        """Convert to polars.DataFrame."""

        return PlFrame(
            data=self.to_python(size),
            schema=self.columns,
            orient="row",
        )

    def to_bytes(self, size: int = -1) -> bytes:
        """Get raw unpacked data."""

        self.pgcopy_compressor.seek(0)

        return self.pgcopy_compressor.read(size)
