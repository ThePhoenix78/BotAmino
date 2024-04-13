from typing import Any
from _typeshed import SupportsRead

__all__ = (
    "decode_sid",
    "gen_deviceId",
    "read_bytes",
    "sid_to_uid",
    "sid_to_ip_address",
    "signature",
    "update_deviceId"
)

PREFIX: str
SIG_KEY: str
DEVICE_KEY: str

def gen_deviceId(data: bytes | str | None = None) -> str: ...
def signature(data: bytes | str) -> str: ...
def update_deviceId(device: str) -> str: ...
def decode_sid(sid: str) -> dict[str, Any]: ...
def sid_to_uid(SID: str) -> str: ...
def sid_to_ip_address(SID: str) -> str: ...
def read_bytes(file: SupportsRead[bytes] | bytes | str) -> bytes: ...
