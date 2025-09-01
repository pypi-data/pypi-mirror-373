from uuid import UUID

from ..enums import PGOid
from .nullables import (
    read_nullable,
    write_nullable,
)


@read_nullable
def to_uuid(binary_data: bytes) -> UUID:
    """Unpack uuid value."""

    return UUID(bytes=binary_data)


@write_nullable
def from_uuid(dtype_value: UUID, pg_oid: PGOid) -> bytes:
    """Pack uuid value."""

    return dtype_value.bytes
