# ----------------------------------------------------------------------
# Copyright (c) 2024 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------


# --------------------
# System wide imports
# -------------------

from __future__ import annotations

from typing import Optional, Type
from datetime import datetime

# =====================
# Third party libraries
# =====================

from sqlalchemy import (
    Enum,
    Boolean,
    Float,
    String,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    PrimaryKeyConstraint,
    select,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from lica.sqlalchemy.metadata import metadata
from lica.sqlalchemy.view import view

from .constants import (
    ObserverType,
    ValidState,
    PhotometerModel,
    PopulationCentre,
    TimestampSource,
    ReadingSource,
    RegisterState,
)

# ================
# Module constants
# ================

# =======================
# Module global variables
# =======================


# =================================
# Data Model, declarative ORM style
# =================================

# ---------------------------------------------
# Additional conveniente types for enumerations
# ---------------------------------------------

# These are really Column declarations
# They are needed on the RHS of the ORM model, in mapped_column()

ObserverCol: Enum = Enum(
    ObserverType,
    name="observer_type",
    create_constraint=False,
    metadata=metadata,
    validate_strings=True,
    values_callable=lambda x: [e.value for e in x],
)

PhotometerModelCol: Enum = Enum(
    PhotometerModel,
    name="model_type",
    create_constraint=False,
    metadata=metadata,
    validate_strings=True,
    values_callable=lambda x: [e.value for e in x],
)


ValidStateCol: Enum = Enum(
    ValidState,
    name="valid_state_type",
    create_constraint=False,
    metadata=metadata,
    validate_strings=True,
    values_callable=lambda x: [e.value for e in x],
)


PopulationCentreCol: Enum = Enum(
    PopulationCentre,
    name="population_type",
    create_constraint=False,
    metadata=metadata,
    validate_strings=True,
    values_callable=lambda x: [e.value for e in x],
)

TimestampSourceCol: Enum = Enum(
    TimestampSource,
    name="timestamp_source_type",
    create_constraint=False,
    metadata=metadata,
    validate_strings=True,
    values_callable=lambda x: [e.value for e in x],
)

ReadingSourceCol: Enum = Enum(
    ReadingSource,
    name="reading_source_type",
    create_constraint=False,
    metadata=metadata,
    validate_strings=True,
    values_callable=lambda x: [e.value for e in x],
)


RegisterStateCol: Enum = Enum(
    RegisterState,
    name="register_state_type",
    create_constraint=False,
    metadata=metadata,
    validate_strings=True,
    values_callable=lambda x: [e.value for e in x],
)

# --------
# Entities
# --------


def make_Date(declarative_base: Type) -> Type:
    class Date(declarative_base):
        __tablename__ = "date_t"

        # Date as YYYYMMDD integer
        date_id: Mapped[int] = mapped_column(primary_key=True)
        # Date as YYYY-MM-DD string
        sql_date: Mapped[str] = mapped_column(String(10))
        # Date as DD/MM/YYYY
        date: Mapped[str] = mapped_column(String(10))
        # Day of monty 1..31
        day: Mapped[int]
        # day of year 1..365
        day_year: Mapped[int]
        # Julian date at midnight
        julian_day: Mapped[float]
        # Sunday, Monday, Tuesday, ...
        weekday: Mapped[str] = mapped_column(String(9))
        # Sun, Mon, Tue, ...
        weekday_abbr: Mapped[str] = mapped_column(String(3))
        # 0=Sunday, 1=Monday
        weekday_num: Mapped[int]
        month_num: Mapped[int]
        # January, February, March, ...
        month: Mapped[str] = mapped_column(String(8))
        # Jan, Feb, Mar, ...
        month_abbr: Mapped[str] = mapped_column(String(3))
        year: Mapped[int]

    return Date


def make_Time(declarative_base: Type) -> Type:
    class Time(declarative_base):
        __tablename__ = "time_t"

        # HHMMSS as integer
        time_id: Mapped[int] = mapped_column(primary_key=True)
        # HH:MM:SS string
        time: Mapped[str] = mapped_column(String(8))
        hour: Mapped[int]
        minute: Mapped[int]
        second: Mapped[int]
        day_fraction: Mapped[float]

    return Time


def make_Observer(declarative_base: Type) -> Type:
    class Observer(declarative_base):
        __tablename__ = "observer_t"

        observer_id: Mapped[int] = mapped_column(primary_key=True)
        # Either Individual or Organization
        type: Mapped[ObserverType] = mapped_column(ObserverCol)
        # Person full name / Organization name
        name: Mapped[str] = mapped_column(String(255))
        # Person affiliation if any
        affiliation: Mapped[Optional[str]] = mapped_column(String(255))
        # Organization org_acronym, may also be applied to affiliation
        acronym: Mapped[Optional[str]] = mapped_column(String(16))
        # Person/Organization website URL
        website_url: Mapped[Optional[str]] = mapped_column(String(255))
        # Person/Organization contact org_email
        email: Mapped[Optional[str]] = mapped_column(String(64))
        # Version control attributes for Persons that change affiliations
        valid_since: Mapped[datetime] = mapped_column(DateTime)
        valid_until: Mapped[datetime] = mapped_column(DateTime)
        valid_state: Mapped[ValidState] = mapped_column(ValidStateCol)

    return Observer


def make_Location(declarative_base: Type) -> Type:
    class Location(declarative_base):
        __tablename__ = "location_t"

        location_id: Mapped[int] = mapped_column(primary_key=True)
        # Geographical longitude in decimal degrees
        longitude: Mapped[Optional[float]]
        # Geographical in decimal degrees
        latitude: Mapped[Optional[float]]
        # Meters above sea level
        elevation: Mapped[Optional[float]]
        # Descriptive name of this unitque location
        place: Mapped[str] = mapped_column(String(255))
        # village, town, city, etc name
        town: Mapped[str] = mapped_column(String(255))
        # province, county, etc..
        sub_region: Mapped[str] = mapped_column(String(255))
        # federal state, comunidad autonomica, etc..
        region: Mapped[str] = mapped_column(String(255))
        country: Mapped[str] = mapped_column(String(64))
        timezone: Mapped[str] = mapped_column(String(64))

        __table_args__ = (UniqueConstraint("longitude", "latitude"),)

    return Location


def make_Units(declarative_base: Type) -> Type:
    class Units(declarative_base):
        __tablename__ = "tess_units_t"

        units_id: Mapped[int] = mapped_column(primary_key=True)
        # federal state, comunidad autonomica, etc..
        timestamp_source: Mapped[TimestampSource] = mapped_column(TimestampSourceCol)
        reading_source: Mapped[ReadingSource] = mapped_column(ReadingSourceCol)

    return Units


def make_Tess(declarative_base: Type) -> Type:
    class Tess(declarative_base):
        __tablename__ = "tess_t"

        tess_id: Mapped[int] = mapped_column(primary_key=True)
        mac_address: Mapped[str] = mapped_column(String(17), index=True)
        # Version control attributes for Persons that change affiliations
        valid_since: Mapped[datetime] = mapped_column(DateTime)
        valid_until: Mapped[datetime] = mapped_column(DateTime)
        valid_state: Mapped[ValidState] = mapped_column(ValidStateCol)
        model: Mapped[PhotometerModel] = mapped_column(PhotometerModelCol)
        firmware: Mapped[str] = mapped_column(String(255))
        authorised: Mapped[bool] = mapped_column(Boolean)
        registered: Mapped[RegisterState] = mapped_column(RegisterStateCol)
        # From 1 to 4
        nchannels: Mapped[int]
        zp1: Mapped[float]
        filter1: Mapped[str] = mapped_column(String(64))
        offset1: Mapped[float] = mapped_column(Float, insert_default=0.0)
        zp2: Mapped[Optional[float]]
        filter2: Mapped[Optional[str]] = mapped_column(String(64))
        offset2: Mapped[float] = mapped_column(Float, insert_default=0.0)
        zp3: Mapped[Optional[float]]
        filter3: Mapped[Optional[str]] = mapped_column(String(64))
        offset3: Mapped[float] = mapped_column(Float, insert_default=0.0)
        zp4: Mapped[Optional[float]]
        filter4: Mapped[Optional[str]] = mapped_column(String(64))
        offset4: Mapped[float] = mapped_column(Float, insert_default=0.0)
        location_id: Mapped[int] = mapped_column(ForeignKey("location_t.location_id"), default=-1)
        observer_id: Mapped[int] = mapped_column(ForeignKey("observer_t.observer_id"), default=-1)

        # This is not a real column, it s meant for the ORM
        location: Mapped["Location"] = relationship()  # noqa: F821
        observer: Mapped["Observer"] = relationship()  # noqa: F821

    return Tess


# This is handled poorly due to the existing underlyng data schema
# that we must follow
# A better choice wpuld have been a relationship table but ....
def make_NameMapping(declarative_base: Type) -> Type:
    class NameMapping(declarative_base):
        __tablename__ = "name_to_mac_t"

        rowid: Mapped[int] = mapped_column(primary_key=True)
        name: Mapped[str] = mapped_column(String(64), index=True)
        mac_address: Mapped[str] = mapped_column(String(17), index=True)

        valid_since: Mapped[datetime] = mapped_column(DateTime)
        valid_until: Mapped[datetime] = mapped_column(DateTime)
        valid_state: Mapped[ValidState] = mapped_column(ValidStateCol)

        def __repr__(self) -> str:
            return f"NameMapping(name={self.name}, mac={self.mac_address}, valid_since={self.valid_since}, valid_until={self.valid_until}, valid_state={self.valid_state})"

    return NameMapping


# =====
# VIEWS
# =====


def make_TessView(
    declarative_base: Type, Tess: Type, NameMapping: Type, Location: Type, Observer: Type
) -> Type:
    tess_view = view(
        name="tess_v",
        metadata=declarative_base.metadata,
        selectable=select(
            Tess.tess_id.label("tess_id"),
            Tess.mac_address.label("mac_address"),
            NameMapping.name.label("name"),
            Tess.valid_since.label("valid_since"),
            Tess.valid_until.label("valid_until"),
            Tess.valid_state.label("valid_state"),
            Tess.model.label("model"),
            Tess.firmware.label("firmware"),
            Tess.authorised.label("authorised"),
            Tess.registered.label("registered"),
            Tess.nchannels.label("nchannels"),
            Tess.zp1.label("zp1"),
            Tess.filter1.label("filter1"),
            Tess.offset1.label("offset1"),
            Tess.zp2.label("zp2"),
            Tess.filter2.label("filter2"),
            Tess.offset2.label("offset2"),
            Tess.zp3.label("zp3"),
            Tess.filter3.label("filter3"),
            Tess.offset3.label("offset3"),
            Tess.zp4.label("zp4"),
            Tess.filter4.label("filter4"),
            Tess.offset4.label("offset4"),
            Location.longitude.label("longitude"),
            Location.latitude.label("latitude"),
            Location.elevation.label("elevation"),
            Location.place.label("place"),
            Location.town.label("town"),
            Location.sub_region.label("sub_region"),
            Location.region.label("region"),
            Location.country.label("country"),
            Location.timezone.label("timezone"),
            Observer.name.label("name"),
            Observer.type.label("type"),
            Observer.affiliation.label("affiliation"),
            Observer.acronym.label("acronym"),
        )
        .select_from(Tess)
        .join(Location, Location.location_id == Tess.location_id)
        .join(Observer, Observer.observer_id == Tess.observer_id)
        .join(NameMapping, NameMapping.mac_address == Tess.mac_address)
        .where(NameMapping.valid_state == ValidState.CURRENT),
    )

    class TessView(declarative_base):
        __table__ = tess_view

    return TessView


def make_TessReadings(declarative_base: Type) -> Type:
    class TessReadings(declarative_base):
        __tablename__ = "tess_readings_t"

        date_id: Mapped[int] = mapped_column(ForeignKey("date_t.date_id"))
        time_id: Mapped[int] = mapped_column(ForeignKey("time_t.time_id"))
        tess_id: Mapped[int] = mapped_column(ForeignKey("tess_t.tess_id"))
        location_id: Mapped[int] = mapped_column(ForeignKey("location_t.location_id"), default=-1)
        observer_id: Mapped[int] = mapped_column(ForeignKey("observer_t.observer_id"), default=-1)
        units_id: Mapped[int] = mapped_column(ForeignKey("tess_units_t.units_id"))
        sequence_number: Mapped[int]
        frequency: Mapped[float]  # Hz
        magnitude: Mapped[float]  # mag/arcsec^2
        box_temperature: Mapped[float]  # degrees celsius
        sky_temperature: Mapped[float]  # degrees celsius
        azimuth: Mapped[Optional[float]]  # decimal degrees
        altitude: Mapped[Optional[float]]  # decimal degrees
        longitude: Mapped[Optional[float]]  # decimal degrees
        latitude: Mapped[Optional[float]]  # decimal degrees
        elevation: Mapped[Optional[float]]  # meters above sea level
        signal_strength: Mapped[int]
        hash: Mapped[Optional[str]] = mapped_column(String(6))  # optional, to verify readings

        __table_args__ = (PrimaryKeyConstraint(date_id, time_id, tess_id),)

    return TessReadings


def make_Tess4cReadings(declarative_base: Type) -> Type:
    class Tess4cReadings(declarative_base):
        __tablename__ = "tess_readings4c_t"

        date_id: Mapped[int] = mapped_column(ForeignKey("date_t.date_id"))
        time_id: Mapped[int] = mapped_column(ForeignKey("time_t.time_id"))
        tess_id: Mapped[int] = mapped_column(ForeignKey("tess_t.tess_id"))
        location_id: Mapped[int] = mapped_column(ForeignKey("location_t.location_id"), default=-1)
        observer_id: Mapped[int] = mapped_column(ForeignKey("observer_t.observer_id"), default=-1)
        units_id: Mapped[int] = mapped_column(ForeignKey("tess_units_t.units_id"))
        sequence_number: Mapped[int]
        freq1: Mapped[float]  # Hz
        mag1: Mapped[float]  # mag/arcsec^2
        freq2: Mapped[float]  # Hz
        mag2: Mapped[float]  # mag/arcsec^2
        freq3: Mapped[float]  # Hz
        mag3: Mapped[float]  # mag/arcsec^2
        freq4: Mapped[float]  # Hz
        mag4: Mapped[float]  # mag/arcsec^2
        box_temperature: Mapped[float]  # degrees celsius
        sky_temperature: Mapped[float]  # degrees celsius
        azimuth: Mapped[Optional[float]]  # decimal degrees
        altitude: Mapped[Optional[float]]  # decimal degrees
        longitude: Mapped[Optional[float]]  # decimal degrees
        latitude: Mapped[Optional[float]]  # decimal degrees
        elevation: Mapped[Optional[float]]  # meters above sea level
        signal_strength: Mapped[int]
        hash: Mapped[Optional[str]] = mapped_column(String(6))  # optional, to verify readings

        __table_args__ = (PrimaryKeyConstraint(date_id, time_id, tess_id),)

    return Tess4cReadings
