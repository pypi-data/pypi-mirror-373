from json import (
    dumps,
    loads,
)
from typing import TypeAlias

from ..enums import PGOid
from .nullables import (
    read_nullable,
    write_nullable,
)


Json: TypeAlias = (
    dict[str, "Json"] | list["Json"] | str | int | float | bool | None
)


@read_nullable
def to_json(binary_data: bytes) -> Json:
    """Unpack json value."""

    return loads(binary_data)


@write_nullable
def from_json(dtype_value: Json, pg_oid: PGOid) -> bytes:
    """Pack json value."""

    return dumps(dtype_value, ensure_ascii=False).encode("utf-8")
