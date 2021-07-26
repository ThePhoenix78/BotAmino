import re
import json
import base64
import requests
from secrets import token_hex

from bs4 import BeautifulSoup


def generate_device_info():
    # I'm still trying to figure out how to generate the device id. So far, decompilation is proving difficult,
    # so sniffed values are being used
    return {
        "device_id": "01A9F9668156F0D5E5CC8637F4F82E0B863F9C3705368F59FB03103EE9D099BCF6D1E19FFC9677612F",
        "device_id_sig": "Aa0ZDPOEgjt1EhyVYyZ5FgSZSqJt",
        "user_agent": "Dalvik/2.1.0 (Linux; U; Android 5.1.1; SM-G973N Build/beyond1qlteue-user 5; com.narvii.amino.master/3.4.33562)"
    }

def decode_base64(data: str):
    data = re.sub(rb'[^a-zA-Z0-9+/]', b'', data.encode())[:162]
    return base64.b64decode(data + b'=' * (-len(data) % 4)).decode("cp437")[1:]

def sid_to_uid(SID: str):
    try: return json.loads(decode_base64(SID))["2"]
    except json.decoder.JSONDecodeError: return sid_to_uid_2(SID)

def sid_to_ip_address(SID: str):
    try: return json.loads(decode_base64(SID))["4"]
    except json.decoder.JSONDecodeError: return sid_to_ip_address_2(SID)

def sid_to_uid_2(SID: str):
    data = f'input={SID}&charset=UTF-8'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.post('https://www.base64decode.org/', data, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    output = soup.find('textarea', {'id': 'output'})
    uid = output.text.split(':')[4].split(',')[0].replace('"', '').replace(' ', '')

    return uid

def sid_to_ip_address_2(SID: str):
    data = f'input={SID}&charset=UTF-8'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.post('https://www.base64decode.org/', data, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    output = soup.find('textarea', {'id': 'output'})
    ip_address = output.text.split(':')[6].split(',')[0].replace('"', '').replace(' ', '')

    return ip_address