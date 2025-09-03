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
CommandLineInterface
===================

Any files in the commands/ folder with the name cmd_*.py
will be attempted to be imported.
"""

import importlib
import logging
import os
import sys
from typing import Any, cast

import click
import grpc
from importlib_resources import files

from buildgrid.server.logging import JSONFormatter
from buildgrid.server.metadata import ctx_grpc_request_id
from buildgrid.server.settings import LOG_RECORD_FORMAT

CONTEXT_SETTINGS = {
    "auto_envvar_prefix": "BUILDGRID",
    "max_content_width": 1000,  # do not truncate option help unnecessarily
}


class Context:
    def __init__(self) -> None:
        self.verbose: bool = False
        self.channel: grpc.Channel | None = None
        self.cas_channel: grpc.Channel | None = None
        self.operations_channel: grpc.Channel | None = None
        self.cache_channel: grpc.Channel | None = None
        self.logstream_channel: grpc.Channel | None = None
        self.instance_name: str = ""

        self.user_home: str = os.getcwd()


pass_context = click.make_pass_decorator(Context, ensure=True)
cmd_folder = files("buildgrid.server.app").joinpath("commands")

commands_namespace = "buildgrid.server.app.commands"


class App(click.Group):
    def list_commands(self, ctx: Any) -> list[str]:
        """Lists available command names."""
        commands = []
        for filename in os.listdir(cmd_folder):
            if filename.endswith(".py") and filename.startswith("cmd_"):
                command_name = filename[4:-3].replace("_", "-")
                commands.append(command_name)
        commands.sort()

        return commands

    def get_command(self, ctx: Any, cmd_name: str) -> click.Command:
        """Looks-up and loads a particular command by name."""
        try:
            module_name = cmd_name.replace("-", "_")
            module = importlib.import_module(f"{commands_namespace}.cmd_{module_name}")
        except ImportError as e:
            failed_import_name = e.name
            assert failed_import_name is not None
            if failed_import_name.startswith(commands_namespace):
                click.echo(f"Error: No such command: [{cmd_name}].", err=True)
                sys.exit(-1)
            else:
                return click.Command(cmd_name, help=f"[unavailable, module '{e.name}' is not installed]")

        return cast(click.Command, module.cli)


class DebugFilter(logging.Filter):
    def __init__(self, debug_domains: str, name: str = "") -> None:
        super().__init__(name=name)
        # Recursive dict. RDict = dict[str, RDict]
        self.__domains_tree: dict[str, Any] = {}

        for domain in debug_domains.split(":"):
            domains_tree = self.__domains_tree
            for label in domain.split("."):
                if all(key not in domains_tree for key in [label, "*"]):
                    domains_tree[label] = {}
                domains_tree = domains_tree[label]

    def filter(self, record: logging.LogRecord) -> bool:
        # Only evaluate DEBUG records for filtering
        if record.levelname != "DEBUG":
            return True
        domains_tree, last_match = self.__domains_tree, None
        for label in record.name.split("."):
            if all(key not in domains_tree for key in [label, "*"]):
                return False
            last_match = label if label in domains_tree else "*"
            domains_tree = domains_tree[last_match]
        if domains_tree and "*" not in domains_tree:
            return False
        return True


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = ctx_grpc_request_id.get() or "---"
        return True


def setup_logging(verbosity: int = 0, json_logs: bool = False, debug_mode: bool = False) -> None:
    """Deals with loggers verbosity"""
    asyncio_logger = logging.getLogger("asyncio")
    root_logger = logging.getLogger()

    log_handler = logging.StreamHandler(stream=sys.stdout)
    for log_filter in root_logger.filters:
        log_handler.addFilter(log_filter)

    log_handler.addFilter(RequestIdFilter())

    formatter = JSONFormatter() if json_logs else logging.Formatter(fmt=LOG_RECORD_FORMAT)
    log_handler.setFormatter(formatter)
    logging.basicConfig(handlers=[log_handler])

    if verbosity == 1:
        root_logger.setLevel(logging.WARNING)
    elif verbosity == 2:
        root_logger.setLevel(logging.INFO)
    elif verbosity >= 3:
        root_logger.setLevel(logging.DEBUG)
    else:
        root_logger.setLevel(logging.ERROR)

    if not debug_mode:
        asyncio_logger.setLevel(logging.CRITICAL)
    else:
        asyncio_logger.setLevel(logging.DEBUG)
        root_logger.setLevel(logging.DEBUG)


@click.command(cls=App, context_settings=CONTEXT_SETTINGS)
@pass_context
def cli(context: Any) -> None:
    """BuildGrid's client and server CLI front-end."""
    root_logger = logging.getLogger()

    # Clean-up root logger for any pre-configuration:
    for log_handler in root_logger.handlers[:]:
        root_logger.removeHandler(log_handler)
    for log_filter in root_logger.filters[:]:
        root_logger.removeFilter(log_filter)

    # Filter debug messages using BGD_MESSAGE_DEBUG value:
    debug_domains = os.environ.get("BGD_MESSAGE_DEBUG", None)
    if debug_domains:
        root_logger.addFilter(DebugFilter(debug_domains))
