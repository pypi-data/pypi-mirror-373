from io import BytesIO
from math import prod
from struct import (
    pack,
    unpack,
)
from typing import Any

from ..enums import (
    ArrayOidToOid,
    PGDataType,
    PGOid,
    PGOidToDType,
)
from ..errors import PGCopyOidNotSupportError
from ..reader import read_record
from ..structs import DTypeFunctions
from .dates import (
    from_date,
    from_interval,
    from_time,
    from_timestamp,
    from_timestamptz,
    from_timetz,
    to_date,
    to_interval,
    to_time,
    to_timestamp,
    to_timestamptz,
    to_timetz,
)
from .digits import (
    from_bool,
    from_float4,
    from_float8,
    from_int2,
    from_int4,
    from_int8,
    from_money,
    from_numeric,
    from_oid,
    from_serial2,
    from_serial4,
    from_serial8,
    to_bool,
    to_float4,
    to_float8,
    to_int2,
    to_int4,
    to_int8,
    to_money,
    to_numeric,
    to_oid,
    to_serial2,
    to_serial4,
    to_serial8,
)
from .geometrics import (
    from_box,
    from_circle,
    from_line,
    from_lseg,
    from_path,
    from_point,
    from_polygon,
    to_box,
    to_circle,
    to_line,
    to_lseg,
    to_path,
    to_point,
    to_polygon,
)
from .ipaddrs import (
    from_network,
    to_network,
)
from .jsons import (
    from_json,
    to_json,
)
from .nullables import (
    read_nullable,
    write_nullable,
)
from .strings import (
    from_bits,
    from_bytea,
    from_macaddr,
    from_text,
    to_bits,
    to_bytea,
    to_macaddr,
    to_text,
)
from .uuids import (
    from_uuid,
    to_uuid,
)


DtypeFunc: dict[PGDataType, DTypeFunctions] = {
    PGDataType.Bit: DTypeFunctions(to_bits, from_bits),
    PGDataType.Bool: DTypeFunctions(to_bool, from_bool),
    PGDataType.Box: DTypeFunctions(to_box, from_box),
    PGDataType.Bytes: DTypeFunctions(to_bytea, from_bytea),
    PGDataType.Cidr: DTypeFunctions(to_network, from_network),
    PGDataType.Circle: DTypeFunctions(to_circle, from_circle),
    PGDataType.Date: DTypeFunctions(to_date, from_date),
    PGDataType.Float4: DTypeFunctions(to_float4, from_float4),
    PGDataType.Float8: DTypeFunctions(to_float8, from_float8),
    PGDataType.Inet: DTypeFunctions(to_network, from_network),
    PGDataType.Int2: DTypeFunctions(to_int2, from_int2),
    PGDataType.Int4: DTypeFunctions(to_int4, from_int4),
    PGDataType.Int8: DTypeFunctions(to_int8, from_int8),
    PGDataType.Interval: DTypeFunctions(to_interval, from_interval),
    PGDataType.Json: DTypeFunctions(to_json, from_json),
    PGDataType.Line: DTypeFunctions(to_line, from_line),
    PGDataType.Lseg: DTypeFunctions(to_lseg, from_lseg),
    PGDataType.Macaddr8: DTypeFunctions(to_macaddr, from_macaddr),
    PGDataType.Macaddr: DTypeFunctions(to_macaddr, from_macaddr),
    PGDataType.Money: DTypeFunctions(to_money, from_money),
    PGDataType.Numeric: DTypeFunctions(to_numeric, from_numeric),
    PGDataType.Oid: DTypeFunctions(to_oid, from_oid),
    PGDataType.Path: DTypeFunctions(to_path, from_path),
    PGDataType.Point: DTypeFunctions(to_point, from_point),
    PGDataType.Polygon: DTypeFunctions(to_polygon, from_polygon),
    PGDataType.Serial2: DTypeFunctions(to_serial2, from_serial2),
    PGDataType.Serial4: DTypeFunctions(to_serial4, from_serial4),
    PGDataType.Serial8: DTypeFunctions(to_serial8, from_serial8),
    PGDataType.Text: DTypeFunctions(to_text, from_text),
    PGDataType.Time: DTypeFunctions(to_time, from_time),
    PGDataType.Timestamp: DTypeFunctions(to_timestamp, from_timestamp),
    PGDataType.Timestamptz: DTypeFunctions(to_timestamptz, from_timestamptz),
    PGDataType.Timetz: DTypeFunctions(to_timetz, from_timetz),
    PGDataType.Uuid: DTypeFunctions(to_uuid, from_uuid),
}


def recursive_elements(
    elements: list[Any],
    array_struct: list[int],
) -> list[Any]:
    """Recursive unpack array struct."""

    if len(array_struct) == 0:
        return elements

    chunk = array_struct.pop()

    if len(elements) == chunk:
        return recursive_elements(elements, array_struct)

    return recursive_elements(
        [
            elements[i:i + chunk]
            for i in range(0, len(elements), chunk)
        ],
        array_struct,
    )


def recursive_num_dim(
    type_values: list,
    num_dim: list,
) -> list[int]:

    if isinstance(type_values, list):
        num_dim.append(len(type_values))
        return recursive_num_dim(type_values[0], num_dim)
    return num_dim


@read_nullable
def to_array(binary_data: bytes) -> list[Any]:
    """Unpack array values."""

    buffer = BytesIO(binary_data)
    num_dim, _, oid = unpack("!3I", buffer.read(12))

    try:
        array_type = PGOid(oid)
    except ValueError:
        raise PGCopyOidNotSupportError("Oid not support.")

    to_dtype = DtypeFunc[PGOidToDType[array_type]].read
    array_struct = [
        unpack("!2I", buffer.read(8))[0]
        for _ in range(num_dim)
    ]
    elements = [
        to_dtype(read_record(buffer))
        for _ in range(prod(array_struct))
    ]

    return recursive_elements(
        elements,
        array_struct,
    )


@write_nullable
def from_array(dtype_value: list[Any], pg_oid: PGOid) -> bytes:
    """Pack array values."""

    num_dim: list[int] = recursive_num_dim(dtype_value, [])

    try:
        array_type = ArrayOidToOid[pg_oid]
    except ValueError:
        raise PGCopyOidNotSupportError("Oid not support.")

    while any(isinstance(value, list) for value in dtype_value):
        expand_values: list[Any] = []
        for value in dtype_value:
            if isinstance(value, list):
                expand_values.extend(value)
            else:
                expand_values.append(value)
        dtype_value = expand_values

    is_nullable: bool = None in dtype_value
    dimensions: list[int] = []
    [dimensions.extend([dim, 1]) for dim in num_dim]
    from_dtype = DtypeFunc[PGOidToDType[array_type]].write

    buffer = BytesIO()
    buffer.write(pack("!3I", len(num_dim), int(is_nullable), array_type.value))
    buffer.write(pack(f"!{len(dimensions)}I", *dimensions))
    [buffer.write(from_dtype(value, array_type)) for value in dtype_value]

    return buffer.getvalue()


AssociateDtypes: dict[PGDataType, DTypeFunctions] = {
    PGDataType.Array: DTypeFunctions(to_array, from_array),
    **DtypeFunc,
}
