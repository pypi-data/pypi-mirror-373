# pgcopylib

Library for reading data from binary format PosgreSQL

## Features

- No dependencies on external libraries
- Without specifying data types, all columns will be read in bytes
- Support for most data types

## Supported Data Types

| PostgreSQL data type  | Python data type                                             |
|:----------------------|:-------------------------------------------------------------|
| _bit                  | list[str]                                                    |
| _bool                 | list[bool]                                                   |
| _box                  | list[tuple[tuple[float, float], tuple[float, float]]]        |
| _bpchar               | list[str]                                                    |
| _bytea                | list[bytes]                                                  |
| _char                 | list[str]                                                    |
| _cidr                 | list[ipaddress.IPv4Network / ipaddress.IPv6Network]          |
| _circle               | list[tuple[float, float, float]]                             |
| _date                 | list[datetime.date]                                          |
| _float4               | list[float]                                                  |
| _float8               | list[float]                                                  |
| _inet                 | list[ipaddress.IPv4Address / ipaddress.IPv6Address]          |
| _int2                 | list[int]                                                    |
| _int4                 | list[int]                                                    |
| _int8                 | list[int]                                                    |
| _interval             | list[dateutil.relativedelta.relativedelta]                   |
| _json                 | list[dict / list / str / int / float / bool / None]          |
| _jsonb                | list[dict / list / str / int / float / bool / None]          |
| _line                 | list[tuple[float, float, float]]                             |
| _lseg                 | list[list[tuple[float, float]]]                              |
| _macaddr              | list[str]                                                    |
| _macaddr8             | list[str]                                                    |
| _money                | list[float]                                                  |
| _numeric              | list[decimal.Decimal]                                        |
| _oid                  | list[int]                                                    |
| _path                 | list[list[tuple[float, float]] / tuple[tuple[float, float]]] |
| _point                | list[tuple[float, float]]                                    |
| _polygon              | list[tuple[tuple[float, float]]]                             |
| _serial2              | list[int]                                                    |
| _serial4              | list[int]                                                    |
| _serial8              | list[int]                                                    |
| _text                 | list[str]                                                    |
| _time                 | list[datetime.time]                                          |
| _timestamp            | list[datetime.datetime]                                      |
| _timestamptz          | list[datetime.datetime]                                      |
| _timetz               | list[datetime.time]                                          |
| _uuid                 | list[uuid.UUID]                                              |
| _varbit               | list[str]                                                    |
| _varchar              | list[str]                                                    |
| _xml                  | list[str]                                                    |
| bit                   | str                                                          |
| bool                  | bool                                                         |
| box                   | tuple[tuple[float, float], tuple[float, float]]              |
| bpchar                | str                                                          |
| bytea                 | bytes                                                        |
| char                  | str                                                          |
| cidr                  | ipaddress.IPv4Network / ipaddress.IPv6Network                |
| circle                | tuple[float, float, float]                                   |
| date                  | datetime.date                                                |
| float4                | float                                                        |
| float8                | float                                                        |
| inet                  | ipaddress.IPv4Address / ipaddress.IPv6Address                |
| int2                  | int                                                          |
| int4                  | int                                                          |
| int8                  | int                                                          |
| interval              | dateutil.relativedelta.relativedelta                         |
| json                  | dict / list / str / int / float / bool / None                |
| jsonb                 | dict / list / str / int / float / bool / None                |
| line                  | tuple[float, float, float]                                   |
| lseg                  | list[tuple[float, float]]                                    |
| macaddr               | str                                                          |
| macaddr8              | str                                                          |
| money                 | float                                                        |
| numeric               | decimal.Decimal                                              |
| oid                   | int                                                          |
| path                  | list[tuple[float, float]] / tuple[tuple[float, float]]       |
| point                 | tuple[float, float]                                          |
| polygon               | tuple[tuple[float, float]]                                   |
| serial2               | int                                                          |
| serial4               | int                                                          |
| serial8               | int                                                          |
| text                  | str                                                          |
| time                  | datetime.time                                                |
| timestamp             | datetime.datetime                                            |
| timestamptz           | datetime.datetime                                            |
| timetz                | datetime.time                                                |
| uuid                  | uuid.UUID                                                    |
| varbit                | str                                                          |
| varchar               | str                                                          |
| xml                   | str                                                          |

## Installation

### From pip

```bash
pip install pgcopylib
```

### From local directory

```bash
pip install .
```

### From git

```bash
pip install git+https://github.com/0xMihalich/pgcopylib
```
