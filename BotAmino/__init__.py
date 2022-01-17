from json import loads
from requests import get

__title__ = 'BotAmino'
__author__ = 'ThePhoenix78'
__license__ = 'MIT'
__copyright__ = 'Copyright 2021-2022 ThePhoenix78'
__version__ = '1.20.3.2'

# thanks to vedansh#4039 ♥

from .BotAmino import *

__newest__ = loads(get("https://pypi.python.org/pypi/BotAmino/json").text)["info"]["version"]

if __version__ != __newest__:
    print(f"New version of {__title__} available: {__newest__} (Using {__version__})")
else:
    print(f"version : {__version__}")
