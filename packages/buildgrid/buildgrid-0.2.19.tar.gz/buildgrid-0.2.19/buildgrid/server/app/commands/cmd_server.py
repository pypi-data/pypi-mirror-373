# Copyright (C) 2018 Bloomberg LP
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
Server command
=================

Create a BuildGrid server.
"""

import functools
import os
import signal
import sys
from types import FrameType
from typing import Any

import click
from jsonschema.exceptions import ValidationError

from buildgrid.server.app.cli import Context, pass_context, setup_logging
from buildgrid.server.app.settings.config import populate_buildgrid_config
from buildgrid.server.app.settings.parser import load_config, validate_config
from buildgrid.server.auth.manager import set_auth_manager
from buildgrid.server.exceptions import PermissionDeniedError, ShutdownSignal
from buildgrid.server.limiter import set_limiter
from buildgrid.server.logging import buildgrid_logger
from buildgrid.server.monitoring import set_monitoring_bus
from buildgrid.server.sentry import set_sentry_client
from buildgrid.server.server import Server

LOGGER = buildgrid_logger(__name__)


@click.group(name="server", short_help="Start a local server instance.")
@pass_context
def cli(context: Context) -> None:
    pass


@cli.command(name="lint", short_help="Check the format of a buildgrid server configuration.")
@click.option("-v", "--verbose", count=True, help="Increase log verbosity level.")
@click.option("--json-logs", is_flag=True, help="Formats logs as JSON")
@click.argument("CONFIG", type=click.Path(file_okay=True, dir_okay=False, exists=True, writable=False))
@pass_context
def lint(context: Context, config: "os.PathLike[str]", verbose: int, json_logs: bool) -> None:
    setup_logging(verbosity=verbose, json_logs=json_logs)

    try:
        validate_config(config, strict=True)
    except ValidationError as e:
        click.echo(click.style(f"ERROR: Config ({config}) failed validation: {e}", fg="red", bold=True), err=True)
        sys.exit(-1)

    click.echo(click.style(f"Success: Config ({config}) passed validation", fg="green", bold=True))


@cli.command("start", short_help="Setup a new server instance.")
@click.argument("CONFIG", type=click.Path(file_okay=True, dir_okay=False, exists=True, writable=False))
@click.option("-v", "--verbose", count=True, help="Increase log verbosity level.")
@click.option("--pid-file", type=click.Path(dir_okay=False), help="Path to PID file")
@click.option("--json-logs", is_flag=True, help="Formats logs as JSON")
@pass_context
def start(
    context: Context, config: "os.PathLike[str]", verbose: int, pid_file: "os.PathLike[str]", json_logs: bool
) -> None:
    """Entry point for the bgd-server CLI command group."""
    setup_logging(verbosity=verbose, json_logs=json_logs)

    click.echo(f"\nLoading config from {config}")

    try:
        settings = load_config(config)
    except ValidationError as e:
        click.echo(click.style(f"ERROR: Config ({config}) failed validation: {e}", fg="red", bold=True), err=True)
        sys.exit(-1)

    try:
        server = _create_server_from_config(settings)

    except KeyError as e:
        click.echo(f"ERROR: Could not parse config: {e}.\n", err=True)
        sys.exit(-1)

    signalled = False

    def stop(sig: int, _: FrameType | None) -> None:
        nonlocal signalled
        if not signalled:
            signalled = True
            click.echo(click.style(f"Received signal {sig}, stopping server.", fg="red", bold=True))
            raise ShutdownSignal(f"Received signal {sig}")
        else:
            click.echo(click.style(f"Ignored signal {sig}, signal handler already triggered.", fg="yellow"))

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    on_server_start_cb = functools.partial(_create_new_pid_file, pid_file)
    click.echo(click.style("Starting BuildGrid server...", fg="green", bold=True))
    try:
        server.start(on_server_start_cb=on_server_start_cb)
    except (KeyboardInterrupt, ShutdownSignal):
        pass
    finally:
        server.stop()
        _remove_old_pid_file(pid_file)


def _remove_old_pid_file(pid_file: os.PathLike[str] | None) -> None:
    """Remove pid_file if it's set"""
    if not pid_file:
        return

    try:
        os.remove(pid_file)
    except os.error:
        LOGGER.error("Error deleting pid-file.", tags=dict(pid_file=str(pid_file)), exc_info=True)


def _create_new_pid_file(pid_file: os.PathLike[str] | None) -> None:
    if pid_file:
        with open(pid_file, "w", encoding="utf-8") as f:
            f.write(str(os.getpid()))

        LOGGER.info("Created pid-file.", tags=dict(pid_file=str(pid_file)))


def _create_server_from_config(raw_configuration: dict[str, Any]) -> Server:
    """Parses configuration and setup a fresh server instance."""

    try:
        config = populate_buildgrid_config(raw_configuration)
    except ValueError as e:
        click.echo(f"Error: populating server config: {e}.", err=True)
        sys.exit(-1)

    if any(name == "unnamed" for instance in config.instances for name in instance.names):
        click.echo("Error: The instance name 'unnamed' is reserved to avoid metrics collisions", err=True)
        sys.exit(-1)

    server = Server(
        server_reflection=config.server_reflection,
        grpc_compression=config.grpc_compression,
        is_instrumented=config.monitoring is not None,
        grpc_server_options=config.grpc_server_options,
        max_workers=config.thread_pool_size,
    )

    if monitoring_bus := config.monitoring:
        set_monitoring_bus(monitoring_bus)

    if auth := config.authorization:
        set_auth_manager(auth)

    if sentry := config.sentry:
        set_sentry_client(sentry)

    if limiter := config.limiter:
        set_limiter(limiter)

    try:
        for channel in config.server:
            server.add_port(channel.address, channel.credentials)

    except PermissionDeniedError as e:
        click.echo(f"Error: {e}.", err=True)
        sys.exit(-1)

    for instance in config.instances:
        for instance_name in instance.names:
            for service in instance.services:
                server.register_instance(instance_name, service)

    return server
