import collections
import contextlib
import enum
import functools
import inspect
import re
import typing
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
STRING_TYPES = [typing.Any, object]
ARRAY_SEPARATOR = ','
MAPPING_SEPARATOR = ':'
UNION_TYPES = [typing.Union]
if PY10:
    import types
    UNION_TYPES.append(types.UnionType)

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


class GroupResult:
    def __init__(self, value: typing.Any, converted: bool, isfactory: bool, isdefault: bool, unsafe: bool):
        self.value = value
        self.converted = converted
        self.isfactory = isfactory
        self.isdefault = isdefault
        self.unsafe = unsafe


class Empty:
    """Marker object for empty parameter default values."""


def parse_args(message, feature='default'):
    return [Argument(m.group('key'), m.group('value'), m.start(), m.end()) for m in re.finditer(PATTERNS[feature], message)]


def from_array_group(text, dtype, default=Empty):
    origin = typing.get_origin(dtype) or tuple
    args = typing.get_args(dtype) or (typing.Any, ...)
    arguments = list(map(lambda s: s.strip(), text.split(ARRAY_SEPARATOR))) if text else []
    invalid_factory = True
    if len(args) == 2 and args[1] is Ellipsis:
        args = tuple([args[0]] * len(arguments))
        invalid_factory = False
    result = []
    argument_iterator = iter(arguments)
    converted, isfactory, isdefault, unsafe = False, False, False, False
    for expected in args:
        try:
            value = next(argument_iterator)
        except StopIteration:
            value = ''
        if expected not in STRING_TYPES:
            value = build_value(value, expected)
        result.append(value)
    try:
        value = origin(result)
        converted = True
    except Exception:
        value = default
        if default is Empty:
            unsafe = True
            if not invalid_factory:
                try:
                    value = origin()
                    unsafe = False
                except Exception:
                    pass
        else:
            isdefault = True
    return GroupResult(value, converted, isfactory, isdefault, unsafe)


def from_boolean_group(text, dtype, default=Empty):
    converted, isfactory, isdefault, unsafe = False, False, False, False
    for bool_value, pattern in {True: REGEX_TRUE, False: REGEX_FALSE}.items():
        if text and pattern.match(text):
            value, converted = dtype(bool_value), True
            break
    else:
        value = default
        if default is Empty:
            unsafe = True
            try:
                value, isfactory, unsafe = dtype(), True, False
            except Exception:
                pass
        else:
            isdefault = True
    return GroupResult(value, converted, isfactory, isdefault, unsafe)


def from_list_group(text, dtype, default=Empty):
    origin, args = typing.get_origin(dtype) or dtype, typing.get_args(dtype)
    expected = args[0] if args else typing.Any
    arguments = list(filter(None, map(str.strip, text.split(ARRAY_SEPARATOR)))) if text else []
    result = []
    converted, isfactory, isdefault, unsafe = False, False, False, False
    for value in arguments:
        if expected not in STRING_TYPES:
            value = build_value(value, expected)
            if value is Empty:
                continue
        result.append(value)
    try:
        value, converted = origin(result), True
    except Exception:
        value = default
        if default is Empty:
            unsafe = True
            try:
                value, isfactory, unsafe = origin(), True, False
            except Exception:
                pass
        else:
            isdefault = True
    return GroupResult(value, converted, isfactory, isdefault, unsafe)


def from_literal_group(text, dtype, default=Empty):
    converted, isfactory, isdefault, unsafe = False, False, False, False
    args = typing.get_args(dtype)
    dtypes = set(type(arg) for arg in args)
    for arg_dtype in dtypes:
        if not text:
            continue
        option = build_value(text, arg_dtype)
        if option in args:
            value, converted = option, True
            break
    else:
        value = default
        if default is Empty:
            unsafe = True
            try:
                value, isfactory, unsafe = args[0], True, False  # first literal argument
            except Exception:
                pass
        else:
            isdefault = True
    return GroupResult(value, converted, isfactory, isdefault, unsafe)


def from_mapping_group(text, dtype, default=Empty):
    converted, isfactory, isdefault, unsafe = False, False, False, False
    origin = typing.get_origin(dtype) or dtype
    if origin.__module__ in ["collections.abc", "typing"]:
        origin = dict
    args = typing.get_args(dtype) or (typing.Any, typing.Any)
    arguments = text.split(MAPPING_SEPARATOR) if text else []
    if len(arguments) % 2:
        arguments += ['']
    arguments = list(map(lambda s: s.strip(), arguments))
    result = []
    for k, v in zip(arguments[::2], arguments[1::2]):
        key = build_value(k, args[0])
        val = build_value(v, args[1])
        if key is Empty or val is Empty:
            continue
        result.append((key, val))
    try:
        value = origin(result)
        converted = True
    except Exception:
        value = default
        if default is Empty:
            unsafe = True
            try:
                value, isfactory, unsafe = origin(result), True, False
            except Exception:
                pass
        else:
            isdefault = True
    return GroupResult(value, converted, isfactory, isdefault, unsafe)


def from_numeric_group(text, dtype, default=Empty):
    converted, isfactory, isdefault, unsafe = False, False, False, False
    text = text.replace('i', 'j')  # math imaginary char
    try:
        if issubclass(dtype, (float, int)):
            value = dtype(complex(text).real)
        elif issubclass(dtype, complex):
            value = dtype(complex(text))
        else:
            raise ValueError
        converted = True
    except ValueError:
        value = default
        if default is Empty:
            unsafe = True
            try:
                value, isfactory, unsafe = dtype(), True, False
            except Exception:
                pass
        else:
            isdefault = True
    return GroupResult(value, converted, isfactory, isdefault, unsafe)


def from_none_group(text, dtype, default=Empty):
    converted, isfactory, isdefault, unsafe = False, False, False, False
    value, isdefault = default, True
    if default is Empty:
        value, unsafe = None, False
    return GroupResult(value, converted, isfactory, isdefault, unsafe)


def from_text_group(text, dtype, default=Empty):
    converted, isfactory, isdefault, unsafe = False, False, False, False
    try:
        if not text:
            raise ValueError
        elif issubclass(dtype, (bytearray, bytes)):
            value = dtype(text, encoding='utf-8', errors='ignore')
        elif issubclass(dtype, str):
            value = dtype(text)
        else:
            raise ValueError
        converted = True
    except ValueError:
        value = default
        if default is Empty:
            unsafe = True
            try:
                value, isfactory, unsafe = dtype(), True, False
            except Exception:
                pass
        else:
            isdefault = True
    return GroupResult(value, converted, isfactory, isdefault, unsafe)


def from_custom_group(text, dtype, default=Empty):
    converted, isfactory, isdefault, unsafe = False, False, False, False
    try:
        if not text:
            raise ValueError
        value, converted = dtype(text), True
    except Exception:
        value = default
        if default is Empty:
            unsafe = True
            try:
                value, isfactory, unsafe = dtype(), True, False
            except Exception:
                pass
        else:
            isdefault = True
    return GroupResult(value, converted, isfactory, isdefault, unsafe)


GroupInfo = collections.namedtuple("GroupInfo", ['dtypes', 'converter'])

class DataGroup(enum.Enum):
    ARRAY = GroupInfo((tuple,), from_array_group)
    BOOLEAN = GroupInfo((bool,), from_boolean_group)
    CUSTOM = GroupInfo((CustomType,), from_custom_group)
    LIST = GroupInfo((frozenset, list, set), from_list_group)
    LITERAL = GroupInfo((typing.Literal,), from_literal_group)
    MAPPING = GroupInfo((dict,), from_mapping_group)
    NUMERIC = GroupInfo((complex, float, int), from_numeric_group)
    NONE = GroupInfo((type(None),), from_none_group)
    TEXT = GroupInfo((bytearray, bytes, str, typing.Any), from_text_group)

    @classmethod
    def get_group(cls, dtype):
        for group in filter(lambda group: group.supported(dtype), cls):
            return group
        return None

    def supported(self, dtype):
        origin = typing.get_origin(dtype) or dtype
        try:
            return issubclass(origin, self.value.dtypes)
        except TypeError:
            return origin in self.value.dtypes


def build_value(text, annotation, param=Empty):
    if annotation in STRING_TYPES:
        annotation = str
    groups = []
    if typing.get_origin(annotation) in UNION_TYPES:
        groups.extend((DataGroup.get_group(dtype), dtype) for dtype in typing.get_args(annotation))
    else:
        groups.append((DataGroup.get_group(annotation), annotation))
    for group, dtype in groups:
        if group is None:
            raise ValueError("Unsupported dtype: %s" % dtype)
    if isinstance(param, inspect.Parameter):
        if param.default is param.empty:
            default = Empty
        else:
            default = param.default
    else:
        default = param
    if not groups:
        return default
    if not isinstance(text, str):
        text = ''
    results = [group.value.converter(text.strip(), dtype, default) for group, dtype in groups]
    if typing.TYPE_CHECKING:
        results = typing.cast(list[GroupResult], results)
    for result in filter(lambda result: result.converted, results):
        return result.value
    for result in filter(lambda result: result.isdefault, results):
        return result.value
    for result in filter(lambda result: result.isfactory, results):
        return result.value
    for result in filter(lambda result: result.unsafe, results):
        if result.value is Empty:
            continue
        return result.value
    raise TypeError("Ïnvalid argument or functionality for %s" % ", ".join(map(lambda g: g.name, groups)))


def supported_annotation(annotation):
    if annotation in STRING_TYPES:
        return True
    return any(group.supported(annotation) for group in DataGroup) and all(supported_annotation(a) for a in typing.get_args(annotation))


def can_has_default(obj):
    origin = typing.get_origin(obj)
    if origin in UNION_TYPES:
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


@functools.lru_cache()
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


@functools.lru_cache()
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
