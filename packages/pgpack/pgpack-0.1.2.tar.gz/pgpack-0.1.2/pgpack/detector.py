from datetime import (
    date,
    datetime,
    time,
)
from dateutil.relativedelta import relativedelta
from decimal import Decimal
from ipaddress import (
    IPv4Address,
    IPv4Network,
    IPv6Address,
    IPv6Network,
)
from typing import (
    Any,
    Union,
)
from types import NoneType
from uuid import UUID


AssociatePyType: dict[Any, int] = {
    bool: (16, 1000),
    bytes: (17, 1001),
    Union[IPv4Network, IPv6Network]: (650, 651),
    date: (1082, 1182),
    float: (701, 1022),
    Union[IPv4Address, IPv6Address]: (869, 1041),
    int: (20, 1016),
    relativedelta: (1186, 1187),
    dict: (114, 199),
    Decimal: (1700, 1231),
    str: (25, 1009),
    time: (1083, 1183),
    datetime: (1114, 1115),
    UUID: (2950, 2951),
}


def detect_oid(data_values: Any, is_array: bool = False) -> int:
    """Associate python type with postgres type."""

    for value in data_values:
        if isinstance(value, list):
            pg_type = detect_oid(value, True)
            if pg_type:
                return pg_type
            continue
        if not isinstance(value, NoneType):
            if is_array:
                return AssociatePyType[value.__class__][1]
            return AssociatePyType[value.__class__][0]
