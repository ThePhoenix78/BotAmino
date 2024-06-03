import requests
import json

from .acm import *
from .client import *
from .sub_client import *
from .lib.util import (
    exceptions as exceptions,
    helpers as helpers,
    objects as objects,
    headers as headers
)
from .socket import *

__title__ = 'Amino.fix'
__author__ = 'Minori'
__license__ = 'MIT'
__copyright__ = 'Copyright 2021-2023 Minori'
__version__ = '2.3.6.2'
__newest__ = __version__


try:
    __newest__ = json.loads(requests.get("https://pypi.org/pypi/amino.fix/json", timeout=2).text)["info"]["version"]
except requests.RequestException:
    pass
finally:
    del requests, json

if __newest__ > __version__:
    print(f"New version of {__title__} available: {__newest__} (Using {__version__})")
    print("Visit our discord - https://discord.gg/Bf3dpBRJHj")
