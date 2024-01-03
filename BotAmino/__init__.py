# This a wrapper of Slimakoi's API with some of my patches
# API made by ThePhoenix78
# Modified by vedansh#4039
# Big optimisation thanks to SempreLEGIT#1378 ♥
# Type hint support by ViktorSky
import typing

from .bannedwords import *
from .bot import *
from .botamino import *
from .command import *
from .parameters import *
from .timeout import *
from .utils import *
from . import (
    bannedwords,
    bot,
    botamino,
    command,
    parameters,
    timeout,
    utils
)

__all__ = (  # type: ignore
    bannedwords.__all__
    + bot.__all__
    + botamino.__all__
    + command.__all__
    + parameters.__all__
    + timeout.__all__
    + utils.__all__
)

__title__ = 'BotAmino'
__author__ = 'ThePhoenix78'
__license__ = 'MIT'
__copyright__ = 'Copyright 2021-2022 ThePhoenix78'
__newest__ = __version__ = '1.29.0'

if not typing.TYPE_CHECKING:
    from urllib.request import urlopen
    from json import loads
    try:
        __newest__ = loads(urlopen("https://pypi.python.org/pypi/BotAmino/json").read())["info"]["version"]
    finally:
        del loads, urlopen

if __version__ != __newest__:
    print(f"New version of {__title__} available: {__newest__} (Using {__version__})")
else:
    print(f"version : {__version__}")
