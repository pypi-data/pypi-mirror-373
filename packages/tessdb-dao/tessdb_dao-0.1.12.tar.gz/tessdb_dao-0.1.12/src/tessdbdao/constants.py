# ----------------------------------------------------------------------
# Copyright (c) 2022
#
# See the LICENSE file for details
# see the AUTHORS file for authors
# ----------------------------------------------------------------------

from math import pi
from enum import StrEnum

EARTH_RADIUS = 6371009.0  # in meters
GEO_COORD_EPSILON = (2 / EARTH_RADIUS) * (180 / pi) # in degrees


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
