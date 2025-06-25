from abc import (
    ABCMeta,
    abstractmethod
)
from collections.abc import Generator
from contextlib import suppress
from io import BytesIO
from re import Pattern
from typing import Any, NoReturn

from _typeshed import SupportsRead

__all__ = (
    'NO_ICON_URL',
    "PATH_AMINO",
    "PATH_CLIENT",
    "PATH_UTILITIES",
    'CustomType',
    'print_exception',
    'safe_exit',
    'split_audio'
)

PY10: bool
NO_ICON_URL: str
PATH_UTILITIES: str
PATH_AMINO: str
PATH_CLIENT: str
REGEX_TRUE: Pattern[str]
REGEX_FALSE: Pattern[str]

class CustomTypeMeta(ABCMeta):
    def __subclasscheck__(cls, subclass: type) -> bool: ...

class CustomType(metaclass=CustomTypeMeta):
    @abstractmethod
    def __init__(self, value: str) -> None: ...

class print_exception(suppress):
    pass

def safe_exit(code: int = 0) -> NoReturn: ...
def split_audio(file: SupportsRead[bytes] | bytes | str, format: str | None = None, chunk_secs: int = 180) -> Generator[BytesIO, Any, None]: ...