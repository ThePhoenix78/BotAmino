import base64
import hmac
from hashlib import sha1

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

        s_headers = {"NDCDEVICEID": dev.device_id}

        web_headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
            "x-requested-with": "xmlhttprequest"
        }

        if data: headers["Content-Length"] = str(len(data))
        if sid: headers["NDCAUTH"] = f"sid={sid}"
        if type: headers["Content-Type"] = type
        if sig: headers["NDC-MSG-SIG"] = sig
        if data is not None and sig is None and isinstance(data, bytes) is False:
            headers["NDC-MSG-SIG"] = base64.b64encode(b"\x22" + hmac.new(bytes.fromhex("307c3c8cd389e69dc298d951341f88419a8377f4"), data.encode(), sha1).digest()).decode()
        self.headers = headers
        self.s_headers = s_headers
        self.web_headers = web_headers
