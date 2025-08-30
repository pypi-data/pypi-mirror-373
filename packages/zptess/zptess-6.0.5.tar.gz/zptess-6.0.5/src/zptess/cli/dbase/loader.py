# ----------------------------------------------------------------------
# Copyright (c) 2024 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------

# --------------------
# System wide imports
# -------------------

import os
import csv
import logging
import datetime

from argparse import ArgumentParser, Namespace

# -------------------
# Third party imports
# -------------------


from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession as AsyncSessionClass
from sqlalchemy.ext.asyncio import async_sessionmaker

from lica.sqlalchemy import sqa_logging
from lica.sqlalchemy.asyncio.dbase import AsyncSession
from lica.asyncio.cli import execute

# --------------
# local imports
# -------------

from ... import __version__
from ..util import parser as prs
from ...lib.dbase.model import Config, Round, Photometer, Sample, Summary, Batch

# ----------------
# Module constants
# ----------------

DESCRIPTION = "TESS-W Calibration Database data loader tool"

# -----------------------
# Module global variables
# -----------------------

ORPHANED_SESSIONS_IN_ROUNDS = set()
ORPHANED_SESSIONS_IN_SAMPLES = set()

# get the root logger
log = logging.getLogger(__name__.split(".")[-1])

# -------------------
# Auxiliary functions
# -------------------


async def load_batch(path: str, async_session: async_sessionmaker[AsyncSessionClass]) -> None:
    async with async_session() as session:
        async with session.begin():
            log.info("loading batch data from %s", path)
            with open(path, newline="") as f:
                reader = csv.DictReader(f, delimiter=";")
                for row in reader:
                    row["email_sent"] = True if row["email_sent"] == "1" else False
                    row["begin_tstamp"] = (
                        datetime.datetime.strptime(row["begin_tstamp"], "%Y-%m-%dT%H:%M:%S")
                        if row["begin_tstamp"]
                        else None
                    )
                    row["end_tstamp"] = (
                        datetime.datetime.strptime(row["end_tstamp"], "%Y-%m-%dT%H:%M:%S")
                        if row["end_tstamp"]
                        else None
                    )
                    batch = Batch(**row)
                    log.info("%r", batch)
                    session.add(batch)


async def load_config(path: str, async_session: async_sessionmaker[AsyncSessionClass]) -> None:
    async with async_session() as session:
        async with session.begin():
            log.info("loading config from %s", path)
            with open(path, newline="") as f:
                reader = csv.DictReader(f, delimiter=";")
                for row in reader:
                    if row["section"] == "database" and row["prop"] == "version":
                        value = int(row["value"]) + 1
                        row["value"] = f"{value:02d}"
                    config = Config(**row)
                    log.info("%r", config)
                    session.add(config)


async def load_photometer(path: str, async_session: async_sessionmaker[AsyncSessionClass]) -> None:
    async with async_session() as session:
        async with session.begin():
            log.info("loading photometer from %s", path)
            with open(path, newline="") as f:
                reader = csv.DictReader(f, delimiter=";")
                for row in reader:
                    for key in ("sensor", "firmware", "filter", "collector", "comment"):
                        row[key] = None if not row[key] else row[key]
                    row["freq_offset"] = 0.0
                    phot = Photometer(**row)
                    log.info("%r", phot)
                    session.add(phot)


async def _load_summary(path: str, async_session: async_sessionmaker[AsyncSessionClass]) -> None:
    async with async_session() as session:
        async with session.begin():
            log.info("loading summary from %s", path)
            with open(path, newline="") as f:
                reader = csv.DictReader(f, delimiter=";")
                for row in reader:
                    mac = row["mac"]
                    name = row["name"]
                    del row["mac"]
                    del row["name"]
                    row["session"] = datetime.datetime.strptime(row["session"], "%Y-%m-%dT%H:%M:%S")
                    row["upd_flag"] = True if row["upd_flag"] == "1" else False
                    row["calibration"] = None if not row["calibration"] else row["calibration"]
                    for key in ("zero_point", "zp_offset", "prev_zp", "freq", "mag"):
                        row[key] = float(row[key]) if row[key] else None
                    for key in ("zero_point_method", "freq_method", "nrounds", "comment"):
                        row[key] = None if not row[key] else row[key]
                    log.info("[%9s - %s]Processing row. %s", name, mac, row)
                    q = select(Photometer).where(Photometer.mac == mac, Photometer.name == name)
                    phot = (await session.scalars(q)).one()
                    summary = Summary(**row)
                    summary.photometer = phot
                    log.info("%r", summary)
                    session.add(summary)


async def _assign_batches(async_session: async_sessionmaker[AsyncSessionClass]) -> None:
    async with async_session() as session:
        async with session.begin():
            q = select(Batch)
            batches = (await session.scalars(q)).all()
            for batch in batches:
                log.info("Handling batch %s", batch)
                q = select(Summary).where(
                    Summary.session.between(batch.begin_tstamp, batch.end_tstamp)
                )
                summaries = (await session.scalars(q)).all()
                for summary in summaries:
                    log.info("Assigning summary %s to batch %s", summary, batch)
                    summary.batch = batch
                    session.add(summary)


async def load_summary(path: str, async_session: async_sessionmaker[AsyncSessionClass]) -> None:
    await _load_summary(path, async_session)
    await _assign_batches(async_session)


async def assign_batches(async_session: async_sessionmaker[AsyncSessionClass]) -> None:
    await _assign_batches(async_session)


async def load_rounds(path: str, async_session: async_sessionmaker[AsyncSessionClass]) -> None:
    async with async_session() as session:
        async with session.begin():
            log.info("loading rounds from %s", path)
            with open(path, newline="") as f:
                reader = csv.DictReader(f, delimiter=";")
                for row in reader:
                    row["seq"] = row["round"]
                    del row["round"]
                    meas_session = datetime.datetime.strptime(row["session"], "%Y-%m-%dT%H:%M:%S")
                    row["begin_tstamp"] = (
                        datetime.datetime.strptime(row["begin_tstamp"], "%Y-%m-%dT%H:%M:%S.%f")
                        if row["begin_tstamp"]
                        else None
                    )
                    row["end_tstamp"] = (
                        datetime.datetime.strptime(row["end_tstamp"], "%Y-%m-%dT%H:%M:%S.%f")
                        if row["end_tstamp"]
                        else None
                    )
                    for key in ("freq", "stddev", "mag", "zp_fict", "zero_point", "duration"):
                        row[key] = float(row[key]) if row[key] else None
                    q = select(Summary).where(
                        Summary.session == meas_session, Summary.role == row["role"]
                    )
                    summary = (await session.scalars(q)).one_or_none()
                    if not summary:
                        log.warn(
                            "No summary for round: session=%(session)s seq=%(seq)s, role=%(role)s,",
                            row,
                        )
                        ORPHANED_SESSIONS_IN_ROUNDS.add(meas_session)
                        continue
                    del row["session"]
                    round_ = Round(**row)
                    round_.summary = summary
                    log.info("%r", round_)
                    session.add(round_)
    log.warn("###########################")
    log.warn("ORPHANED SESSIONS IN ROUNDS")
    log.warn("###########################")
    for s in sorted(ORPHANED_SESSIONS_IN_ROUNDS):
        log.warn(s)


async def load_samples(path, async_session: async_sessionmaker[AsyncSessionClass]) -> None:
    async with async_session() as session:
        async with session.begin():
            log.info("loading samples from %s", path)
            with open(path, newline="") as f:
                reader = csv.DictReader(f, delimiter=";")
                for row in reader:
                    meas_session = datetime.datetime.strptime(row["session"], "%Y-%m-%dT%H:%M:%S")
                    del row["session"]
                    row["tstamp"] = datetime.datetime.strptime(
                        row["tstamp"], "%Y-%m-%dT%H:%M:%S.%f"
                    )
                    row["temp_box"] = float(row["temp_box"]) if row["temp_box"] else None
                    row["freq"] = float(row["freq"])
                    row["seq"] = int(row["seq"]) if row["seq"] else None
                    sample = Sample(**row)
                    q = (
                        select(Round)
                        .join(Summary)
                        .where(Summary.session == meas_session, Summary.role == row["role"])
                    )
                    rounds_per_summary = (await session.scalars(q)).all()
                    if not rounds_per_summary:
                        ORPHANED_SESSIONS_IN_SAMPLES.add(meas_session)
                        log.warn("Can't find session %s for this sample %s", meas_session, sample)
                        continue
                    q = select(Summary).where(
                        Summary.session == meas_session, Summary.role == row["role"]
                    )
                    sample.summary = (await session.scalars(q)).one()
                    for r in rounds_per_summary:
                        if r.begin_tstamp <= sample.tstamp <= r.end_tstamp:
                            sample.rounds.append(r)  # no need to do r.append(sample) !!!
                    log.info("%r", sample)
                    session.add(sample)
    log.warn("============================")
    log.warn("ORPHANED SESSIONS IN SAMPLES")
    log.warn("============================")
    for s in sorted(ORPHANED_SESSIONS_IN_SAMPLES):
        log.warn(s)


# --------------
# main functions
# --------------

TABLE = {
    "config": load_config,
    "batch": load_batch,
    "photometer": load_photometer,
    "summary": load_summary,
    "assign": assign_batches,
    "rounds": load_rounds,
    "samples": load_samples,
}


async def loader(args) -> None:
    if args.command not in ("all", "nosamples", "norounds", "assign"):
        func = TABLE[args.command]
        path = os.path.join(args.input_dir, args.command + ".csv")
        await func(path, AsyncSession)
        if args.command == "all":
            assert ORPHANED_SESSIONS_IN_ROUNDS == ORPHANED_SESSIONS_IN_SAMPLES, (
                f"Difference is {ORPHANED_SESSIONS_IN_ROUNDS - ORPHANED_SESSIONS_IN_SAMPLES}"
            )
    elif args.command == "norounds":
        for name in ("config", "batch", "photometer", "summary"):
            path = os.path.join(args.input_dir, name + ".csv")
            func = TABLE[name]
            await func(path, AsyncSession)
    elif args.command == "nosamples":
        for name in ("config", "batch", "photometer", "summary", "rounds"):
            path = os.path.join(args.input_dir, name + ".csv")
            func = TABLE[name]
            await func(path, AsyncSession)
    elif args.command == "assign":
        func = TABLE[name]
        await func(AsyncSession)
    else:
        for name in ("config", "batch", "photometer", "summary", "rounds", "samples"):
            path = os.path.join(args.input_dir, name + ".csv")
            func = TABLE[name]
            await func(path, AsyncSession)


def add_args(parser: ArgumentParser) -> None:
    subparser = parser.add_subparsers(dest="command")
    subparser.add_parser("config", parents=[prs.idir()], help="Load config CSV")
    subparser.add_parser("batch", parents=[prs.idir()], help="Load batch CSV")
    subparser.add_parser("photometer", parents=[prs.idir()], help="Load photometer CSV")
    subparser.add_parser("summary", parents=[prs.idir()], help="Load summary CSV")
    subparser.add_parser("assign", parents=[], help="Assign summaries to batches")
    subparser.add_parser("rounds", parents=[prs.idir()], help="Load rounds CSV")
    subparser.add_parser("samples", parents=[prs.idir()], help="Load samples CSV")
    subparser.add_parser("nosamples", parents=[prs.idir()], help="Load all CSVs except samples")
    subparser.add_parser("all", parents=[prs.idir()], help="Load all CSVs")


async def cli_main(args: Namespace) -> None:
    sqa_logging(args)
    await loader(args)


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
