__title__ = 'Amino.py'
__author__ = 'Slimakoi'
__license__ = 'MIT'
__copyright__ = 'Copyright 2020-2021 Slimakoi'
__version__ = '1.2.17'

from .acm import ACM
from .client import Client
from .sub_client import SubClient
from .socket import Callbacks, SocketHandler
from .lib.util import device, exceptions, headers, helpers, objects
from requests import get
from json import loads

__newest__ = loads(get("https://pypi.python.org/pypi/Amino.py/json").text)["info"]["version"]

if __version__ != __newest__:
    print(exceptions.LibraryUpdateAvailable(f"New version of {__title__} available: {__newest__} (Using {__version__})"))
