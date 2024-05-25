from dataclasses import dataclass
from enum import Enum
from inspect import Parameter
from re import Pattern
from typing import (
    Any,
    Callable,
    Iterable,
    Mapping,
    NamedTuple,
    Sequence,
    TypeGuard
)

from .parameters import Parameters
from .typing import ParserFeature

__all__ = (
    'build_value',
    'can_has_default',
    'supported_annotation',
)

DEFAULT_REGEX: str
QUOTEDKEY_REGEX: str
STRING_TYPES: list[type]
ARRAY_SEPARATOR: str
MAPPING_SEPARATOR: str
BOOL_REGEX: dict[bool, Pattern[str]]
UNION_TYPES: list[type]
PATTERNS: dict[ParserFeature, str]

@dataclass
class Argument:
    key: str | None
    value: str
    start: int
    end: int

@dataclass
class GroupResult:
    value: Any
    converted: bool
    isfactory: bool
    isdefault: bool
    unsafe: bool

class Empty: ...

def parse_args(message: str, feature: ParserFeature = 'default') -> list[Argument]: ...
def from_array_group(text: str, dtype: type[Sequence[Any]], default: Any | type[Empty]) -> GroupResult: ...
def from_boolean_group(text: str, dtype: type, default: Any | type[Empty]) -> GroupResult: ...
def from_list_group(text: str, dtype: type[Iterable[Any]], default: Any | type[Empty]) -> GroupResult: ...
def from_literal_group(text: str, dtype: type, default: Any | type[Empty]) -> GroupResult: ...
def from_mapping_group(text: str, dtype: type[Mapping[Any, Any]], default: Any | type[Empty]) -> GroupResult: ...
def from_numeric_group(text: str, dtype: type, default: Any | type[Empty]) -> GroupResult: ...
def from_none_group(text: str, dtype: type, default: Any | type[Empty]) -> GroupResult: ...
def from_text_group(text: str, dtype: type, default: Any | type[Empty]) -> GroupResult: ...
def from_custom_group(text: str, dtype: type, default: Any | type[Empty]) -> GroupResult: ...

class GroupInfo(NamedTuple):
    dtypes: tuple[type, ...]
    converter: Callable[[str, type, Any | type[Empty]], GroupResult]

class DataGroup(Enum):
    ARRAY: GroupInfo
    BOOLEAN: GroupInfo
    CUSTOM: GroupInfo
    LIST: GroupInfo
    LITERAL: GroupInfo
    MAPPING: GroupInfo
    NUMERIC: GroupInfo
    NONE: GroupInfo
    TEXT: GroupInfo
    @classmethod
    def get_group(cls, dtype: Any) -> DataGroup | None: ...
    def supported(self, dtype: Any) -> bool: ...

def build_value(text: str | None, annotation: Any, param: Parameter | Any = ...) -> Any: ...
def supported_annotation(annotation: type) -> bool: ...
def can_has_default(obj: Any) -> TypeGuard[Callable[[], Any]]: ...
def extract_annotations(callback: Callable[..., Any]) -> dict[str, Any]: ...
def validate_lite_callback(callback: Callable[[Parameters], Any]) -> None: ...
def validate_callback(callback: Callable[..., Any]) -> None: ...
def bind_callback(callback: Callable[..., Any], data: Parameters, arguments: list[Argument]) -> tuple[tuple[Any, ...], dict[str, Any]]: ...
