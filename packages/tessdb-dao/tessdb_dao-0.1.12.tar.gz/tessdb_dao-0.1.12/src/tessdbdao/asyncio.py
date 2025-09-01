# ----------------------------------------------------------------------
# Copyright (c) 2024 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------


# --------------------
# System wide imports
# -------------------

from typing import Type

# ---------------------
# Third party libraries
# ---------------------

from lica.sqlalchemy.asyncio.model import Model

# -------------------
# Own package imports
# -------------------

from .model import (
    make_Time,
    make_Date,
    make_Observer,
    make_Location,
    make_Units,
    make_Tess,
    make_TessView,
    make_NameMapping,
    make_TessReadings,
    make_Tess4cReadings,
)

# Tables creation with asyncio Model behaviour built-in

Date: Type = make_Date(Model)
Time: Type = make_Time(Model)
Observer: Type = make_Observer(Model)
Location: Type = make_Location(Model)
Units: Type = make_Units(Model)
Tess: Type = make_Tess(Model)
NameMapping: Type = make_NameMapping(Model)
TessView: Type = make_TessView(Model, Tess, NameMapping, Location, Observer)
TessReadings: Type = make_TessReadings(Model)
Tess4cReadings: Type = make_Tess4cReadings(Model)


__all__ = [
    "Date",
    "Time",
    "Observer",
    "Location",
    "Units",
    "Tess",
    "NameMapping",
    "TessView",
    "TessReadings",
    "Tess4cReadings",
]
