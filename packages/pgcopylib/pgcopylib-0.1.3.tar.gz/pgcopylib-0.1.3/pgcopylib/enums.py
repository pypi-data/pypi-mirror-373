from enum import Enum


class PGOid(Enum):
    """PGCopy OID Identifiers."""

    _bit = 1561
    _bool = 1000
    _box = 1020
    _bpchar = 1014
    _bytea = 1001
    _char = 1002
    _cidr = 651
    _circle = 719
    _date = 1182
    _float4 = 1021
    _float8 = 1022
    _inet = 1041
    _int2 = 1005
    _int4 = 1007
    _int8 = 1016
    _interval = 1187
    _json = 199
    _jsonb = 3807
    _line = 629
    _lseg = 1018
    _macaddr = 1040
    _macaddr8 = 775
    _money = 791
    _numeric = 1231
    _oid = 1028
    _path = 1019
    _point = 1017
    _polygon = 1027
    _text = 1009
    _time = 1183
    _timestamp = 1115
    _timestamptz = 1185
    _timetz = 1270
    _tsquery = 3645
    _tsvector = 3643
    _uuid = 2951
    _varbit = 1563
    _varchar = 1015
    _xml = 143
    bit = 1560
    bool = 16
    box = 603
    bpchar = 1042
    bytea = 17
    char = 18
    cidr = 650
    circle = 718
    date = 1082
    float4 = 700
    float8 = 701
    inet = 869
    int2 = 21
    int4 = 23
    int8 = 20
    interval = 1186
    json = 114
    jsonb = 3802
    line = 628
    lseg = 601
    macaddr = 829
    macaddr8 = 774
    money = 790
    numeric = 1700
    oid = 26
    path = 602
    point = 600
    polygon = 604
    text = 25
    time = 1083
    timestamp = 1114
    timestamptz = 1184
    timetz = 1266
    tsquery = 3615
    tsvector = 3614
    uuid = 2950
    varbit = 1562
    varchar = 1043
    xml = 142


class PGDataType(Enum):
    """PGCopy Data Types."""

    # Digits Types
    Bool = 100
    Float4 = 101
    Float8 = 102
    Int2 = 103
    Int4 = 104
    Int8 = 105
    Money = 106
    Numeric = 107
    Oid = 108
    Serial2 = 109
    Serial4 = 110
    Serial8 = 111
    # Geometric Types
    Box = 200
    Circle = 201
    Line = 202
    Lseg = 203
    Path = 204
    Point = 205
    Polygon = 206
    # Network Types
    Cidr = 300
    Inet = 301
    Macaddr = 302
    Macaddr8 = 303
    # Data Types
    Date = 400
    Interval = 401
    Timestamp = 402
    Timestamptz = 403
    Time = 404
    Timetz = 405
    # Text Type
    Json = 500
    Text = 501
    # Bynary Types
    Bit = 600
    Bytes = 601
    Uuid = 602
    # Array Type
    Array = 700


PGOidToDType: dict[PGOid, PGDataType] = {
    # Associate oid with data type.
    PGOid._bit: PGDataType.Array,
    PGOid._bool: PGDataType.Array,
    PGOid._box: PGDataType.Array,
    PGOid._bpchar: PGDataType.Array,
    PGOid._bytea: PGDataType.Array,
    PGOid._char: PGDataType.Array,
    PGOid._cidr: PGDataType.Array,
    PGOid._circle: PGDataType.Array,
    PGOid._date: PGDataType.Array,
    PGOid._float4: PGDataType.Array,
    PGOid._float8: PGDataType.Array,
    PGOid._inet: PGDataType.Array,
    PGOid._int2: PGDataType.Array,
    PGOid._int4: PGDataType.Array,
    PGOid._int8: PGDataType.Array,
    PGOid._interval: PGDataType.Array,
    PGOid._json: PGDataType.Array,
    PGOid._jsonb: PGDataType.Array,
    PGOid._line: PGDataType.Array,
    PGOid._lseg: PGDataType.Array,
    PGOid._macaddr: PGDataType.Array,
    PGOid._macaddr8: PGDataType.Array,
    PGOid._money: PGDataType.Array,
    PGOid._numeric: PGDataType.Array,
    PGOid._oid: PGDataType.Array,
    PGOid._path: PGDataType.Array,
    PGOid._point: PGDataType.Array,
    PGOid._polygon: PGDataType.Array,
    PGOid._text: PGDataType.Array,
    PGOid._time: PGDataType.Array,
    PGOid._timestamp: PGDataType.Array,
    PGOid._timestamptz: PGDataType.Array,
    PGOid._timetz: PGDataType.Array,
    PGOid._uuid: PGDataType.Array,
    PGOid._varbit: PGDataType.Array,
    PGOid._varchar: PGDataType.Array,
    PGOid._xml: PGDataType.Array,
    PGOid.bit: PGDataType.Bit,
    PGOid.bool: PGDataType.Bool,
    PGOid.box: PGDataType.Box,
    PGOid.bpchar: PGDataType.Text,
    PGOid.bytea: PGDataType.Bytes,
    PGOid.char: PGDataType.Text,
    PGOid.cidr: PGDataType.Cidr,
    PGOid.circle: PGDataType.Circle,
    PGOid.date: PGDataType.Date,
    PGOid.float4: PGDataType.Float4,
    PGOid.float8: PGDataType.Float8,
    PGOid.inet: PGDataType.Inet,
    PGOid.int2: PGDataType.Int2,
    PGOid.int4: PGDataType.Int4,
    PGOid.int8: PGDataType.Int8,
    PGOid.interval: PGDataType.Interval,
    PGOid.json: PGDataType.Json,
    PGOid.jsonb: PGDataType.Json,
    PGOid.line: PGDataType.Line,
    PGOid.lseg: PGDataType.Lseg,
    PGOid.macaddr: PGDataType.Macaddr,
    PGOid.macaddr8: PGDataType.Macaddr8,
    PGOid.money: PGDataType.Money,
    PGOid.numeric: PGDataType.Numeric,
    PGOid.oid: PGDataType.Oid,
    PGOid.path: PGDataType.Path,
    PGOid.point: PGDataType.Point,
    PGOid.polygon: PGDataType.Polygon,
    PGOid.text: PGDataType.Text,
    PGOid.time: PGDataType.Time,
    PGOid.timestamp: PGDataType.Timestamp,
    PGOid.timestamptz: PGDataType.Timestamptz,
    PGOid.timetz: PGDataType.Timetz,
    PGOid.uuid: PGDataType.Uuid,
    PGOid.varbit: PGDataType.Bit,
    PGOid.varchar: PGDataType.Text,
    PGOid.xml: PGDataType.Text,
}


ArrayOidToOid: dict[PGOid, PGOid] = {
    PGOid._bit: PGOid.bit,
    PGOid._bool: PGOid.bool,
    PGOid._box: PGOid.box,
    PGOid._bpchar: PGOid.bpchar,
    PGOid._bytea: PGOid.bytea,
    PGOid._char: PGOid.char,
    PGOid._cidr: PGOid.cidr,
    PGOid._circle: PGOid.circle,
    PGOid._date: PGOid.date,
    PGOid._float4: PGOid.float4,
    PGOid._float8: PGOid.float8,
    PGOid._inet: PGOid.inet,
    PGOid._int2: PGOid.int2,
    PGOid._int4: PGOid.int4,
    PGOid._int8: PGOid.int8,
    PGOid._interval: PGOid.interval,
    PGOid._json: PGOid.json,
    PGOid._jsonb: PGOid.jsonb,
    PGOid._line: PGOid.line,
    PGOid._lseg: PGOid.lseg,
    PGOid._macaddr: PGOid.macaddr,
    PGOid._macaddr8: PGOid.macaddr8,
    PGOid._money: PGOid.money,
    PGOid._numeric: PGOid.numeric,
    PGOid._oid: PGOid.oid,
    PGOid._path: PGOid.path,
    PGOid._point: PGOid.point,
    PGOid._polygon: PGOid.polygon,
    PGOid._text: PGOid.text,
    PGOid._time: PGOid.time,
    PGOid._timestamp: PGOid.timestamp,
    PGOid._timestamptz: PGOid.timestamptz,
    PGOid._timetz: PGOid.timetz,
    PGOid._uuid: PGOid.uuid,
    PGOid._varbit: PGOid.varbit,
    PGOid._varchar: PGOid.varchar,
    PGOid._xml: PGOid.xml,
}


PGDataTypeLength: dict[PGDataType, int] = {
    # Length for current data type.
    PGDataType.Array: -1,
    PGDataType.Bit: -1,
    PGDataType.Bool: 1,
    PGDataType.Box: 32,
    PGDataType.Bytes: -1,
    PGDataType.Cidr: -1,
    PGDataType.Circle: 24,
    PGDataType.Date: 4,
    PGDataType.Float4: 4,
    PGDataType.Float8: 8,
    PGDataType.Inet: -1,
    PGDataType.Int2: 2,
    PGDataType.Int4: 4,
    PGDataType.Int8: 8,
    PGDataType.Interval: 16,
    PGDataType.Json: -1,
    PGDataType.Line: 24,
    PGDataType.Lseg: 32,
    PGDataType.Macaddr8: 8,
    PGDataType.Macaddr: 6,
    PGDataType.Numeric: -1,
    PGDataType.Oid: 4,
    PGDataType.Path: -1,
    PGDataType.Point: 16,
    PGDataType.Polygon: -1,
    PGDataType.Serial2: 2,
    PGDataType.Serial4: 4,
    PGDataType.Serial8: 8,
    PGDataType.Text: -1,
    PGDataType.Time: 8,
    PGDataType.Timestamp: 8,
    PGDataType.Timestamptz: 8,
    PGDataType.Timetz: 12,
    PGDataType.Uuid: 16,
}
