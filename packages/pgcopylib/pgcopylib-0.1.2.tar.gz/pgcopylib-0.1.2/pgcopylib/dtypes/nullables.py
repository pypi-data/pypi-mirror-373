from struct import pack
from types import (
    FunctionType,
    NoneType,
)
from typing import (
    Any,
    Optional,
)

from ..constants import NULLABLE
from ..enums import PGOid


def read_nullable(to_dtype: FunctionType):
    """Decorator for read None value."""

    def wrapper(binary_data: Optional[bytes]) -> Optional[Any]:

        if isinstance(binary_data, NoneType):
            return

        return to_dtype(binary_data)

    return wrapper


def write_nullable(from_dtype: FunctionType):
    """Decorator for write None value and data with length."""

    def wrapper(dtype_value: Optional[Any], pg_oid: PGOid) -> bytes:

        if isinstance(dtype_value, NoneType):
            return NULLABLE

        data: bytes = from_dtype(dtype_value, pg_oid)
        len_data: int = len(data)
        return pack(f"!I{len_data}s", len_data, data)

    return wrapper
