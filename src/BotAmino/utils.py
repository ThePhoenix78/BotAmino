import abc
import contextlib
import inspect
import io
import os
import re
import sys
import tempfile
import typing

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

# constants
PY10 = sys.version_info >= (3, 10)
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


def split_audio(file, format=None, chunk_secs=180):
    """Split an audio file in n seconds using pydub library"""
    import pydub
    chunk_length_ms = chunk_secs * 1000
    if not isinstance(file, str):
        if hasattr(file, "read"):
            if hasattr(file, "name") and file.name.count(".") and not format:
                *_, format = file.name.split(".")
            file = file.read()
        with tempfile.NamedTemporaryFile("w+b", suffix=format, delete=False) as tmp:
            tmp.write(file)
        audio = pydub.AudioSegment.from_file(tmp.name, format=format)
        os.remove(tmp.name)
    else:
        audio = pydub.AudioSegment.from_file(file, format=format)
    if not format:
        format = "mp3"
    audio_length_ms = len(audio)
    prev_time = 0
    for curr_time in range(chunk_length_ms, audio_length_ms, chunk_length_ms):
        chunk = audio[prev_time:curr_time]
        tmpfile = tempfile.mkdtemp(suffix=format)
        try:
            yield io.BytesIO(chunk.export(tmpfile, format=format).read())
        finally:
            os.remove(tmpfile)
        prev_time = curr_time
    if prev_time < audio_length_ms:
        chunk = audio[prev_time:audio_length_ms]
        tmpfile = tempfile.mkdtemp(suffix=format)
        try:
            yield io.BytesIO(chunk.export(tmpfile, format=format).read())
        finally:
            os.remove(tmpfile)
