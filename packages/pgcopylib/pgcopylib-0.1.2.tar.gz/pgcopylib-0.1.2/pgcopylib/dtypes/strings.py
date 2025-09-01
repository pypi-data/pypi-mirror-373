from struct import unpack

from ..enums import PGOid
from .nullables import (
    read_nullable,
    write_nullable,
)


@read_nullable
def to_text(binary_data: bytes) -> str:
    """Unpack text value."""

    return binary_data.decode("utf-8", errors="replace")


@write_nullable
def from_text(dtype_value: str, pg_oid: PGOid) -> bytes:
    """Pack text value."""

    return dtype_value.encode("utf-8")


@read_nullable
def to_macaddr(binary_data: bytes) -> str:
    """Unpack macaddr and macaddr8 value."""

    return ":".join(
        f"{byte:02x}"
        for byte in unpack(
            f"!{len(binary_data)}B",
            binary_data,
        )
    ).upper()


@write_nullable
def from_macaddr(dtype_value: str, pg_oid: PGOid) -> bytes:
    """Pack macaddr and macaddr8 value."""

    return bytes.fromhex(dtype_value.replace(":", ""))


@read_nullable
def to_bits(binary_data: bytes) -> str:
    """Unpack bit and varbit value."""

    length, bit_data = unpack(
        f"!I{len(binary_data) - 4}s",
        binary_data,
    )

    return "".join(
        str((byte >> i) & 1)
        for byte in bit_data
        for i in range(7, -1, -1)
    )[:length]


@write_nullable
def from_bits(dtype_value: str, pg_oid: PGOid) -> bytes:
    """Pack bit and varbit value."""

    return int(dtype_value, 2).to_bytes(
        (len(dtype_value) + 7) // 8, "big"
    )


@read_nullable
def to_bytea(binary_data: bytes) -> bytes:
    """Unpack bytea value."""

    return binary_data


@write_nullable
def from_bytea(dtype_value: bytes, pg_oid: PGOid) -> bytes:
    """Pack bytea value."""

    return dtype_value
