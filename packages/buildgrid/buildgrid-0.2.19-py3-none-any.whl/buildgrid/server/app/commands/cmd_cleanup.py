# Copyright (C) 2020 Bloomberg LP
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
Cleanup command
=================

Create a BCS cleanup daemon
"""
import signal
import sys
from datetime import timedelta
from os import PathLike

import click

from buildgrid.server.app.cli import Context, pass_context, setup_logging
from buildgrid.server.app.settings.config import BuildgridConfig, CleanupConfig, populate_buildgrid_config
from buildgrid.server.app.settings.parser import load_config
from buildgrid.server.cas.storage.index.index_abc import IndexABC
from buildgrid.server.cleanup.cleanup import CASCleanUp
from buildgrid.server.monitoring import set_monitoring_bus


def parse_size(string: str) -> int:
    """Convert string with suffix representing memory unit, to integer."""
    multipliers = {"K": 1000, "M": 1000000, "G": 1000000000, "T": 1000000000000}
    string = string.upper()
    multiplier = multipliers.get(string[-1], 1)
    amount = float(string[0:-1]) if string[-1] in multipliers else float(string)
    return int(amount * multiplier)


def parse_time(string: str) -> timedelta:
    """Convert string with suffix representing time unit, to timedelta."""
    multipliers = {"M": 60, "H": 3600, "D": 86400, "W": 604800}
    string = string.upper()
    multiplier = multipliers.get(string[-1], 1)
    amount = float(string[0:-1]) if string[-1] in multipliers else float(string)
    return timedelta(seconds=amount * multiplier)


@click.group(name="cleanup", short_help="Start a local cleanup service.")
@pass_context
def cli(context: Context) -> None:
    pass


@cli.command("start", short_help="Setup a new cleanup instance.")
@click.argument("CONFIG_PATH", type=click.Path(file_okay=True, dir_okay=False, exists=True, writable=False))
@click.option("-v", "--verbose", count=True, help="Increase log verbosity level.")
@click.option("--dry-run", is_flag=True, help="Do not actually cleanup CAS")
@click.option("--sleep-interval", type=int, help="Seconds to sleep inbetween calls to cleanup")
@click.option(
    "--high-watermark",
    type=str,
    help="Storage size needed to trigger cleanup. K, M, G, and T "
    "suffixes are supported (kilobytes, megabytes, gigabytes, "
    "and terabytes respectively).",
)
@click.option(
    "--low-watermark",
    type=str,
    help="Storage size needed to stop cleanup. K, M, G, and T "
    "suffixes are supported (kilobytes, megabytes, gigabytes, "
    "and terabytes respectively).",
)
@click.option(
    "--batch-size",
    type=str,
    help="Number of bytes to clean up in one go. K, M, G, and T "
    "suffixes are supported (kilobytes, megabytes, gigabytes, "
    "and terabytes respectively).",
)
@click.option(
    "--only-if-unused-for",
    type=str,
    default="0",
    metavar="<INTEGER/FLOAT>[M/H/D/W]",
    help="Number of seconds old a blob must be for cleanup to delete it. "
    "Optional M, H, D, W suffixes are supported (minutes, hours, days, "
    "weeks respectively). For example, if the value 3D is specified. Cleanup will "
    "ignore all blobs which are 3 days or younger. If unspecified, the "
    "value will default to 0 seconds. "
    "Important note: "
    'The value of "--only-if-unused-for" should be greater than that of '
    'the "refresh-accesstime-older-than" parameter found in the sql-index '
    "configuration, which is used to protect the timestamp of blobs "
    "from being updated if they were last accessed too recently. "
    "In other words, to avoid a blob from being cleaned up sooner than expected due "
    "to the effect of suppressed accesstime update, allocate a more generous age "
    "that a blob is allowed to be unused-for.",
)
@click.option("--json-logs", is_flag=True, help="Formats logs as JSON")
@pass_context
def start(
    context: Context,
    config_path: "PathLike[str]",
    verbose: int,
    dry_run: bool,
    high_watermark: str | None,
    low_watermark: str | None,
    sleep_interval: int,
    batch_size: str | None,
    only_if_unused_for: str,
    json_logs: bool,
) -> None:
    """Entry point for the bgd-server CLI command group."""
    if dry_run and verbose < 2:
        # If we're doing a dry run, the only thing we care about is the INFO
        # level output, so bump up the verbosity if needed
        verbose = 2
    setup_logging(verbosity=verbose, json_logs=json_logs)

    settings = load_config(config_path)
    try:
        config = populate_buildgrid_config(settings)
    except ValueError as e:
        click.echo(f"Error: populating server config: {e}.", err=True)
        sys.exit(-1)

    if config.cleanup:
        cleanup = _create_cleanup_from_config(
            config,
            dry_run,
            sleep_interval=sleep_interval,
        )
    else:
        # If there's no cleanup section in the config, then validate some required options exist
        try:
            if high_watermark is None or low_watermark is None or batch_size is None:
                click.echo(
                    "ERROR: high-watermark, low-watermark, and batch-size must be specified when not defining "
                    "cleanup settings in the configuration."
                )
                sys.exit(-1)
            high_watermark_val = parse_size(high_watermark)
            low_watermark_val = parse_size(low_watermark)
            batch_size_val = parse_size(batch_size)
            only_if_unused_for_val = parse_time(only_if_unused_for)
        except ValueError:
            click.echo(
                "ERROR: Only 'K', 'M', 'G', and 'T' are supported as size suffixes "
                "for the high/low water marks and batch size."
            )
            sys.exit(-1)
        if low_watermark_val > high_watermark_val:
            click.echo("ERROR: The low water mark must be lower than the high water mark.")
            sys.exit(-1)
        batch_size_val = min(batch_size_val, high_watermark_val - low_watermark_val)
        cleanup = _create_cleanup_from_cmdline(
            config,
            dry_run,
            high_watermark_val,
            low_watermark_val,
            sleep_interval,
            batch_size_val,
            only_if_unused_for_val,
        )

    try:
        signal.signal(signal.SIGTERM, cleanup.stop)
        signal.signal(signal.SIGINT, cleanup.stop)
        try:
            cleanup.start()
        finally:
            cleanup.stop()

    except KeyError as e:
        click.echo(f"ERROR: Could not parse config: {e}.\n", err=True)
        sys.exit(-1)

    except KeyboardInterrupt:
        pass

    except Exception as e:
        click.echo(f"ERROR: Uncaught Exception: {e}.\n", err=True)
        sys.exit(-1)


def _create_cleanup_from_config(
    config: BuildgridConfig,
    dry_run: bool,
    sleep_interval: int,
) -> CASCleanUp:
    """Create a CASCleaner with most options set in the configuration file."""

    if monitoring_bus := config.monitoring:
        set_monitoring_bus(monitoring_bus)

    return CASCleanUp(
        cleanup_configs=config.cleanup,
        dry_run=dry_run,
        sleep_interval=sleep_interval,
        monitor=config.monitoring is not None,
    )


def _create_cleanup_from_cmdline(
    config: BuildgridConfig,
    dry_run: bool,
    high_watermark: int,
    low_watermark: int,
    sleep_interval: int,
    batch_size: int,
    only_if_unused_for: timedelta,
) -> CASCleanUp:
    """Create a CASCleaner without a dedicated cleanup config. Most options come from the
    command line. The passed configuration will be used to determine the indexes to cleanup,
    grabbing the first one per instance."""
    try:
        cleanup_configs = []
        for instance in config.instances:
            for storage in instance.storages:
                if isinstance(storage, IndexABC):
                    # Construct a dynamic config based on command line parameters and
                    # the discovered storage.
                    options = CleanupConfig(
                        name=instance.names[0],
                        index=storage,
                        high_watermark=high_watermark,
                        low_watermark=low_watermark,
                        high_blob_count_watermark=None,
                        low_blob_count_watermark=None,
                        batch_size=batch_size,
                        only_if_unused_for=only_if_unused_for,
                        large_blob_lifetime=None,
                        large_blob_threshold=None,
                        retry_limit=10,
                    )
                    cleanup_configs.append(options)
                    break
            else:
                click.echo(f"Warning: Skipping instance {instance.names}.", err=False)

    except KeyError as e:
        click.echo(f"Error: Storage/Index missing from configuration: {e}.", err=True)
        sys.exit(-1)

    if cleanup_configs:
        return CASCleanUp(
            cleanup_configs=cleanup_configs,
            dry_run=dry_run,
            sleep_interval=sleep_interval,
            monitor=config.monitoring is not None,
        )

    click.echo("Error: Did not find any indexes to clean.", err=True)
    sys.exit(-1)
