from typing import NamedTuple
from types import FunctionType


class DTypeFunctions(NamedTuple):
    """Class for associate read and write functions."""

    read: FunctionType
    write: FunctionType
