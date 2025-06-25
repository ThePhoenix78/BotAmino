from __future__ import annotations

import abc
import base64
import collections.abc
import contextlib
import datetime
import functools
import hashlib
import hmac
import inspect
import io
import os
import pathlib
import re
import sys
import tempfile
import time
import types
import typing
import typing_extensions
import uuid
import ujson
import requests

if typing.TYPE_CHECKING:
    import pydub
    
    from _typeshed import SupportsRead
else:
    with contextlib.suppress(ImportError):
        import pydub


__all__ = (
    "NO_ICON_URL",
    "PATH_AMINO",
    "PATH_UTILITIES",
    "CustomType",
    "print_exception",
    "safe_exit",
    "split_audio"
)

P = typing_extensions.ParamSpec("P")
G = typing.TypeVar("G")
S = typing.TypeVar("S")
T = typing.TypeVar("T")

# constants
PY10 = sys.version_info > (3, 10)
PREFIX01 = "01"
PREFIX19 = "19"
PREFIX32 = "32"
PREFIX42 = "42"
PREFIX52 = "52"
DEV01KEY = "54D50523CCF670A4509650E84D11CAEC"
DEV19KEY = "e7309ecc0953c6fa60005b2765f99dbbc965c8e9"
DEV32KEY = "76b4a156aaccade137b8b1e77b435a81971fbd3e"
DEV42KEY = "02b258c63559d8804321c5d5065af320358d366f"
DEV52KEY = "ae49550458d8e7c51d566916b04888bf"
SIG19KEY = "dfa5ed192dda6e88a12fe12130dc6206b1251e44"
SIG32KEY = "fbf98eb3a07a9042ee5593b10ce9f3286a69d4e2"
SIG42KEY = "f8e7a61ac3f725941e3ac7cae2d688be97f30b93"
SIG52KEY = "eab4f1b9e3340cd1631ede3b587cc3eb"


# current
DEVICE_PREFIX = PREFIX52
DEVICE_KEY = DEV19KEY
SIGNATURE_PREFIX = PREFIX52
SIGNATURE_KEY = SIG52KEY
AGORA_APP_ID_AUDIO = "2b0567d3ff534f0593528432dac20dc1"
AGORA_APP_ID_AUDIO_DEV = "92c6a12930984cde9b49a8dd78131bad"
AGORA_APP_ID_SCREEN_ROOM = "bf8df8ece609424487de640dcb95bf7f"
AGORA_APP_ID_SCREEN_ROOM_DEV = "9862e22af39f4d2a8cd230dc8c789604"
AGORA_APP_ID_VIDEO = "8d30e965b43f4cb1ba6144f411f3c3cb"
AGORA_APP_ID_VIDEO_DEV = "3f79ff67eac8404bbf5b6e00d3148ae1"
NO_ICON_URL = "https://wa1.aminoapps.com/static/img/user-icon-placeholder.png"
FMT_AMINO_TIME = r"%Y-%m-%dT%H:%M:%SZ"
FMT_CLOCK = r"%H:%M:%S"
FMT_DATE = r"%Y-%m-%d"
PATH_UTILITIES = "utilities"
PATH_AMINO = os.path.join(PATH_UTILITIES, "amino_list")
# regex
RE_TRUE = re.compile(r"(?i)yes|yep|y|1|true|si|s")
RE_FALSE = re.compile(r"(?i)no|nop|n|0|false|")
RE_AMINO_ID_LINK = re.compile(r"http[s]?://aminoapps.com/u/\S+")
RE_AMINO_LINK = re.compile(r"https?://aminoapps.com/p/\S+")
RE_COMMUNITY_LINK = re.compile(r"http[s]?://aminoapps.com/c/\s+")
RE_HEX_COLOR = re.compile(r"#(?:[0-9a-fA-F]{3}){1,2}$", re.I)
RE_INVITATION_LINK = re.compile(r"http[s]?://aminoapps.com/invite/\s+")
RE_MENTION_NICKNAME = re.compile(r"\W+?@(\S+)\W+?(?=\s|$)")
RE_MENTION = re.compile(r"\W+?@\S+\W+?(?=\s|$)")
RE_NUMBER_IN_MSG = re.compile(r"\s*(\d+)\s*")
RE_NUMBER = re.compile(r"\d+")
RE_UUID = re.compile(
    r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})", re.I
)
RE_YT_LINK = re.compile(
    "(http[s]?://(?:youtu.be|(?:(?:www.|m.)?youtube.com))/(?:(?:embed|watch)(?:[?v=/]+))?[A-Za-z0-9_-]{11})",
    re.I,
)
RE_YT_VIDEO_ID = re.compile("[A-Za-z0-9_-]{11}")

DEFAULT_MENTION_PATTERN = "@[\\u4e00-\\u9fa5\\w\\-]+"
METION_TAG = "@"
MENTION_END = "\u202c\u202d"
MENTION_START = "\u200e\u200f"

DEFAULT_CHAT_BG = [
    "http://static.narvii.com/default-chat-room-background/1_00.png"
    "http://static.narvii.com/default-chat-room-background/2_00.png",
    "http://static.narvii.com/default-chat-room-background/3_00.png",
    "http://static.narvii.com/default-chat-room-background/4_00.png",
    "http://static.narvii.com/default-chat-room-background/5_00.png",
    "http://static.narvii.com/default-chat-room-background/6_00.png",
    "http://static.narvii.com/default-chat-room-background/7_00.png",
    "http://static.narvii.com/default-chat-room-background/8_00.png",
    "http://static.narvii.com/default-chat-room-background/9_00.png",
    "http://static.narvii.com/default-chat-room-background/10_00.png",
]


# classes
class CustomTypeMeta(abc.ABCMeta):
    def __subclasscheck__(cls, subclass: type) -> bool:
        from .parser import supported_annotation  # circular import

        if super().__subclasscheck__(subclass):
            result, first_param = False, True
            for param in inspect.signature(subclass).parameters.values():
                if first_param:
                    annotation = (
                        typing.Any
                        if param.annotation is param.empty
                        else param.annotation
                    )
                    if supported_annotation(annotation):
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
    def __init__(self, value: typing.Any) -> None: ...


class print_exception(contextlib.suppress):
    def __exit__(
        self,
        exctype: type[BaseException] | None,
        excinst: BaseException | None,
        exctb: types.TracebackType | None,
    ) -> bool:
        if excinst:
            print(repr(excinst))
        return super().__exit__(exctype, excinst, exctb)


class GenericProperty(typing.Generic[G, S], property):
    def __init__(
        self,
        fget: collections.abc.Callable[[typing.Any], G] | None = None,
        fset: collections.abc.Callable[[typing.Any, S], None] | None = None,
        fdel: collections.abc.Callable[[typing.Any], None] | None = None,
    ) -> None:
        self.fget = fget
        self.fset = fset
        self.fdel = fdel
        self.__doc__ = fget.__doc__
        self.owner: type | None = None
        self.name: str | None = None

    def __set_name__(self, owner: type, name: str) -> None:
        self.owner = owner
        self.name = name

    @typing.overload
    def __get__(
        self, instance: None, owner: type | None = None
    ) -> typing_extensions.Self: ...
    @typing.overload
    def __get__(self, instance: object, owner: type | None = None) -> G: ...
    def __get__(
        self, instance: object | None, owner: type | None = None
    ) -> G | typing_extensions.Self:
        if instance is None:
            return self
        if self.fget is None:
            ownername = owner.__qualname__ if owner else None
            ownermsg = (
                f"{self.name!r} of {ownername!r}"
                if self.name
                else f"of {ownername}" if owner else ""
            )
            raise TypeError(f"property {ownermsg!r} object has no getter")
        return self.fget(instance)

    def __set__(self, instance: typing.Any, value: S) -> None:
        if self.fset is None:
            owner = None if instance is None else type(instance).__qualname__
            ownermsg = (
                f"{self.name!r} of {owner!r}"
                if self.name
                else f"of {owner}" if owner else ""
            )
            raise TypeError(f"property {ownermsg!r} object has no setter")
        self.fset(instance, value)

    def __delete__(self, instance: typing.Any) -> None:
        if self.fdel is None:
            owner = None if instance is None else type(instance).__qualname__
            ownermsg = (
                f"{self.name!r} of {owner!r}"
                if self.name
                else f"of {owner}" if owner else ""
            )
            raise TypeError(f"property {ownermsg!r} object has no deleter")
        self.fdel(instance)


def safe_exit(code: int = 0) -> typing.NoReturn:
    """exit the program"""
    os._exit(code)  # type: ignore


def to_secs(days: int = 0, hours: int = 0, mins: int = 0, secs: int = 0) -> int:
    return ((days * 24 + hours) * 60 + mins) * 60 + secs


def clock(secs: float | None = None) -> str:
    return time.strftime(
        FMT_CLOCK,
        time.localtime() if secs is None else time.gmtime(secs % (60 * 60 * 24)),
    )


def clock_to_time(clock: str) -> int:
    t = time.strptime(clock, FMT_CLOCK)
    return to_secs(hours=t.tm_hour, mins=t.tm_min, secs=t.tm_sec)


def date(secs: float | None = None) -> str:
    return time.strftime(
        FMT_DATE, time.localtime() if secs is None else time.gmtime(abs(secs))
    )


def date_to_time(date: str) -> int:
    return int(time.mktime(datetime.datetime.strptime(date, FMT_DATE).timetuple()))


def timestamp(secs: float | None = None) -> str:
    return time.strftime(
        FMT_AMINO_TIME, time.localtime() if secs is None else time.gmtime(abs(secs))
    )


def timestamp_to_time(timestamp: str) -> int:
    return int(
        time.mktime(datetime.datetime.strptime(timestamp, FMT_AMINO_TIME).timetuple())
    )


def build_uuid() -> str:
    return str(uuid.uuid4())


def currentTimeMillis() -> int:
    return int(time.time() * 1000)


def build_device(
    did: bytes | None = None, version: str = DEVICE_PREFIX, key: str = DEVICE_KEY
) -> str:
    info = bytes.fromhex(version) + (did or os.urandom(20))
    device = info + hmac.new(bytes.fromhex(key), info, hashlib.sha1).digest()
    return device.hex().upper()


def update_device(
    device: str, prefix: str = DEVICE_PREFIX, key: str = DEVICE_KEY
) -> str:
    return build_device(bytes.fromhex(device[2:42]), prefix, key)


def check_device(device: str, key: str = DEVICE_KEY) -> bool:
    provided_mac = device[-40:]
    identifier = bytes.fromhex(device[:-40])
    expected_mac = hmac.new(bytes.fromhex(key), identifier, hashlib.sha1).hexdigest()
    return provided_mac.lower() == expected_mac.lower()


def build_signature(
    data: bytes | str, prefix: str = SIGNATURE_PREFIX, key: str = SIGNATURE_KEY
) -> str:
    content = data.encode("utf-8") if isinstance(data, str) else data
    return base64.b64encode(
        bytes.fromhex(prefix)
        + hmac.new(
            bytes.fromhex(key),
            content,
            hashlib.sha1,
        ).digest()
    ).decode("utf-8")


def read_file(fp: str | pathlib.Path | typing.BinaryIO) -> bytes:
    if isinstance(fp, pathlib.Path):
        fp = str(fp.resolve())
    if isinstance(fp, str):
        fp = open(fp, "rb")
    with fp:
        return fp.read()


def build_target(path: str, comId: int = 0) -> str:
    return urljoin("ndc://", f"x{comId}" if comId else "g", path)


def build_ndtopic(topic: str, objectId: str | None = None, comId: int = 0) -> str:
    return urljoin(
        "ndtopic", f"x{comId}" if comId else "g", topic, objectId or "", sep=":"
    )


class SID(typing.NamedTuple):
    json: dict[str, typing.Any]
    key: str
    prefix: str
    version: int
    null: typing.Any | None
    objectId: str
    objectType: int
    ip_address: str
    timestamp: int
    clientType: int

    @property
    def expired(self) -> bool:
        return (time.time() - self.timestamp) > 60 * 60 * 24


def decode_sid(sid: str) -> SID:
    decoded = base64.urlsafe_b64decode(sid + "=" * (4 - len(sid) % 4))
    json = ujson.loads(decoded[1:-20].decode("utf-8"))
    return SID(
        json=json,
        key=decoded[-20:].hex(),
        prefix=decoded[:2].hex(),
        version=json["0"],
        null=json["1"],
        objectId=json["2"],
        objectType=json["3"],
        ip_address=json["4"],
        timestamp=json["5"],
        clientType=json["6"],
    )


def getYoutubeImage(videoId: str):
    with requests.get("http://i.ytimg.com/vi/" + videoId + "/default.jpg") as response:
        return response.content


def getHQYoutubeImage(videoId: str):
    with requests.get(
        "http://i.ytimg.com/vi/" + videoId + "/hqdefault.jpg"
    ) as response:
        return response.content


def urljoin(*uri: str, sep: str = "/") -> str:
    return sep.join(
        filter(None, map(lambda u: u.removeprefix("/").removesuffix("/"), uri))
    )


def objectTypeName(objectType: int) -> str:
    return {
        0: "user-profile",
        1: "blog",
        2: "item",
        3: "comment",
        4: "blog-category",
        7: "chat-message",
        12: "chat-thread",
        13: "item-category",
        15: "item-submission",
        16: "community",
        17: "community-collection",
        20: "bookmark",
        106: "shared-folder",
        109: "shared-file",
        114: "sticker-collection",
        116: "chat-bubble",
        122: "avatar-frame",
        128: "topic",
        131: "announcement",
    }[objectType]


def apiTypeName(objectType: int) -> str:
    return {
        0: "user-profile",
        1: "blog",
        2: "item",
        3: "comment",
        4: "blog/category",
        7: "chat/message",
        12: "chat/thread",
        13: "item/category",
        15: "item/submission",
        16: "community",
        17: "community/collection",
        20: "bookmark",
        106: "shared-folder/folders",
        109: "shared-folder/files",
        114: "sticker-collection",
        116: "chat/chat-bubble",
        122: "avatar-frame",
        128: "topic",
        131: "announcement",
    }[objectType]


@typing.overload
def copy_signature(
    __wrapped: collections.abc.Callable[P, T], __ismethod: typing.Literal[False] = False
) -> collections.abc.Callable[
    [collections.abc.Callable[..., T]], collections.abc.Callable[P, T]
]: ...
@typing.overload
def copy_signature(
    __wrapped: collections.abc.Callable[
        typing_extensions.Concatenate[typing.Any, P], T
    ],
    __ismethod: typing.Literal[True],
) -> collections.abc.Callable[
    [collections.abc.Callable[typing_extensions.Concatenate[S, ...], typing.Any]],
    collections.abc.Callable[typing_extensions.Concatenate[S, P], T],
]: ...
def copy_signature(
    wrapped: collections.abc.Callable[..., T], _: bool = False
) -> collections.abc.Callable[..., collections.abc.Callable[..., T]]:
    def decorator(
        callback: collections.abc.Callable[..., typing.Any],
    ) -> collections.abc.Callable[..., typing.Any]:
        @functools.wraps(wrapped)
        def wrapper(*args: typing.Any, **kwargs: typing.Any) -> typing.Any:
            return callback(*args, **kwargs)

        wrapper.__signature__ = inspect.signature(wrapped)  # type: ignore
        return wrapper

    return decorator


def split_audio(
    file: str | SupportsRead[bytes] | bytes,
    format: str | None = None,
    chunk_secs: int = 180,
) -> collections.abc.Iterator[io.BytesIO]:
    """Split an audio file in n seconds using pydub library"""
    if 'pydub' not in sys.modules:
        raise ImportError("pydub is required for split_audio but is not installed")

    chunk_length_ms = chunk_secs * 1000
    if not isinstance(file, str):
        if not isinstance(file, bytes):
            if hasattr(file, "name"):
                name = typing.cast(str, getattr(file, "name"))
                if name.count(".") and not format:
                    *_, format = name.split(".")
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