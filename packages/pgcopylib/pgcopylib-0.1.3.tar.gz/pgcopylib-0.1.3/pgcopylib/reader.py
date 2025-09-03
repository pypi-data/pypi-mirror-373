from io import BufferedReader
from struct import unpack
from typing import Optional


def read_record(file: BufferedReader) -> Optional[bytes]:
    """Read one record to bytes."""

    length: int = unpack("!l", file.read(4))[0]

    if length == -1:
        return None
    if length == 0:
        return b""

    return file.read(length)


def skip_record(file: BufferedReader) -> None:
    """Skip one record."""

    length: int = unpack("!l", file.read(4))[0]

    if length > 0:
        file.seek(file.tell() + length)
