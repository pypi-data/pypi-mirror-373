# ----------------------------------------------------------------------
# Copyright (c) 2024 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------

# --------------------
# System wide imports
# -------------------

import logging
from datetime import datetime, timedelta, timezone
from itertools import batched, product
from argparse import ArgumentParser, Namespace

# -------------------
# Third party imports
# -------------------

from lica.sqlalchemy import sqa_logging
from lica.sqlalchemy.asyncio.dbase import create_engine_sessionclass
from lica.asyncio.cli import execute

# --------------
# local imports
# -------------

from .. import __version__
from .util import parser as prs
from ..asyncio import Date, Time, Location, Observer, Units
from ..constants import ObserverType, ValidState, TimestampSource, ReadingSource

# ----------------
# Module constants
# ----------------

DESCRIPTION = "TESS Database initial populate tool"

# -----------------------
# Module global variables
# -----------------------


# get the module/package logger

log = logging.getLogger(__name__.split(".")[-1])

# get the database engine and session factory object
engine, Session = create_engine_sessionclass(env_var="DATABASE_URL")

# -------------------
# Auxiliary functions
# -------------------


def julian_day(date: datetime) -> float:
    """Returns the Julian day number of a date at 0h UTC."""
    a = (14 - date.month) // 12
    y = date.year + 4800 - a
    m = date.month + 12 * a - 3
    return (date.day + ((153 * m + 2) // 5) + 365 * y + y // 4 - y // 100 + y // 400 - 32045) - 0.5


class TimeIterator:
    def __init__(self, step_seconds=1):
        self.step = timedelta(seconds=step_seconds)
        self.current = datetime(
            year=2000, month=1, day=1, hour=0, minute=0, second=0, microsecond=0
        )
        self.limit = datetime(year=2000, month=1, day=2, hour=0, minute=0, second=0, microsecond=0)

    def __iter__(self):
        return self

    def __next__(self) -> datetime:
        x = self.current
        if x == self.limit:
            raise StopIteration
        self.current += self.step
        return x


class DateIterator:
    def __init__(self, from_date: datetime, to_date: datetime):
        self.step = timedelta(days=1)
        self.current = from_date
        self.limit = to_date

    def __iter__(self):
        return self

    def __next__(self) -> datetime:
        x = self.current
        if x > self.limit:
            raise StopIteration
        self.current += self.step
        return x


# -------------
# CLI Functions
# -------------


async def cli_populate_date(session: Session, args: Namespace) -> None:
    log.info("Generating Date values")
    date_iterator = DateIterator(from_date=args.since, to_date=args.until)
    date_objs = (
        Date(
            date_id=d.year * 10000 + d.month * 100 + d.day,
            sql_date=d.strftime("%Y-%m-%d"),
            day=int(d.strftime("%d")),
            date=d.strftime("%d/%m/%Y"),
            day_year=int(d.strftime("%j")),
            julian_day=julian_day(d),
            weekday=d.strftime("%A"),
            weekday_abbr=d.strftime("%a"),
            weekday_num=int(d.strftime("%w")),  # 0 = Sunday
            month=d.strftime("%B"),
            month_num=int(d.strftime("%m")),
            month_abbr=d.strftime("%b"),
            year=int(d.strftime("%Y")),
        )
        for d in date_iterator
    )
    for i, batch in enumerate(batched(date_objs, args.batch_size), start=1):
        log.info("Writing Date batch #%d (%d records)", i, len(batch))
        async with session.begin():
            for obj in batch:
                session.add(obj)


async def cli_populate_time(session: Session, args: Namespace) -> None:
    log.info("Generating Time values")
    time_iterator = TimeIterator(step_seconds=args.seconds)
    time_objs = (
        Time(
            time_id=t.hour * 10000 + t.minute * 100 + t.second,
            time=t.strftime("%H:%M:%S"),
            hour=t.hour,
            minute=t.minute,
            second=t.second,
            day_fraction=(t.hour * 3600 + t.minute * 60 + t.second) / (24 * 60 * 60),
        )
        for t in time_iterator
    )
    for i, batch in enumerate(batched(time_objs, args.batch_size), start=1):
        log.info("Writing Time batch #%d (%d records)", i, len(batch))
        async with session.begin():
            for obj in batch:
                session.add(obj)


async def cli_populate_location(session: Session, args: Namespace) -> None:
    log.info("Generating Default Unknown Location value")
    location = Location(
        location_id=-1,
        longitude=None,
        latitude=None,
        elevation=None,
        place="Unknown",
        town="Unknown",
        sub_region="Unknown",
        region="Unknown",
        country="Unknown",
        timezone="Etc/UTC",
    )
    async with session.begin():
        session.add(location)


async def cli_populate_observer(session: Session, args: Namespace) -> None:
    log.info("Generating Default Unknown Observer value")
    observer = Observer(
        observer_id=-1,
        type=ObserverType.ORG,
        name="Unknown",
        valid_since=datetime(2000, 1, 1, tzinfo=timezone.utc),
        valid_until=datetime(2999, 12, 31, 23, 59, 59, tzinfo=timezone.utc),
        valid_state=ValidState.CURRENT,
    )
    async with session.begin():
        session.add(observer)

async def cli_populate_units(session: Session) -> None:
    log.info("Generating Default Units values")
    a_list =  ([v.value for v in ReadingSource], [v.value for v in TimestampSource], )
    for i, item in enumerate(product(*a_list)):
        unit = Units(
            units_id=i,
            timestamp_source = item[1],
            reading_source = item[0],
        )
        async with session.begin():
            session.add(unit)


async def cli_populate_all(session: Session, args: Namespace) -> None:
    await cli_populate_units(session)
    await cli_populate_observer(session, args)
    await cli_populate_location(session, args)
    await cli_populate_date(session, args)
    await cli_populate_time(session, args)


def add_args(parser: ArgumentParser) -> None:
    subparser = parser.add_subparsers(dest="command", required=True)
    p = subparser.add_parser(
        "date", parents=[prs.since(), prs.until(), prs.batch()], help="Load initial Date values"
    )
    p.set_defaults(func=cli_populate_date)
    p = subparser.add_parser(
        "time", parents=[prs.seconds(), prs.batch()], help="Load initial Time values"
    )
    p.set_defaults(func=cli_populate_time)
    p = subparser.add_parser("location", parents=[], help="Load initial Location values")
    p.set_defaults(func=cli_populate_location)
    p = subparser.add_parser("observer", parents=[], help="Load initial Observer values")
    p.set_defaults(func=cli_populate_observer)
    p = subparser.add_parser(
        "all",
        parents=[prs.since(), prs.until(), prs.seconds(), prs.batch()],
        help="Load all initial values",
    )
    p.set_defaults(func=cli_populate_all)


async def cli_main(args: Namespace) -> None:
    sqa_logging(args)
    async with Session() as session:
        await args.func(session, args)
    await engine.dispose()


def main():
    """The main entry point specified by pyproject.toml"""
    execute(
        main_func=cli_main,
        add_args_func=add_args,
        name=__name__,
        version=__version__,
        description=DESCRIPTION,
    )


if __name__ == "__main__":
    main()
