from io import (
    BufferedReader,
    BufferedWriter,
)
from struct import pack
from typing import (
    Any,
    Optional,
    Union,
    TYPE_CHECKING,
)
from zlib import (
    crc32,
    compress,
)

from pandas import DataFrame as PdFrame
from polars import DataFrame as PlFrame
from pgcopylib import (
    PGCopyWriter,
    PGOid,
)

from .compressor import pgcopy_compressor
from .enums import CompressionMethod
from .errors import PGPackMetadataCrcError
from .header import HEADER
from .metadata import (
    metadata_from_frame,
    metadata_reader,
)
from .offset import OffsetOpener
from .structs import PGParam

if TYPE_CHECKING:
    from lz4.frame import LZ4FrameFile
    from zstandard import ZstdCompressionWriter


NAN2NONE = {float("nan"): None}


class PGPackWriter:
    """Class for write PGPack format."""

    fileobj: BufferedWriter
    compression_method: CompressionMethod
    columns: list[str]
    pgtypes: list[PGOid]
    pgparam: list[PGParam]
    metadata_end: int
    fileobj_end: int
    pgcopy_compressed_length: int
    pgcopy_data_length: int
    _str: Optional[str]

    def __init__(
        self,
        fileobj: BufferedWriter,
        compression_method: CompressionMethod = CompressionMethod.LZ4,
    ) -> None:
        """Class initialization."""

        self.fileobj = fileobj
        self.compression_method = compression_method
        self.columns = []
        self.pgtypes = []
        self.pgparam = []
        self.metadata_end = 0
        self.fileobj_end = 0
        self.pgcopy_compressed_length = 0
        self.pgcopy_data_length = -1
        self._str = None

        self.fileobj.seek(0)
        self.fileobj.write(HEADER)

    def write_metadata(
        self,
        metadata: bytes,
    ) -> int:
        """Make blocks with metadata."""

        metadata_zlib: bytes = compress(metadata)
        metadata_crc: bytes = pack("!L", crc32(metadata_zlib))
        metadata_length: bytes = pack("!L", len(metadata_zlib))

        self.fileobj.write(metadata_crc)
        self.fileobj.write(metadata_length)
        self.fileobj.write(metadata_zlib)
        self.fileobj.flush()

        self.metadata_end = len(metadata_zlib) + 16
        self.columns, self.pgtypes, self.pgparam = metadata_reader(metadata)
        self._str = None

        return self.metadata_end

    def write_pgcopy(
        self,
        pgcopy: BufferedReader,
    ) -> int:
        """Make blocks with pgcopy."""

        if not self.metadata_end:
            raise PGPackMetadataCrcError()

        compression_method: bytes = pack("!B", self.compression_method.value)

        self.fileobj.seek(self.metadata_end)
        self.fileobj.write(compression_method)
        self.fileobj.write(bytes(16))  # write empty data for correction later

        offset_opener = OffsetOpener(self.fileobj)
        pgcopy_writer: Union[
            OffsetOpener,
            LZ4FrameFile,
            ZstdCompressionWriter,
        ] = pgcopy_compressor(
            offset_opener,
            self.compression_method,
        )

        if hasattr(pgcopy, "copy_reader"):
            for data in pgcopy.copy_reader():
                pgcopy_writer.write(data)
        else:
            pgcopy_writer.write(pgcopy.read())

        if not isinstance(pgcopy_writer, OffsetOpener):
            pgcopy_writer.close()

        self.pgcopy_compressed_length: int = offset_opener.tell()
        self.pgcopy_data_length: int = pgcopy.tell()
        self.fileobj_end: int = self.fileobj.tell()

        self.fileobj.seek(self.metadata_end + 1)
        self.fileobj.write(
            pack("!2Q", self.pgcopy_compressed_length, self.pgcopy_data_length)
        )
        self.fileobj.flush()
        self._str = None

        return self.fileobj_end

    def write(
        self,
        metadata: bytes,
        pgcopy: BufferedReader,
    ) -> int:
        """Write PGPack file."""

        self.write_metadata(metadata)
        self.write_pgcopy(pgcopy)
        self.fileobj.close()

        return self.fileobj_end

    def from_python(
        self,
        dtype_data: list[list[Any]],
    ) -> None:
        """Write PGPack file from python objects."""

        if not self.metadata_end:
            raise PGPackMetadataCrcError()

        compression_method: bytes = pack("!B", self.compression_method.value)

        self.fileobj.seek(self.metadata_end)
        self.fileobj.write(compression_method)
        self.fileobj.write(bytes(16))  # write empty data for correction later

        offset_opener = OffsetOpener(self.fileobj)
        compressor: Union[
            OffsetOpener,
            LZ4FrameFile,
            ZstdCompressionWriter,
        ] = pgcopy_compressor(
            offset_opener,
            self.compression_method,
        )
        pgcopy_writer = PGCopyWriter(
            compressor,
            pgtypes=self.pgtypes,
        )
        pgcopy_writer.write(dtype_data)
        pgcopy_writer.finalize()

        self.pgcopy_compressed_length: int = offset_opener.tell()
        self.pgcopy_data_length: int = pgcopy_writer.tell()
        self.fileobj_end: int = self.fileobj.tell()

        self.fileobj.seek(self.metadata_end + 1)
        self.fileobj.write(
            pack("!2Q", self.pgcopy_compressed_length, self.pgcopy_data_length)
        )
        self.fileobj.flush()
        self._str = None

        return self.fileobj_end

    def from_pandas(
        self,
        data_frame: PdFrame,
    ) -> None:
        """Write PGPack file from pandas.DataFrame."""

        if not self.metadata_end:
            self.write_metadata(metadata_from_frame(data_frame))

        return self.from_python([[
            NAN2NONE.get(
                data_value,
                int(data_value)
                if self.pgtypes[column] in (
                    PGOid.int2,
                    PGOid.int4,
                    PGOid.int8,
                    PGOid.oid,
                )
                else data_value,
            )
            for column, data_value in enumerate(data_values)
        ] for data_values in data_frame.values])

    def from_polars(
        self,
        data_frame: PlFrame,
    ) -> None:
        """Write PGPack file from polars.DataFrame."""

        if not self.metadata_end:
            self.write_metadata(metadata_from_frame(data_frame))

        return self.from_python(data_frame.iter_rows())

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
