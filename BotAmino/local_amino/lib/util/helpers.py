import json

from hashlib import sha1
from functools import reduce
from base64 import b85decode, b64decode


def generate_device_info():
    try:
        deviceId = "2271017D5F917B37DAC9C325B10542BC9B63109292D882729D1813D5355404380E2F1A699A34629C10"
    except Exception:
        deviceId = "2271017D5F917B37DAC9C325B10542BC9B63109292D882729D1813D5355404380E2F1A699A34629C10"

    return {
        "device_id": "2271017D5F917B37DAC9C325B10542BC9B63109292D882729D1813D5355404380E2F1A699A34629C10",
        "device_id_sig": "Aa0ZDPOEgjt1EhyVYyZ5FgSZSqJt",
        "user_agent": "Dalvik/2.1.0 (Linux; U; Android 5.1.1; SM-G973N Build/beyond1qlteue-user 5; com.narvii.amino.master/3.4.33562)"
    }

# okok says: please use return annotations :(( https://www.python.org/dev/peps/pep-3107/#return-values

def decode_sid(sid: str) -> dict:
    return json.loads(b64decode(reduce(lambda a, e: a.replace(*e), ("-+", "_/"), sid + "=" * (-len(sid) % 4)).encode())[1:-20].decode())

def sid_to_uid(SID: str) -> str: return decode_sid(SID)["2"]

def sid_to_ip_address(SID: str) -> str: return decode_sid(SID)["4"]
