from struct import (
    pack,
    unpack,
)
from typing import Union

from ..enums import PGOid
from .nullables import (
    read_nullable,
    write_nullable,
)


@read_nullable
def to_point(binary_data: bytes) -> tuple[float, float]:
    """Unpack point value."""

    return unpack("!2d", binary_data)


@write_nullable
def from_point(dtype_value: tuple[float, float], pg_oid: PGOid) -> bytes:
    """Pack point value."""

    return pack("!2d", *dtype_value)


@read_nullable
def to_line(binary_data: bytes) -> tuple[float, float, float]:
    """Unpack line value."""

    return unpack("!3d", binary_data)


@write_nullable
def from_line(dtype_value: tuple[float, float, float], pg_oid: PGOid) -> bytes:
    """Pack line value."""

    return pack("!3d", *dtype_value)


@read_nullable
def to_circle(binary_data: bytes) -> tuple[float, float, float]:
    """Unpack circle value."""

    return to_line(binary_data)


@write_nullable
def from_circle(
    dtype_value: tuple[float, float, float],
    pg_oid: PGOid,
) -> bytes:
    """Pack circle value."""

    return from_line(dtype_value)


@read_nullable
def to_lseg(binary_data: bytes) -> list[tuple[float, float]]:
    """Unpack lseg value."""

    x1, y1, x2, y2 = unpack("!4d", binary_data)

    return [(x1, y1), (x2, y2)]


@write_nullable
def from_lseg(dtype_value: list[tuple[float, float]], pg_oid: PGOid) -> bytes:
    """Pack lseg value."""

    return pack("!4d", *dtype_value[0], *dtype_value[1])


@read_nullable
def to_box(binary_data: bytes) -> tuple[
    tuple[float, float],
    tuple[float, float],
]:
    """Unpack box value."""

    x1, y1, x2, y2 = unpack("!4d", binary_data)

    return (x1, y1), (x2, y2)


@write_nullable
def from_box(
    dtype_value: tuple[
        tuple[float, float],
        tuple[float, float],
    ],
    pg_oid: PGOid,
) -> bytes:
    """Pack box value."""

    return pack("!4d", *dtype_value[0], *dtype_value[1])


@read_nullable
def to_path(binary_data: bytes) -> Union[
    list[tuple[float, float]],
    tuple[tuple[float, float]],
]:
    """Unpack path value."""

    is_closed, length, *path_data = unpack(
        f"!?l{(len(binary_data) - 5) // 8}d",
        binary_data,
    )
    path_data = tuple(
        path_data[i:i + 2]
        for i in range(0, len(path_data), 2)
    )

    return {
        True: tuple,
        False: list,
    }[is_closed](
        path_data[i:i + length]
        for i in range(0, len(path_data), length)
    )


@write_nullable
def from_path(
    dtype_value: Union[
        list[tuple[float, float]],
        tuple[tuple[float, float]],
    ],
    pg_oid: PGOid,
) -> bytes:
    """Pack path value."""

    is_closed = isinstance(dtype_value, tuple)
    length = len(dtype_value)
    path_data = sum(dtype_value, ())

    return pack(
        f"!?l{len(path_data)}d",
        is_closed,
        length,
        *path_data
    )


@read_nullable
def to_polygon(binary_data: bytes) -> tuple[tuple[float, float]]:
    """Unpack polygon value."""

    length, *path_data = unpack(
        f"!l{(len(binary_data) - 4) // 8}d",
        binary_data,
    )
    path_data = tuple(
        path_data[i:i + 2]
        for i in range(0, len(path_data), 2)
    )

    return tuple(
        path_data[i:i + length]
        for i in range(0, len(path_data), length)
    )


@write_nullable
def from_polygon(
    dtype_value: tuple[tuple[float, float]],
    pg_oid: PGOid,
) -> bytes:
    """Pack polygon value."""

    length = len(dtype_value)
    path_data = sum(dtype_value, ())

    return pack(
        f"!l{len(path_data)}d",
        length,
        *path_data
    )
