from hashlib import sha1
import requests
import base64
import hmac
import json


def local_signature(data) -> str:
    return


def signature(data) -> str:
    if isinstance(data, dict):
        data = json.dumps(data)
    return requests.get(f"http://forevercynical.com/generate/signature?data={str(data)}").json()['signature']
