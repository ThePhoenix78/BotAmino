import base64
import hmac
from hashlib import sha1
import requests

from . import device
sid = None

class Headers:
    def __init__(self, data = None, type = None, deviceId: str = None, sig: str = None):
        if deviceId:
            dev = device.DeviceGenerator(deviceId=deviceId)
        else:
            dev = device.DeviceGenerator()

        headers = {
            "NDCDEVICEID": dev.device_id,
            "Accept-Language": "en-US",
            "Content-Type": "application/json; charset=utf-8",
            "User-Agent": dev.user_agent,
            "Host": "service.narvii.com",
            "Accept-Encoding": "gzip",
            "Connection": "Keep-Alive"
        }

        if data: headers["Content-Length"] = str(len(data))
        if sid: headers["NDCAUTH"] = f"sid={sid}"
        if type: headers["Content-Type"] = type
        if sig: headers["NDC-MSG-SIG"] = sig
        if data is not None and sig is None and isinstance(data, bytes) is False: headers["NDC-MSG-SIG"] = base64.b64encode(b"\x32" + hmac.new(bytes.fromhex("fbf98eb3a07a9042ee5593b10ce9f3286a69d4e2"), data.encode(), sha1).digest()).decode()
        self.headers = headers
