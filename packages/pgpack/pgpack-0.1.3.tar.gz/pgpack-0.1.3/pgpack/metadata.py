from json import (
    dumps,
    loads,
)

from pandas import DataFrame as PdFrame
from polars import DataFrame as PlFrame
from pgcopylib import PGOid

from .detector import detect_oid
from .structs import PGParam


def metadata_reader(metadata: bytes) -> tuple[
    list[str],
    list[PGOid],
    list[PGParam],
]:
    """Read columns and data types from unpacked metadata."""

    metadata_info: list[list[int, list[str, int]]] = loads(metadata)
    columns_data: dict[int, list[str, int]] = {
        column: name_dtype_ps
        for column, name_dtype_ps in metadata_info
    }
    num_columns: int = len(columns_data)

    return [
        columns_data[num_column][0]
        for num_column in range(1, num_columns + 1)
    ], [
        PGOid(columns_data[num_column][1])
        for num_column in range(1, num_columns + 1)
    ], [
        PGParam(*columns_data[num_column][2:])
        for num_column in range(1, num_columns + 1)
    ]


def metadata_from_frame(frame: PdFrame | PlFrame) -> bytes:
    """Generate metadata from pandas.DataFrame | polars.DataFrame."""

    return dumps(
        list(enumerate(map(
                lambda column: (str(column), *detect_oid(frame[column])),
                frame.columns,
            ),
            start=1,
        )),
        ensure_ascii=False,
    ).encode("utf-8")
