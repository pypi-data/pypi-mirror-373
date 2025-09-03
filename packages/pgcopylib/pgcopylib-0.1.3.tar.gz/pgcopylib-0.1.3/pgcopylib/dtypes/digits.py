from decimal import Decimal, ROUND_HALF_UP
from struct import (
    pack,
    unpack,
    unpack_from,
)

from ..enums import PGOid
from .nullables import (
    read_nullable,
    write_nullable,
)


@read_nullable
def to_bool(binary_data: bytes) -> bool:
    """Unpack bool value."""

    return unpack("!?", binary_data)[0]


@write_nullable
def from_bool(dtype_value: bool, pg_oid: PGOid) -> bytes:
    """Pack bool value."""

    return pack("!?", dtype_value)


@read_nullable
def to_oid(binary_data: bytes) -> int:
    """Unpack oid value."""

    return unpack("!I", binary_data)[0]


@write_nullable
def from_oid(dtype_value: int, pg_oid: PGOid) -> bytes:
    """Pack oid value."""

    return pack("!I", dtype_value)


@read_nullable
def to_serial2(binary_data: bytes) -> int:
    """Unpack serial2 value."""

    return unpack("!H", binary_data)[0]


@write_nullable
def from_serial2(dtype_value: int, pg_oid: PGOid) -> bytes:
    """Pack serial2 value."""

    return pack("!H", dtype_value)


@read_nullable
def to_serial4(binary_data: bytes) -> int:
    """Unpack serial4 value."""

    return unpack("!L", binary_data)[0]


@write_nullable
def from_serial4(dtype_value: int, pg_oid: PGOid) -> bytes:
    """Pack serial4 value."""

    return pack("!L", dtype_value)


@read_nullable
def to_serial8(binary_data: bytes) -> int:
    """Unpack serial8 value."""

    return unpack("!Q", binary_data)[0]


@write_nullable
def from_serial8(dtype_value: int, pg_oid: PGOid) -> bytes:
    """Pack serial8 value."""

    return pack("!Q", dtype_value)


@read_nullable
def to_int2(binary_data: bytes) -> int:
    """Unpack int2 value."""

    return unpack("!h", binary_data)[0]


@write_nullable
def from_int2(dtype_value: int, pg_oid: PGOid) -> bytes:
    """Pack int2 value."""

    return pack("!h", dtype_value)


@read_nullable
def to_int4(binary_data: bytes) -> int:
    """Unpack int4 value."""

    return unpack("!l", binary_data)[0]


@write_nullable
def from_int4(dtype_value: int, pg_oid: PGOid) -> bytes:
    """Pack int4 value."""

    return pack("!l", dtype_value)


@read_nullable
def to_int8(binary_data: bytes) -> int:
    """Unpack int8 value."""

    return unpack("!q", binary_data)[0]


@write_nullable
def from_int8(dtype_value: int, pg_oid: PGOid) -> bytes:
    """Pack int8 value."""

    return pack("!q", dtype_value)


@read_nullable
def to_money(binary_data: bytes) -> float:
    """Unpack money value."""

    return to_int8(binary_data) * 0.01


@write_nullable
def from_money(dtype_value: float, pg_oid: PGOid) -> bytes:
    """Pack money value."""

    return from_int8(int(dtype_value / 0.01))


@read_nullable
def to_float4(binary_data: bytes) -> float:
    """Unpack float4 value."""

    return unpack("!f", binary_data)[0]


@write_nullable
def from_float4(dtype_value: float, pg_oid: PGOid) -> bytes:
    """Pack float4 value."""

    return pack("!f", dtype_value)


@read_nullable
def to_float8(binary_data: bytes) -> float:
    """Unpack float8 value."""

    return unpack("!d", binary_data)[0]


@write_nullable
def from_float8(dtype_value: float, pg_oid: PGOid) -> bytes:
    """Pack float8 value."""

    return pack("!d", dtype_value)


@read_nullable
def to_numeric(binary_data: bytes) -> Decimal:
    """Unpack numeric value."""

    ndigits, weight, sign, dscale = unpack_from(
        "!hhhh",
        binary_data,
    )

    if sign == 0xc000:
        return Decimal("nan")

    is_negative: bool = sign == 0x4000
    digits: list[int] = [
        unpack_from("!h", binary_data[i:i + 2])[-1]
        for i in range(8, 8 + ndigits * 2, 2)
    ]

    numeric = Decimal(0)
    scale = Decimal(10) ** -dscale

    for pos, digit in enumerate(digits):
        power = Decimal(4) * (Decimal(weight) - Decimal(pos))
        term = Decimal(digit) * (Decimal(10) ** power)
        numeric += term

    if is_negative:
        numeric *= -1

    return numeric.quantize(scale)


@write_nullable
def from_numeric(dtype_value: Decimal, pg_oid: PGOid) -> bytes:
    """Pack numeric value."""

    if dtype_value.is_nan():
        return pack("!hhhh", 0, 0, 0xC000, 0)

    is_negative: bool = dtype_value < 0
    sign: int = 0x4000 if is_negative else 0x00000

    if dtype_value == 0:
        return pack("!hhhh", 0, 0, sign, 0)

    abs_value: Decimal = abs(dtype_value)
    as_tuple = abs_value.as_tuple()
    dscale: int = abs(as_tuple.exponent) if as_tuple.exponent < 0 else 0
    scaled_value: Decimal = abs_value * (Decimal(10) ** dscale)
    int_value = int(scaled_value.to_integral_value(rounding=ROUND_HALF_UP))

    base = 10000
    digits = []
    temp = int_value

    while temp > 0:
        digits.append(temp % base)
        temp //= base

    if not digits:
        digits = [0]

    digits.reverse()
    ndigits = len(digits)
    weight = (len(str(int_value)) - 1) // 4
    header = pack("!hhhh", ndigits, weight, sign, dscale)
    digits_data = b''.join(pack("!h", digit) for digit in digits)

    return header + digits_data
