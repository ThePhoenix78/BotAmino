import base64
import functools
import hashlib
import hmac
import json
import os

import requests

__all__ = (
    "decode_sid",
    "gen_deviceId",
    "read_bytes",
    "sid_to_uid",
    "sid_to_ip_address",
    "signature",
    "update_deviceId"
)

PREFIX = "19"
SIG_KEY = "DFA5ED192DDA6E88A12FE12130DC6206B1251E44"
DEVICE_KEY = "E7309ECC0953C6FA60005B2765F99DBBC965C8E9"

def gen_deviceId(data=None):
    if isinstance(data, str):
        data = bytes(data, 'utf-8')
    identifier = bytes.fromhex(PREFIX) + (data or os.urandom(20))
    mac = hmac.new(bytes.fromhex(DEVICE_KEY), identifier, hashlib.sha1)
    return f"{identifier.hex()}{mac.hexdigest()}".upper()

def signature(data):
    if not isinstance(data, bytes):
        data = data.encode()
    return base64.b64encode(bytes.fromhex(PREFIX) + hmac.digest(bytes.fromhex(SIG_KEY), data, hashlib.sha1)).decode()

def update_deviceId(device):
    return gen_deviceId(bytes.fromhex(device[2:42]))

def decode_sid(sid):
    sid = sid + "=" * (-len(sid) % 4)
    return json.loads(base64.b64decode(functools.reduce(lambda a, e: a.replace(*e), (("-", "+"), ("_", "/")), sid).encode())[1:-20].decode())

def sid_to_uid(SID):
    return decode_sid(SID)["2"]

def sid_to_ip_address(SID):
    return decode_sid(SID)["4"]

def read_bytes(file):
    if isinstance(file, str):
        if file.startswith("http") and "://" in file:
            with requests.get(file) as response:
                response.raise_for_status()
                data = response.content
        elif os.path.exists(file) and os.path.isfile(file):
            with open(file, "rb") as f:
                f.seek
                data = f.read()
        else:
            data = None
    elif isinstance(file, bytes):
        data = file
    elif callable(getattr(file, "read", None)):
        data = file.read()
    else:
        data = None
    if not isinstance(data, bytes):
        arg = file if isinstance(file, str) else file.__qualname__ if isinstance(file, type) else type(file).__qualname__
        raise ValueError(f"Invalid media. Expected bytes, url, filename or readable file, not {arg!r}")
    return data
