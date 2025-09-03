# ----------------------------------------------------------------------
# Copyright (c) 2022
#
# See the LICENSE file for details
# see the AUTHORS file for authors
# ----------------------------------------------------------------------

from math import pi
from enum import StrEnum
from datetime import datetime, timezone

EARTH_RADIUS = 6371009.0  # in meters
GEO_COORD_EPSILON = (2 / EARTH_RADIUS) * (180 / pi) # in degrees

INFINITE_T = datetime(year=2999, month=12, day=31, hour=23, minute=59, second=59, tzinfo=timezone.utc)

class ObserverType(StrEnum):
    PERSON = "Individual"
    ORG = "Organization"

class PhotometerModel(StrEnum):
    TESSW = "TESS-W"
    TESSWDL = "TESS-WDL" # Variant with datalogger
    TESS4C = "TESS4C"

class ValidState(StrEnum):
    CURRENT = "Current"
    EXPIRED = "Expired"

# As returned by Nominatim search
class PopulationCentre(StrEnum):
    VILLAGE = "village"
    MUNICIP = "municipality"
    TOWN = "town"
    CITY = "city"
  
class TimestampSource(StrEnum):
    SUBSCRIBER = "Subscriber"
    PUBLISHER = "Publisher"

class ReadingSource(StrEnum):
    DIRECT = "Direct"
    IMPORTED = "Imported"

class RegisterState(StrEnum):
    MANUAL = "Manual"
    AUTO = "Automatic"
    UNKNOWN = "Unknown"

class RegisterOp(StrEnum):
    CREATE = "CR"
    RENAME = "RN"
    REPLACE = "RP"
    EXTINCT = "XX"
