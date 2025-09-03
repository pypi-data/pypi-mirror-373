from typing_extensions import Buffer
from collections.abc import Iterable
from io import (
    BufferedReader,
    BufferedWriter,
    RawIOBase,
)


class OffsetOpener:
    """Class for read from offset."""

    def __init__(
        self,
        fileobj: BufferedReader | BufferedWriter,
    ) -> None:
        """Class initialization."""

        self.fileobj = fileobj
        self.offset = self.fileobj.tell()
        self.fileobj.seek(self.offset)

    def __hash__(self) -> int:
        """OffsetOpener hash exploit."""

        return self.fileobj.__hash__()

    def __enter__(self) -> "OffsetOpener":
        """OffsetOpener __enter__ exploit."""

        return self

    def __exit__(
        self,
        exc_type: object,
        exc_value: object,
        exc_tb: object,
    ) -> bool:
        """OffsetOpener __exit__ exploit."""

        return self.fileobj.__exit__(
            exc_type,
            exc_value,
            exc_tb,
        )

    @property
    def __class__(self) -> BufferedReader | BufferedWriter:
        """OffsetOpener class exploit."""

        return self.fileobj.__class__

    @property
    def raw(self) -> RawIOBase:
        return self.fileobj.raw

    @property
    def name(self) -> str:
        return self.fileobj.name

    @property
    def mode(self) -> str:
        return self.fileobj.mode

    @property
    def closed(self) -> bool:
        return self.fileobj.closed

    def read(self, size: int = -1) -> bytes:
        return self.fileobj.read(size)

    def read1(self, size: int = -1) -> bytes:
        return self.fileobj.read1(size)

    def readline(self, size: int = -1) -> bytes:
        return self.fileobj.readline(size)

    def readlines(self, hint: int = -1) -> list[bytes]:
        return self.fileobj.readlines(hint)

    def write(self, buffer: Buffer) -> int:
        return self.fileobj.write(buffer)

    def writelines(self, lines: Iterable[Buffer]) -> None:
        self.fileobj.writelines(lines)

    def flush(self) -> None:
        return self.fileobj.flush()

    def seek(self, target: int, whence: int = 0) -> int:
        if target == 0 and whence == 2:
            return self.fileobj.seek(target, whence) - self.offset
        if whence == 0:
            return self.fileobj.seek(target + self.offset)

    def peek(self, size: int = 0) -> bytes:
        return self.fileobj.peek(size)

    def truncate(self, pos: int | None = None) -> int:
        return self.fileobj.truncate(pos)

    def tell(self) -> int:
        return self.fileobj.tell() - self.offset

    def close(self) -> None:
        self.fileobj.close()

    def readable(self) -> bool:
        return self.fileobj.readable()

    def writable(self) -> bool:
        return self.fileobj.writable()

    def seekable(self) -> bool:
        return self.fileobj.seekable()

    def readinto(self, buffer: Buffer) -> int:
        return self.fileobj.readinto(buffer)

    def readinto1(self, buffer: Buffer) -> int:
        return self.fileobj.readinto1(buffer)

    def isatty(self) -> bool:
        return self.fileobj.isatty()

    def fileno(self) -> int:
        return self.fileobj.fileno()

    def detach(self) -> RawIOBase:
        return self.fileobj.detach()
