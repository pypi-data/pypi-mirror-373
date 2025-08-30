# ----------------------------------------------------------------------
# Copyright (c) 2022
#
# See the LICENSE file for details
# see the AUTHORS file for authors
# ----------------------------------------------------------------------

from enum import StrEnum


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
