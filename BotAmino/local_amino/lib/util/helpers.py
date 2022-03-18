import json

from functools import reduce
from base64 import b64decode


# okok says: please use return annotations :(( https://www.python.org/dev/peps/pep-3107/#return-values
def decode_sid(sid: str) -> dict: return json.loads(
    b64decode(reduce(lambda a, e: a.replace(*e), ("-+", "_/"), sid + "=" * (-len(sid) % 4)).encode())[1:-20].decode())


def sid_to_uid(SID: str) -> str: return decode_sid(SID)["2"]


def sid_to_ip_address(SID: str) -> str: return decode_sid(SID)["4"]
