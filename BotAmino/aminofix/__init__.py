__title__ = 'Amino.fix'
__author__ = 'Minori'
__license__ = 'MIT'
__copyright__ = 'Copyright 2021-2023 Minori'
__version__ = '2.3.5.3'

from .acm import ACM
from .client import Client
from .sub_client import SubClient
from .lib.util import exceptions, helpers, objects, headers
from .asyncfix import acm, client, sub_client, socket
from .socket import Callbacks, SocketHandler
from requests import get
from json import loads

__newest__ = loads(get("https://pypi.org/pypi/amino.fix/json").text)["info"]["version"]

if __version__ != __newest__:
    print(f"New version of {__title__} available: {__newest__} (Using {__version__})")
    print("Visit our discord - https://discord.gg/Bf3dpBRJHj")
