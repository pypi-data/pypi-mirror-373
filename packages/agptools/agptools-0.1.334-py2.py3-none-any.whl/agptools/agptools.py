"""Main module."""

# libraty modules
import asyncio
import os

# library partial
from time import sleep


# local imports
from .helpers import parse_uri

# 3rd party libraries


# ---------------------------------------------------------
# Loggers
# ---------------------------------------------------------

from pycelium.tools.logs import logger

log = logger(__name__)

# subloger = logger(f'{__name__}.subloger')


# =========================================================
# agptools
# =========================================================
