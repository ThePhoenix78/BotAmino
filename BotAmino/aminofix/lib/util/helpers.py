import json
import os

from functools import reduce
from base64 import b64decode, b64encode
from typing import Union
from hashlib import sha1
from hmac import new

PREFIX = bytes.fromhex("19")
SIG_KEY = bytes.fromhex("DFA5ED192DDA6E88A12FE12130DC6206B1251E44")
DEVICE_KEY = bytes.fromhex("E7309ECC0953C6FA60005B2765F99DBBC965C8E9")

def gen_deviceId(data: bytes = None) -> str:
    if isinstance(data, str): data = bytes(data, 'utf-8')
    identifier = PREFIX + (data or os.urandom(20))
    mac = new(DEVICE_KEY, identifier, sha1)
    return f"{identifier.hex()}{mac.hexdigest()}".upper()

def signature(data: Union[str, bytes]) -> str:
    data = data if isinstance(data, bytes) else data.encode("utf-8")
    return b64encode(PREFIX + new(SIG_KEY, data, sha1).digest()).decode("utf-8")

def update_deviceId(device: str) -> str:
    return gen_deviceId(bytes.fromhex(device[2:42]))

def decode_sid(sid: str) -> dict:
    return json.loads(b64decode(reduce(lambda a, e: a.replace(*e), ("-+", "_/"), sid + "=" * (-len(sid) % 4)).encode())[1:-20].decode())

def sid_to_uid(SID: str) -> str: return decode_sid(SID)["2"]

def sid_to_ip_address(SID: str) -> str: return decode_sid(SID)["4"]