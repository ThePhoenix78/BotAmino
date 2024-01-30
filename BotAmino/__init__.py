"""A library to create Amino bots"""
# This a wrapper of Slimakoi's API with some of my patches
# API made by ThePhoenix78
# Modified by vedansh#4039
# Big optimisation thanks to SempreLEGIT#1378 ♥
from .bannedwords import *
from .bot import *
from .botamino import *
from .command import *
from .parameters import *
from .timeout import *
from .utils import *

# type-hint helper
from . import typing as typing

___all__ = (
    "PATH_AMINO",
    "PATH_CLIENT",
    "PATH_UTILITIES",
    "BannedWords",
    "Bot",
    "BotAmino",
    "Command",
    "CustomType",
    "Parameters",
    "TimeOut"
)

__title__ = 'BotAmino'
__author__ = 'ThePhoenix78'
__license__ = 'MIT'
__copyright__ = 'Copyright 2021-2022 ThePhoenix78'
__url__ = 'https://github.com/ThePhoenix78/BotAmino'
__newest__ = __version__ = '1.29.0'

from urllib.request import urlopen
from urllib.error import HTTPError, URLError
from json import loads
try:
    __newest__ = loads(urlopen("https://pypi.python.org/pypi/BotAmino/json").read())["info"]["version"]
except (HTTPError, URLError):
    pass
finally:
    del HTTPError, URLError, loads, urlopen

if __version__ < __newest__:
    print(f"New version of {__title__} available: {__newest__} (Using {__version__})")
else:
    print(f"version : {__version__}")
