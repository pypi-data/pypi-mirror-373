"""PGCopy bynary dump parser."""

from .dtypes import AssociateDtypes
from .enums import (
    PGDataType,
    PGDataTypeLength,
    PGOid,
    PGOidToDType,
)
from .errors import (
    PGCopyEOFError,
    PGCopyError,
    PGCopyOidNotSupportError,
    PGCopyRecordError,
    PGCopySignatureError,
)
from .pgcopy import PGCopy
from .writer import PGCopyWriter


__all__ = (
    "AssociateDtypes",
    "PGCopy",
    "PGCopyEOFError",
    "PGCopyError",
    "PGCopyOidNotSupportError",
    "PGCopyRecordError",
    "PGCopySignatureError",
    "PGCopyWriter",
    "PGDataType",
    "PGDataTypeLength",
    "PGOid",
    "PGOidToDType",
)
__author__ = "0xMihalich"
__version__ = "0.1.3"
