from dataclasses import dataclass
from enum import Enum
from functools import lru_cache
from inspect import Parameter
from re import Pattern
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Mapping,
    NamedTuple,
    Optional,
    Sequence,
    Tuple,
    Type,
    TypeGuard,
    Union
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
ALLOW_TYPES: List[type]
ARRAY_SEPARATOR: str
MAPPING_SEPARATOR: str
BOOL_REGEX: Dict[bool, Pattern[str]]
TYPE_WRAPPER: List[type]
PATTERNS: Dict[ParserFeature, str]

@dataclass
class Argument:
    key: Optional[str]
    value: str
    start: int
    end: int

class Empty: ...

def parse_args(message: str, feature: ParserFeature = 'default') -> List[Argument]: ...
def from_array_group(text: str, dtype: Type[Sequence[Any]], default: Union[Any, Type[Empty]]) -> Any: ...
def from_boolean_group(text: str, dtype: type, default: Union[Any, Type[Empty]]) -> Any: ...
def from_list_group(text: str, dtype: Type[Iterable[Any]], default: Union[Any, Type[Empty]]) -> Any: ...
def from_literal_group(text: str, dtype: type, default: Union[Any, Type[Empty]]) -> Any: ...
def from_mapping_group(text: str, dtype: Type[Mapping[Any, Any]], default: Union[Any, Type[Empty]]) -> Any: ...
def from_numeric_group(text: str, dtype: type, default: Union[Any, Type[Empty]]) -> Any: ...
def from_text_group(text: str, dtype: type, default: Union[Any, Type[Empty]]) -> Any: ...
def from_custom_group(text: str, dtype: type, default: Union[Any, Type[Empty]]) -> Any: ...

class GroupInfo(NamedTuple):
    dtypes: Tuple[type, ...]
    converter: Callable[[str, type, Union[Any, Type[Empty]]], Any]

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
    def get_group(cls, dtype: Any) -> Optional[DataGroup]: ...
    def supported(self, dtype: Any) -> bool: ...

def build_value(text: Optional[str], annotation: Any, param: Optional[Parameter] = None) -> Any: ...
def supported_annotation(annotation: type) -> bool: ...
def can_has_default(obj: Any) -> TypeGuard[Callable[[], Any]]: ...
def extract_annotations(callback: Callable[..., Any]) -> Dict[str, Any]: ...
def validate_lite_callback(callback: Callable[[Parameters], Any]) -> None: ...
def validate_callback(callback: Callable[..., Any]) -> None: ...
def bind_callback(callback: Callable[..., Any], data: Parameters, arguments: List[Argument]) -> Tuple[Tuple[Any, ...], Dict[str, Any]]: ...
