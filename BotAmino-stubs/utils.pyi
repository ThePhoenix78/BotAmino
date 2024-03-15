from abc import (
    ABCMeta,
    abstractmethod
)
from contextlib import suppress
from re import Pattern
from types import TracebackType
from typing import NoReturn, Optional, Type

__all__ = (
    'NO_ICON_URL',
    "PATH_AMINO",
    "PATH_CLIENT",
    "PATH_UTILITIES",
    'CustomType',
    'print_exception',
    'safe_exit'
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
    def __exit__(
        self,
        exctype: Optional[Type[BaseException]],
        excinst: Optional[BaseException],
        exctb: Optional[TracebackType]
    ) -> bool: ...

def safe_exit(code: int = 0) -> NoReturn: ...
