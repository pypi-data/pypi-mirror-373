from io import BufferedWriter
from struct import pack
from typing import (
    Any,
    TYPE_CHECKING,
)

from .constants import HEADER
from .dtypes import AssociateDtypes
from .enums import (
    PGOid,
    PGOidToDType,
)
from .errors import PGCopyRecordError

if TYPE_CHECKING:
    from types import FunctionType


class PGCopyWriter:
    """PGCopy dump packer."""

    def __init__(
        self,
        file: BufferedWriter,
        pgtypes: list[PGOid],
    ) -> None:
        """Class initialization."""

        self.file: BufferedWriter = file
        self.pgtypes: list[PGOid] = pgtypes
        self.from_dtypes: list[FunctionType] = [
            AssociateDtypes[PGOidToDType[pgtype]].write
            for pgtype in pgtypes
        ]
        self.num_columns: int = len(pgtypes)
        self.num_rows: int = 0

        self.file.write(HEADER)
        self.file.write(bytes(8))

    def write_record(self, dtype_value: Any, column: int) -> None:
        """Write single record to file."""

        self.file.write(self.from_dtypes[column](
            dtype_value,
            self.pgtypes[column],
        ))

    def write_raw(self, dtype_values: list[Any]) -> None:
        """Write single raw into file."""

        if len(dtype_values) != self.num_columns:
            raise PGCopyRecordError()

        self.file.write(pack("!h", len(dtype_values)))
        [
            self.write_record(dtype_value, column)
            for column, dtype_value in enumerate(dtype_values)
        ]
        self.num_rows += 1

    def write(self, dtype_data: list[list[Any]]) -> None:
        """Write all rows into file."""

        [
            self.write_raw(dtype_values)
            for dtype_values in dtype_data
        ]

    def close(self) -> None:
        """Finalize file."""

        self.file.write(b"\xff\xff")
        self.file.flush()

    def __repr__(self) -> str:
        """PGCopy info in interpreter."""

        return self.__str__()

    def __str__(self) -> str:
        """PGCopy info."""

        return f"""PGCopy dump writer
Total columns: {self.num_columns}
Total raws: {self.num_rows}
Postgres types: {[pgtype.name for pgtype in self.pgtypes]}
"""
