"""
Mappers transform plain dict to another dict
converting key and values.

Classes definition are inspired on pydantic
"""

import sys
import traceback

from dateutil.parser import parse
from dateutil.tz import gettz

from syncmodels.mapper import *
from ..models import inventory

# ---------------------------------------------------------
# Loggers
# ---------------------------------------------------------

from agptools.logs import logger

log = logger(__name__)


# =========================================================
# SwarmtubeInventory Mappers
# =========================================================


# ---------------------------------------------------------
# Base Mappers Classes
# ---------------------------------------------------------
class SwarmtubeInventory(Mapper):
    PYDANTIC = inventory.SwarmtubeInventory

    current_sign_in_at = I, I
    current_sign_in_ip = I, I
    last_activity_on = I, DATE
    last_sign_in_at = I, DATE
    last_sign_in_ip = I, I
    sign_in_count = I, INT, 0
