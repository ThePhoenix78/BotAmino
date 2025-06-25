"""A library to create Amino bots"""
# This a wrapper of Slimakoi's API with some of my patches
# API made by ThePhoenix78
# Modified by vedansh#4039
# Big optimisation thanks to SempreLEGIT#1378 ♥
# Updated by V¡ktor

__all__ = (
    "BannedWords",
    "Bot",
    "BotAmino",
    "Client",
    "Command",
    "HTTPClient",
    "Parameters",
    "SubClient",
    "TimeOut"
)

from typing import TYPE_CHECKING

from .acm import *
from .bannedwords import *
from .bot import *
from .botamino import *
from .client import *
from .command import *
from .http import *
from .parameters import *
from .subclient import *
from .timeout import *
from .ws import *

from . import (
    errors as errors,
    objects as objects,
    parser as parser,
    types as types,
    typing as typing,
    utils as utils
)

__title__ = 'BotAmino'
__author__ = 'ThePhoenix78'
__license__ = 'MIT'
__copyright__ = 'Copyright 2021-2022 ThePhoenix78'
__url__ = 'https://github.com/ThePhoenix78/BotAmino'
__newest__ = __version__ = '1.29.0'

if not TYPE_CHECKING:
    import urllib.error
    import urllib.request

    try:
        with urllib.request.urlopen("https://pypi.org/rss/project/botamino/releases.xml", timeout=25) as response:
            __newest__ = response.read().split(b"<title>", 2)[-1].split(b"<")[0].decode()
    except urllib.error.URLError:
        pass
    finally:
        del urllib

if __version__ < __newest__:
    print(f"New version of {__title__} available: {__newest__} (Using {__version__})")
else:
    print(f"version : {__version__}")
