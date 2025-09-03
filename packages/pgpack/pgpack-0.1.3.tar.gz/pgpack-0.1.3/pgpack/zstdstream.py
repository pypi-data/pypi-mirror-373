from io import (
    BufferedReader,
    BufferedWriter,
    BytesIO,
    UnsupportedOperation,
)
from os import (
    SEEK_SET,
    SEEK_CUR,
    SEEK_END,
)

from zstandard import (
    ZstdCompressor,
    ZstdCompressionWriter,
    ZstdDecompressor,
    ZstdError,
)
from zstandard.backend_cffi import (
    DECOMPRESSION_RECOMMENDED_OUTPUT_SIZE,
    DECOMPRESSION_RECOMMENDED_INPUT_SIZE,
    FORMAT_ZSTD1,
)
from zstandard._cffi import ( # type: ignore
    ffi,
    lib,
)

from .errors import PGPackModeError


def _zstd_error(zresult):
    return ffi.string(lib.ZSTD_getErrorName(zresult)).decode("utf-8")


class ZstdDecompressionReader:
    """ZSTD compression reader with full seek support."""

    def __init__(
            self,
            decompressor: ZstdDecompressor,
            source: BufferedReader,
            read_size: int,
            read_across_frames: bool,
            closefd: bool = False,
    ):
        """Class initialized."""

        self._decompressor = decompressor
        self._source = source
        self._read_size = read_size
        self._read_across_frames = bool(read_across_frames)
        self._closefd = bool(closefd)
        self._entered = False
        self._closed = False
        self._bytes_decompressed = 0
        self._finished_input = False
        self._finished_output = False
        self._in_buffer = ffi.new("ZSTD_inBuffer *")
        self._source_buffer = None

    def __enter__(self):
        if self._entered:
            raise ValueError("cannot __enter__ multiple times")

        if self._closed:
            raise ValueError("stream is closed")

        self._entered = True
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self._entered = False
        self._decompressor = None
        self.close()
        self._source = None

        return False

    def reinit(self) -> None:
        """Reinitialized class."""

        self._source.seek(0)
        self._decompressor._ensure_dctx()
        self._bytes_decompressed = 0
        self._finished_input = False
        self._finished_output = False
        self._in_buffer = ffi.new("ZSTD_inBuffer *")
        self._source_buffer = None

    def readable(self):
        return True

    def writable(self):
        return False

    def seekable(self):
        return False

    def readline(self, size=-1):  # noqa: ARG002
        raise UnsupportedOperation()

    def readlines(self, hint=-1):  # noqa: ARG002
        raise UnsupportedOperation()

    def write(self, data):  # noqa: ARG002
        raise UnsupportedOperation()

    def writelines(self, lines):  # noqa: ARG002
        raise UnsupportedOperation()

    def isatty(self):
        return False

    def flush(self):
        return None

    def close(self):
        if self._closed:
            return

        self._closed = True

        f = getattr(self._source, "close", None)
        if self._closefd and f:
            f()

    @property
    def closed(self):
        return self._closed

    def tell(self):
        return self._bytes_decompressed

    def readall(self):
        chunks = BytesIO()

        while True:
            chunk = self.read(1048576)
            if not chunk:
                break

            chunks.write(chunk)

        return chunks.getvalue()

    def __iter__(self):
        raise UnsupportedOperation()

    def __next__(self):
        raise UnsupportedOperation()

    next = __next__

    def _read_input(self):

        if self._in_buffer.pos < self._in_buffer.size:
            return

        if self._finished_input:
            return

        if hasattr(self._source, "read"):
            data = self._source.read(self._read_size)

            if not data:
                self._finished_input = True
                return

            self._source_buffer = ffi.from_buffer(data)
            self._in_buffer.src = self._source_buffer
            self._in_buffer.size = len(self._source_buffer)
            self._in_buffer.pos = 0
        else:
            self._source_buffer = ffi.from_buffer(self._source)
            self._in_buffer.src = self._source_buffer
            self._in_buffer.size = len(self._source_buffer)
            self._in_buffer.pos = 0

    def _decompress_into_buffer(self, out_buffer):
        """Decompress available input into an output buffer.

        Returns True if data in output buffer should be emitted.
        """
        zresult = lib.ZSTD_decompressStream(
            self._decompressor._dctx, out_buffer, self._in_buffer
        )

        if self._in_buffer.pos == self._in_buffer.size:
            self._in_buffer.src = ffi.NULL
            self._in_buffer.pos = 0
            self._in_buffer.size = 0
            self._source_buffer = None

            if not hasattr(self._source, "read"):
                self._finished_input = True

        if lib.ZSTD_isError(zresult):
            raise ZstdError("zstd decompress error: %s" % _zstd_error(zresult))

        return out_buffer.pos and (
                out_buffer.pos == out_buffer.size
                or zresult == 0
                and not self._read_across_frames
        )

    def read(self, size=-1):
        if self._closed:
            raise ValueError("stream is closed")

        if size < -1:
            raise ValueError("cannot read negative amounts less than -1")

        if size == -1:
            return self.readall()

        if self._finished_output or size == 0:
            return b""

        dst_buffer = ffi.new("char[]", size)
        out_buffer = ffi.new("ZSTD_outBuffer *")
        out_buffer.dst = dst_buffer
        out_buffer.size = size
        out_buffer.pos = 0

        self._read_input()
        if self._decompress_into_buffer(out_buffer):
            self._bytes_decompressed += out_buffer.pos
            return ffi.buffer(out_buffer.dst, out_buffer.pos)[:]

        while not self._finished_input:
            self._read_input()
            if self._decompress_into_buffer(out_buffer):
                self._bytes_decompressed += out_buffer.pos
                return ffi.buffer(out_buffer.dst, out_buffer.pos)[:]

        self._bytes_decompressed += out_buffer.pos
        return ffi.buffer(out_buffer.dst, out_buffer.pos)[:]

    def readinto(self, b):
        if self._closed:
            raise ValueError("stream is closed")

        if self._finished_output:
            return 0

        dest_buffer = ffi.from_buffer(b)
        ffi.memmove(b, b"", 0)
        out_buffer = ffi.new("ZSTD_outBuffer *")
        out_buffer.dst = dest_buffer
        out_buffer.size = len(dest_buffer)
        out_buffer.pos = 0

        self._read_input()
        if self._decompress_into_buffer(out_buffer):
            self._bytes_decompressed += out_buffer.pos
            return out_buffer.pos

        while not self._finished_input:
            self._read_input()
            if self._decompress_into_buffer(out_buffer):
                self._bytes_decompressed += out_buffer.pos
                return out_buffer.pos

        self._bytes_decompressed += out_buffer.pos
        return out_buffer.pos

    def read1(self, size=-1):
        if self._closed:
            raise ValueError("stream is closed")

        if size < -1:
            raise ValueError("cannot read negative amounts less than -1")

        if self._finished_output or size == 0:
            return b""

        if size == -1:
            size = DECOMPRESSION_RECOMMENDED_OUTPUT_SIZE

        dst_buffer = ffi.new("char[]", size)
        out_buffer = ffi.new("ZSTD_outBuffer *")
        out_buffer.dst = dst_buffer
        out_buffer.size = size
        out_buffer.pos = 0

        while not self._finished_input:
            self._read_input()
            self._decompress_into_buffer(out_buffer)

            if out_buffer.pos:
                break

        self._bytes_decompressed += out_buffer.pos
        return ffi.buffer(out_buffer.dst, out_buffer.pos)[:]

    def readinto1(self, b):
        if self._closed:
            raise ValueError("stream is closed")

        if self._finished_output:
            return 0

        dest_buffer = ffi.from_buffer(b)
        ffi.memmove(b, b"", 0)

        out_buffer = ffi.new("ZSTD_outBuffer *")
        out_buffer.dst = dest_buffer
        out_buffer.size = len(dest_buffer)
        out_buffer.pos = 0

        while not self._finished_input and not self._finished_output:
            self._read_input()
            self._decompress_into_buffer(out_buffer)

            if out_buffer.pos:
                break

        self._bytes_decompressed += out_buffer.pos
        return out_buffer.pos

    def seek(
        self,
        pos: int,
        whence: int = SEEK_SET,
    ) -> int:

        if self._closed:
            raise ValueError("stream is closed")

        read_amount = 0

        if whence == SEEK_SET:

            if pos < 0:
                raise OSError("cannot seek to negative position with SEEK_SET")

            if pos == self._bytes_decompressed:
                return pos

            if pos < self._bytes_decompressed:
                self.reinit()
                return self.seek(pos, whence)

            read_amount = pos - self._bytes_decompressed

        elif whence == SEEK_CUR:
            if pos < 0:
                self.reinit()
                return self.seek(pos, whence)

            read_amount = pos

        elif whence == SEEK_END:
            result = self.read(DECOMPRESSION_RECOMMENDED_OUTPUT_SIZE)

            while result:
                result = self.read(DECOMPRESSION_RECOMMENDED_OUTPUT_SIZE)

        while read_amount:
            result = self.read(
                min(read_amount, DECOMPRESSION_RECOMMENDED_OUTPUT_SIZE)
            )

            if not result:
                break

            read_amount -= len(result)

        return self._bytes_decompressed


class CustomZstdDecompressor(ZstdDecompressor):
    """Recompile class."""

    def __init__(
        self,
        dict_data=None,
        max_window_size=0,
        format=FORMAT_ZSTD1,
    ) -> None:

        super().__init__(dict_data, max_window_size, format)

        self._dict_data = dict_data
        self._max_window_size = max_window_size
        self._format = format

        dctx = lib.ZSTD_createDCtx()
        if dctx == ffi.NULL:
            raise MemoryError()

        self._dctx = dctx

        try:
            self._ensure_dctx()
        finally:
            self._dctx = ffi.gc(
                dctx, lib.ZSTD_freeDCtx, size=lib.ZSTD_sizeof_DCtx(dctx)
            )

    def stream_reader(
            self,
            source,
            read_size=DECOMPRESSION_RECOMMENDED_INPUT_SIZE,
            read_across_frames=False,
            closefd=True,
    ):
        """Redefine to custom ZstdDecompressionReader."""

        self._ensure_dctx()
        return ZstdDecompressionReader(
            self, source, read_size, read_across_frames, closefd=closefd
        )

    def _ensure_dctx(self, load_dict=True):
        lib.ZSTD_DCtx_reset(self._dctx, lib.ZSTD_reset_session_only)

        if self._max_window_size:
            zresult = lib.ZSTD_DCtx_setMaxWindowSize(
                self._dctx, self._max_window_size
            )
            if lib.ZSTD_isError(zresult):
                raise ZstdError(
                    "unable to set max window size: %s" % _zstd_error(zresult)
                )

        zresult = lib.ZSTD_DCtx_setParameter(
            self._dctx, lib.ZSTD_d_format, self._format
        )
        if lib.ZSTD_isError(zresult):
            raise ZstdError(
                "unable to set decoding format: %s" % _zstd_error(zresult)
            )

        if self._dict_data and load_dict:
            zresult = lib.ZSTD_DCtx_refDDict(
                self._dctx,
                self._dict_data._ddict,
            )
            if lib.ZSTD_isError(zresult):
                raise ZstdError(
                    "unable to reference prepared dictionary: %s"
                    % _zstd_error(zresult)
                )


def zstd_file(
    fileobj: BufferedReader | BufferedWriter,
    mode: str = "rb",
) -> ZstdDecompressionReader | ZstdCompressionWriter:
    """ZSTD stream reader/writer."""

    if mode not in ("rb", "rb+", "wb"):
        raise PGPackModeError()

    closefd: bool = False
    ctx: CustomZstdDecompressor | ZstdCompressor = {
        "rb": CustomZstdDecompressor,
        "rb+": ZstdCompressor,
        "wb": ZstdCompressor,
    }[mode]()

    if mode == "rb":
        return ctx.stream_reader(fileobj, closefd=closefd)

    return ctx.stream_writer(fileobj, closefd=closefd)
