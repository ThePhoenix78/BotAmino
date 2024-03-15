import collections
import contextlib
import enum
import inspect
import re
import typing
import typing_extensions
# internal
from .parameters import Parameters
from .utils import (
    PY10,
    REGEX_FALSE,
    REGEX_TRUE,
    CustomType
)

__all__ = (
    'build_value',
    'can_has_default',
    'supported_annotation',
)

# message argument regex
DEFAULT_REGEX = r"(?:(?P<key>[^=\s]+)=)?(?P<valuequote>['\"])?(?P<value>(?(2)(?:\\\2|[^\2])*?|[^\s]+))(?(2)\2)"
QUOTEDKEY_REGEX = r"(?:(?P<keyquote>['\"])?(?P<key>(?(1)(?:\\\1|[^\1])*?|[^=\s]+))(?(1)\1)=)?(?P<valuequote>['\"])?(?P<value>(?(3)(?:\\\3|[^\3])*?|[^\s]+))(?(3)\3)"
# intern checker util
ALLOW_TYPES = [typing.Any, object]
ARRAY_SEPARATOR = ','
MAPPING_SEPARATOR = ':'
BOOL_REGEX = {
    True: REGEX_TRUE,
    False: REGEX_FALSE
}
TYPE_WRAPPER = [typing.Union]
if PY10:
    import types
    TYPE_WRAPPER.extend([typing.Annotated, types.UnionType])
else:
    TYPE_WRAPPER.append(typing_extensions.Annotated)

PATTERNS = {
    'default': DEFAULT_REGEX,
    'quotedkey': QUOTEDKEY_REGEX
}

class Argument:
    __slots__ = (
        'key',
        'value',
        'start',
        'end'
    )

    def __init__(self, key, value, start, end):
        self.key = key
        self.value = value
        self.start = start
        self.end = end


class Empty:
    """Marker object for empty parameter default values."""


def parse_args(message, feature='default'):
    return [Argument(m.group('key'), m.group('value'), m.start(), m.end()) for m in re.finditer(PATTERNS[feature], message)]


def from_array_group(text, dtype, default=Empty):
    assert DataGroup.ARRAY.supported(dtype), 'Invalid dtype. Expected %s, got %r' % (DataGroup.ARRAY, dtype)
    origin, args = typing.get_origin(dtype) or tuple, typing.get_args(dtype) or (typing.Any, ...)
    arguments = list(map(lambda s: s.strip(), text.split(ARRAY_SEPARATOR)))
    if len(args) == 2 and args[1] is Ellipsis:
        args = tuple([args[0]] * len(arguments))
    result = []
    argument_iterator = iter(arguments)
    for expected in args:
        try:
            value = next(argument_iterator)
        except StopIteration:
            value = ''
        if expected not in ALLOW_TYPES:
            value = build_value(value, expected)
        result.append(value)
    try:
        return origin(result)
    except Exception:
        if default is Empty:
            raise
        return default

def from_boolean_group(text, dtype, default=Empty):
    assert DataGroup.BOOLEAN.supported(dtype), 'Invalid dtype. Expected %s, got %r' % (DataGroup.BOOLEAN, dtype)
    for bool_value, pattern in BOOL_REGEX.items():
        if pattern.match(text):
            return dtype(bool_value)
    try:
        return dtype()
    except Exception:
        if default is Empty:
            raise
        return default


def from_list_group(text, dtype, default=Empty):
    assert DataGroup.LIST.supported(dtype), 'Invalid dtype. Expected %s, got %r' % (DataGroup.LIST, dtype)
    origin, args = typing.get_origin(dtype) or dtype, typing.get_args(dtype)
    expected = args[0] if args else typing.Any
    partial = from_array_group(text, tuple, default)
    result = [build_value(value, expected) for value in partial]
    try:
        return origin(result)
    except Exception:
        if default is Empty:
            raise
        return default


def from_literal_group(text, dtype, default=Empty):
    assert DataGroup.LITERAL.supported(dtype), 'Invalid dtype. Expected %s, got %r' % (DataGroup.LITERAL, dtype)
    args = typing.get_args(dtype)
    dtypes = set(type(arg) for arg in args)
    for arg_dtype in dtypes:
        value = build_value(text, arg_dtype)
        if value in args:
            return value
    else:
        if default is Empty:
            return args[0]  # first literal argument
        return default


def from_mapping_group(text, dtype, default=Empty):
    assert DataGroup.MAPPING.supported(dtype), 'Invalid dtype. Expected %s, got %r' % (DataGroup.MAPPING, dtype)
    origin, args = typing.get_origin(dtype) or dtype, typing.get_args(dtype) or (typing.Any, typing.Any)
    result = {}
    arguments = text.split(MAPPING_SEPARATOR, 1)
    if len(arguments) != 2:
        arguments += ['']
    k, v  = map(lambda s: s.strip(), arguments)
    key = build_value(k, args[0])
    value = build_value(v, args[1])
    result[key] = value
    try:
        return origin(result)
    except Exception:
        if default is Empty:
            raise
        return default


def from_numeric_group(text, dtype, default=Empty):
    assert DataGroup.NUMERIC.supported(dtype), 'Invalid dtype. Expected %s, got %r' % (DataGroup.NUMERIC, dtype)
    text = text.replace('i', 'j') # math imaginary char
    try:
        if issubclass(dtype, (float, int)):
            return dtype(complex(text).real)
        elif issubclass(dtype, complex):
            return dtype(complex(text))
        else:
            raise ValueError
    except ValueError:
        if default is Empty:
            return dtype()
        return default


def from_text_group(text, dtype, default=Empty):
    assert DataGroup.TEXT.supported(dtype), 'Invalid dtype. Expected %s, got %r' % (DataGroup.TEXT, dtype)
    if issubclass(dtype, (bytearray, bytes)):
        return dtype(text, encoding='utf-8', errors='ignore')
    elif issubclass(dtype, str):
        return dtype(text)
    else:
        if default is Empty:
            return dtype()
        return default


def from_custom_group(text, dtype, default=Empty):
    assert DataGroup.CUSTOM.supported(dtype), 'Invalid dtype. Expected %s, got %r' % (DataGroup.CUSTOM, dtype)
    try:
        return dtype(text)
    except Exception:
        if default is Empty:
            raise
        return default


GroupInfo = collections.namedtuple("GroupInfo", ['dtypes', 'converter'])

class DataGroup(enum.Enum):
    ARRAY = GroupInfo((tuple,), from_array_group)
    BOOLEAN = GroupInfo((bool,), from_boolean_group)
    CUSTOM = GroupInfo((CustomType,), from_custom_group)
    LIST = GroupInfo((frozenset, list, set), from_list_group)
    LITERAL = GroupInfo((typing.Literal,), from_literal_group)
    MAPPING = GroupInfo((dict,), from_mapping_group)
    NUMERIC = GroupInfo((complex, float, int), from_numeric_group)
    NONE = GroupInfo((type(None),), from_numeric_group)
    TEXT = GroupInfo((bytearray, bytes, str, typing.Any), from_text_group)

    @classmethod
    def get_group(cls, dtype):
        for group in cls:
            if group.supported(dtype):
                return group
        else:
            return None

    def supported(self, dtype):
        origin = typing.get_origin(dtype) or dtype
        try:
            return issubclass(origin, self.value.dtypes)
        except TypeError:
            return origin in self.value.dtypes


def build_value(text, annotation, param=None):
    if annotation in ALLOW_TYPES:
        annotation = str
    group = DataGroup.get_group(annotation)
    inspect._empty
    default = Empty if param is None or param.default is param.empty else param.default
    if group is None:
        return default
    if not isinstance(text, str):
        text = ''
    return group.value.converter(text.strip(), annotation, default)


def supported_annotation(annotation):
    if annotation in ALLOW_TYPES:
        return True
    return any(group.supported(annotation) for group in DataGroup) and all(supported_annotation(a) for a in typing.get_args(annotation))


def can_has_default(obj):
    origin = typing.get_origin(obj)
    if origin in TYPE_WRAPPER:
        return all(can_has_default(o) for o in typing.get_args(obj))
    elif obj in [typing.Any]:
        return True
    try:
        annotations = extract_annotations(obj)
        for name, param in inspect.signature(obj).parameters.items():
            if param.kind in (param.VAR_POSITIONAL, param.VAR_KEYWORD):
                continue
            if not can_has_default(annotations.get(name, typing.Any)) and param.default is param.empty:
                return False
        else:
            return True
    except ValueError:
        return supported_annotation(obj)


def extract_annotations(callback):
    with contextlib.suppress(AttributeError):
        for name, dtype in callback.__annotations__.copy().items():
            if not isinstance(dtype, str) or dtype != Parameters.__name__:
                continue
            callback.__annotations__[name] = Parameters
    with contextlib.suppress(TypeError):
        return dict(typing.get_type_hints(callback))
    return {}


def validate_lite_callback(callback):
    sign = inspect.signature(callback)
    if not sign.parameters:
        raise ValueError("Invalid callback. An argument for BotAmino.Parameters is required") from None
    annotations = extract_annotations(callback)
    first_param = True
    for param in sign.parameters.values():
        annotation = annotations.get(param.name, typing.Any)
        if first_param:
            if annotation not in (typing.Any, Parameters):
                classname = getattr(annotation, '__name__', type(annotation).__name__)
                raise ValueError("Invalid {!r} annotation. {!r} is not compatible with BotAmino.Parameters".format(param.name, classname)) from None
            first_param = False
            continue
        raise ValueError("Invalid parameters. Lite callback should have only 1 parameter")


def validate_callback(callback):
    sign = inspect.signature(callback)
    if not sign.parameters:
        raise ValueError("Invalid callback. An argument for BotAmino.Parameters is required") from None
    annotations = extract_annotations(callback)
    first_param = True
    for name, param in sign.parameters.items():
        annotation = annotations.get(name, typing.Any)
        if first_param:
            if annotation not in (typing.Any, Parameters):
                classname = getattr(annotation, '__name__', type(annotation).__name__)
                raise ValueError("Invalid {!r} annotation. {!r} is not compatible with BotAmino.Parameters".format(name, classname))
            first_param = False
            continue
        if supported_annotation(annotation):
            continue
        if param.default is param.empty and not can_has_default(annotation):
            classname = getattr(annotation, '__name__', type(annotation).__name__)
            raise ValueError("Invalid {!r} annotation. {!r} requires default value".format(name, classname))


def bind_callback(callback, data, arguments):
    annotations = extract_annotations(callback)
    args = [data]
    kwargs = {}
    parameters = list(inspect.signature(callback).parameters.values())[1:]
    positional_params = filter(lambda param: param.kind in [param.POSITIONAL_ONLY, param.VAR_POSITIONAL], parameters)
    pos_or_kw_params = list(filter(lambda param: param.kind == param.POSITIONAL_OR_KEYWORD, parameters))
    keyword_params = list(filter(lambda param: param.kind in [param.KEYWORD_ONLY, param.VAR_KEYWORD], parameters))
    positional_arguments = filter(lambda argument: argument.key is None, arguments)
    keyword_arguments = {}
    for argument in filter(lambda argument: argument.key is not None, arguments):
        keyword_arguments[argument.key] = argument.value
    # parsing positional only arguments
    for param in positional_params:
        annotation = annotations.get(param.name, typing.Any)
        if param.kind == param.VAR_POSITIONAL:
            args.extend(build_value(argument.value, annotation, param) for argument in positional_arguments)
            break
        try:
            argument = next(positional_arguments)
        except StopIteration:
            value = build_value(None, annotation, param)
        else:
            value = build_value(argument.value, annotation, param)
        args.append(value)
    # parsing positional or keyword arguments
    for param in pos_or_kw_params:
        annotation = annotations.get(param.name, typing.Any)
        try:
            argument = next(positional_arguments)
            arg_default = argument.value
        except StopIteration:
            arg_default = None
        kwargs[param.name] = build_value(keyword_arguments.pop(param.name, arg_default), annotation, param)
    # parsing keyword only arguments
    for param in keyword_params:
        annotation = annotations.get(param.name, typing.Any)
        if param.kind == param.VAR_KEYWORD:
            kwargs.update({key: build_value(value, annotation, param) for key, value in keyword_arguments.items()})
            break
        kwargs[param.name] = build_value(keyword_arguments.pop(param.name, None), annotation, param)
    return tuple(args), dict(kwargs)
