import abc
import contextlib
import inspect
import os
import re
import sys
import typing

__all__ = (
    'NO_ICON_URL',
    "PATH_AMINO",
    "PATH_CLIENT",
    "PATH_UTILITIES",
    'CustomType',
    'print_exception'
)

# constants
PY39 = sys.version_info > (3, 9)
NO_ICON_URL = "https://wa1.aminoapps.com/static/img/user-icon-placeholder.png"
PATH_UTILITIES = "utilities"
PATH_AMINO = os.path.join(PATH_UTILITIES, "amino_list")
PATH_CLIENT = "client.txt"
# regex
REGEX_TRUE = re.compile(r"(?i)yes|yep|y|1|true|si|s")
REGEX_FALSE = re.compile(r"(?i)no|nop|n|0|false|")

# classes
class CustomTypeMeta(abc.ABCMeta):
    def __subclasscheck__(cls, subclass):
        if super().__subclasscheck__(subclass):
            result, first_param = False, True
            for param in inspect.signature(subclass).parameters.values():
                if first_param:
                    if param.annotation in [param.empty, typing.Any, str]:
                        result = True
                    first_param = False
                    continue
                if param.default is param.empty:
                    result = False
            return result
        return False


class CustomType(metaclass=CustomTypeMeta):
    __slots__ = ()

    @abc.abstractmethod
    def __init__(self, value):
        pass


class print_exception(contextlib.suppress):
    def __exit__(self, exctype, excinst, exctb):
        if excinst:
            print(repr(excinst))
        return super().__exit__(exctype, excinst, exctb)


# functions
def safe_exit(code=0):
    """exit the program"""
    os._exit(code)
