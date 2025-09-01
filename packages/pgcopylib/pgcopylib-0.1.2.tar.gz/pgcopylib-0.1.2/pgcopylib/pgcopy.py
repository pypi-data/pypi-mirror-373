from io import (
    BufferedReader,
    BufferedWriter,
)
from types import FunctionType
from typing import (
    Any,
    Generator,
    Optional,
)
from struct import (
    error as UnpackError,
    unpack,
)

from .constants import HEADER
from .dtypes import AssociateDtypes
from .enums import (
    PGOid,
    PGOidToDType,
)
from .errors import (
    PGCopySignatureError,
    PGCopyEOFError,
    PGCopyError,
)
from .reader import (
    read_record,
    skip_record,
)
from .writer import PGCopyWriter


class PGCopy:
    """PGCopy dump unpacker."""

    def __init__(
        self,
        file: BufferedReader,
        pgtypes: list[PGOid] = [],
    ) -> None:
        """Class initialization."""

        self.file = file
        self.pgtypes = pgtypes

        self.file.seek(0)

        self.header: bytes = self.file.read(11)

        if self.header != HEADER:
            msg = "PGCopy signature not match!"
            raise PGCopySignatureError(msg)

        self.flags_area: list[int] = [
            (byte >> i) & 1
            for byte in self.file.read(4)
            for i in range(7, -1, -1)
        ]
        self.is_oid_enable: bool = bool(self.flags_area[16])
        self.header_ext_length: int = unpack("!i", self.file.read(4))[0]
        self.num_columns: Optional[int] = None
        self.num_rows: Optional[int] = None

    @staticmethod
    def to_dtypes(reader: FunctionType):
        """Cast data types decorator."""

        def wrapper(*args, **kwargs):

            self: PGCopy = args[0]
            raw: tuple[bytes, int] = reader(*args, **kwargs)

            if self.pgtypes:
                to_dtype: FunctionType = AssociateDtypes[
                    PGOidToDType[self.pgtypes[raw[1]]]
                ].read
                return to_dtype(raw[0])

            return raw[0]

        return wrapper

    def _col_rows(self) -> None:
        """Read columns and rows."""

        if not self.num_columns and not self.num_rows:
            self.file.seek(19)
            self.num_rows = 0

            cols: int = unpack("!h", self.file.read(2))[0]
            all_cols: list[int] = []

            while cols != -1:
                all_cols.append(cols)
                self.num_rows += 1

                if self.is_oid_enable:
                    self.file.seek(self.file.tell() + 4)

                [skip_record(self.file) for _ in range(cols)]
                cols: int = unpack("!h", self.file.read(2))[0]

            self.num_columns = max(all_cols)

    @to_dtypes
    def _reader(
        self,
        column: int,
    ) -> tuple[Any, int]:
        """Read record from file."""

        return read_record(self.file), column

    def read_raw(self) -> list[Optional[Any], None, None]:
        """Read single row."""

        cols: int = unpack("!h", self.file.read(2))[0]

        if cols == -1:
            raise PGCopyEOFError("PGCopy end of file!")
        if not cols:
            raise PGCopyError("No columns!")
        if self.is_oid_enable:
            self.file.seek(self.file.tell() + 4)

        return [
            self._reader(column)
            for column in range(cols)
        ]

    def read_raws(self) -> Generator[
        list[Optional[Any]],
        None,
        None,
    ]:
        """Read all rows."""

        self.num_rows = 0

        while 1:
            try:
                raw = self.read_raw()
                self.num_columns = len(raw)
                self.num_rows += 1
                yield raw
            except PGCopyEOFError:
                break

    def read(self, size: int = -1) -> list[list[Any]]:
        """Read raws."""

        for _ in range(2):
            try:
                row_iter = iter(self.read_raws())
                rows: list[list[Any]] = [next(row_iter)]
                break
            except (StopIteration, UnpackError):
                self.file.seek(19)

        if size == -1:
            rows.extend(self.read_raws())
        else:
            for _ in range(size - 1):
                try:
                    rows.append(next(row_iter))
                except StopIteration:
                    break

        return rows

    def writer(self, file: BufferedWriter) -> PGCopyWriter:
        """Initialize PGCopyWriter from PGCopy."""

        return PGCopyWriter(file, self.pgtypes)

    def __repr__(self) -> str:
        """PGCopy info in interpreter."""

        return self.__str__()

    def __str__(self) -> str:
        """PGCopy info."""

        self._col_rows()

        return f"""PGCopy dump reader
Total columns: {self.num_columns}
Total raws: {self.num_rows}
Postgres types: {
    [pgtype.name for pgtype in self.pgtypes] or
    ["raw" for _ in range(self.num_columns)]
}
"""
