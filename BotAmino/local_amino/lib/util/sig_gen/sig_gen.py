import base64
import hmac
from hashlib import sha1


def signature(data) -> str:
    mac = hmac.new(bytes.fromhex("307c3c8cd389e69dc298d951341f88419a8377f4"), data.encode("utf-8"), sha1)
    digest = bytes.fromhex("22") + mac.digest()
    return base64.b64encode(digest).decode("utf-8")
