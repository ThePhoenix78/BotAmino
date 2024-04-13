import typing

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

if not typing.TYPE_CHECKING:
    import requests
    import json
    try:
        with requests.get("https://pypi.org/pypi/amino.fix/json") as response:
            __newest__ = json.loads(response.text)["info"]["version"]
    except requests.RequestException:
        pass
    else:
        del response
    del requests, json

if __newest__ > __version__:
    print(f"New version of {__title__} available: {__newest__} (Using {__version__})")
    print("Visit our discord - https://discord.gg/Bf3dpBRJHj")
