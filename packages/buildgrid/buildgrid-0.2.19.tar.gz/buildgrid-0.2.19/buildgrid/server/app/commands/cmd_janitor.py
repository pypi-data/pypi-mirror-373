# Copyright (C) 2024 Bloomberg LP
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  <http://www.apache.org/licenses/LICENSE-2.0>
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
CAS Janitor
===========

Cleanup daemon which is responsible for picking up any mess left by the regular cleaner.

The regular cleaner is required to synchronize between the index and the storage, and
so it is possible to get into a state where the blob is removed from the index but not
removed from the storage (eg. in the event of an error when removing the blob from
storage after removing it's index entry).

The Janitor takes care of this situation by regularly iterating over the entire
storage and removing any blobs which aren't referenced by an index. This ensures that
any hanging blobs are removed in a timely manner and the storage space consumption
doesn't spiral up out of control.

"""


import os
import signal
import sys
import threading
from contextlib import ExitStack
from types import FrameType

import click

from buildgrid.server.cleanup.janitor.config import parse_janitor_config
from buildgrid.server.cleanup.janitor.index import IndexLookup, RedisIndexLookup, SqlIndexLookup
from buildgrid.server.cleanup.janitor.s3 import S3Janitor
from buildgrid.server.cleanup.janitor.sql import SQLJanitor
from buildgrid.server.cleanup.janitor.types import Janitor, JanitorConfig
from buildgrid.server.monitoring import get_monitoring_bus

from ..cli import setup_logging


@click.group(name="janitor", short_help="Service to clean up orphaned blobs from S3 buckets.")
def cli() -> None:
    pass


@cli.command("start", short_help="Start a CAS Janitor process.")
@click.argument("CONFIG_PATH", type=click.Path(file_okay=True, dir_okay=False, exists=True, writable=False))
@click.option("-v", "--verbose", count=True, help="Increase log verbosity level.")
@click.option("--json-logs", is_flag=True, help="Formats logs as JSON")
def start(
    config_path: "os.PathLike[str]",
    verbose: int,
    json_logs: bool,
) -> None:
    setup_logging(verbosity=verbose, json_logs=json_logs)

    click.echo(f"Starting up a CAS janitor: config_path={config_path}")

    config = parse_janitor_config(config_path)

    # Janitoring for an SQL CAS index
    if config.sql_connection_string is not None:
        index: IndexLookup = SqlIndexLookup(config.sql_connection_string)

    # Janitoring for a Redis CAS index
    elif config.redis is not None:
        index = RedisIndexLookup(config.redis)

    # No other janitor types are supported
    else:
        click.echo("Either redis or sql_connection_string is needed", err=True)
        sys.exit(-1)

    if config.s3 is None and config.sql_storage_config is None:
        click.echo("Either s3 or sql_storage_config is needed", err=True)
        sys.exit(-1)

    janitors: list[Janitor] = []

    def set_sleep_interval(janitor_config: JanitorConfig) -> None:
        if not janitor_config.sleep_interval:
            if not config.sleep_interval:
                click.echo("Sleep interval must be set", err=True)
                sys.exit(-1)
            else:
                janitor_config.sleep_interval = config.sleep_interval

    if config.sql_storage_config is not None:
        set_sleep_interval(config.sql_storage_config)
        janitors.append(SQLJanitor(config.sql_storage_config, index))

    if config.s3 is not None:
        set_sleep_interval(config.s3)
        janitors.append(S3Janitor(config.s3, index))

    if not janitors:
        click.echo("Janitor could not be properly created", err=True)
        sys.exit(-1)

    shutdown_requested = threading.Event()

    def stop_janitors(_signal: int | None, _frame: FrameType | None) -> None:
        shutdown_requested.set()

    signal.signal(signal.SIGTERM, stop_janitors)
    signal.signal(signal.SIGINT, stop_janitors)

    with ExitStack() as stack:
        stack.enter_context(get_monitoring_bus())
        for janitor in janitors:
            stack.enter_context(janitor)
        shutdown_requested.wait()
