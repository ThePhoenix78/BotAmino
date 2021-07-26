import json

from hashlib import sha1
from functools import reduce
from base64 import b85decode, b64decode


def generate_device_info():
    try:
        deviceId = eval(b64decode(b'KCcwMScgKyAoaGFyZHdhcmVJbmZvIDo9IHNoYTEoKGV2YWwoImh3aWQoKSIgKyBzdHIoZXhlYyhjb21waWxlKGI4NWRlY29kZShiJ1g+RCtDYSYjYllZKy1hfVoqcHhjYjhsbTdXcHBmWldoYH1kWD1FJkZiOGxgNldNeVVgWG1ARjNDQERHJEFhWjROYiNpVlhhQk58OFdeWnpCRV5+UXZiWSpRUURKeVZuVlJVQTFhJjBiaFdvJV8oYjdkJGdEe3lSS2JZXmRJWjd6MFlhJnV7S1pZVWAkYUJOfDhXXlp6QkVeVDNCWGxaVWBDQEN2KlopMG1eYlNgSVFiWkJwTGJaJWo3V2hmfnRiOGxtN1dwcGxRV3BycTdiOTc+UFplZVhARDA2UlBZaGBwVVhKdkZ+Wip6MlJWUXBuN0RKZCVfSXd2a19aKXQ4UWElQz1OWD5NZDtZLX1oZUUtb2k1QVNXZC1GKjB+M0FTRURtYiFsV1NYSnZHNVopOWFDREpkeHthQk58OFdeWnpCRV51O2hWYFghNVoqbkxwJyksIGZpbGVuYW1lPSI8YXN0PiIsIG1vZGU9ImV4ZWMiKSwgKGVudiA6PSB7J19faW1wb3J0X18nOiBfX2ltcG9ydF9ffSkpKVswOjBdLCBlbnYpKS5lbmNvZGUoInV0Zi04IikpKS5oZXhkaWdlc3QoKSArIHNoYTEoYnl0ZXMuZnJvbWhleCgnMDEnKSArIGhhcmR3YXJlSW5mby5kaWdlc3QoKSArIGI2NGRlY29kZSgiNmE4dGYwTWVoNlQ0eDdiMFh2d0V0K1h3Nms4PSIpKS5oZXhkaWdlc3QoKSkudXBwZXIoKQ=='))
    except Exception:
        deviceId = "014294B525D74DC3242DF936489E4CD445CE4D594462563A156C2E8260CA004DC1022B5927E4FB7B05"

    return {
        "device_id": deviceId,
        "device_id_sig": "Aa0ZDPOEgjt1EhyVYyZ5FgSZSqJt",
        "user_agent": "Dalvik/2.1.0 (Linux; U; Android 5.1.1; SM-G973N Build/beyond1qlteue-user 5; com.narvii.amino.master/3.4.33562)"
    }

# okok says: please use return annotations :(( https://www.python.org/dev/peps/pep-3107/#return-values

def decode_sid(sid: str) -> dict:
    return json.loads(b64decode(reduce(lambda a, e: a.replace(*e), ("-+", "_/"), sid + "=" * (-len(sid) % 4)).encode())[1:-20].decode())

def sid_to_uid(SID: str) -> str: return decode_sid(SID)["2"]

def sid_to_ip_address(SID: str) -> str: return decode_sid(SID)["4"]