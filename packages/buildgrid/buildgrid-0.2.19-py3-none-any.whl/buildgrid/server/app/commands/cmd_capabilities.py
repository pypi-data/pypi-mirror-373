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


import sys
from typing import Any

import click
from google.protobuf import json_format

from buildgrid.server.client.capabilities import CapabilitiesInterface
from buildgrid.server.client.channel import setup_channel
from buildgrid.server.exceptions import InvalidArgumentError

from ..cli import pass_context


@click.command(name="capabilities", short_help="Capabilities service.")
@click.option(
    "--remote",
    type=click.STRING,
    default="http://localhost:50051",
    show_default=True,
    help="Remote execution server's URL (port defaults to 50051 if no specified).",
)
@click.option(
    "--auth-token",
    type=click.Path(exists=True, dir_okay=False),
    default=None,
    help="Authorization token for the remote.",
)
@click.option(
    "--client-key",
    type=click.Path(exists=True, dir_okay=False),
    default=None,
    help="Private client key for TLS (PEM-encoded).",
)
@click.option(
    "--client-cert",
    type=click.Path(exists=True, dir_okay=False),
    default=None,
    help="Public client certificate for TLS (PEM-encoded).",
)
@click.option(
    "--server-cert",
    type=click.Path(exists=True, dir_okay=False),
    default=None,
    help="Public server certificate for TLS (PEM-encoded).",
)
@click.option(
    "--instance-name", type=click.STRING, default=None, show_default=True, help="Targeted farm instance name."
)
@click.option("--action-id", type=str, help="Action ID.")
@click.option("--invocation-id", type=str, help="Tool invocation ID.")
@click.option("--correlation-id", type=str, help="Correlated invocation ID.")
@pass_context
def cli(
    context: Any,
    remote: str,
    instance_name: str,
    auth_token: str,
    client_key: str,
    client_cert: str,
    server_cert: str,
    action_id: str,
    invocation_id: str,
    correlation_id: str,
) -> None:
    """Entry point for the bgd-capabilities CLI command group."""
    try:
        context.channel, _ = setup_channel(
            remote,
            auth_token=auth_token,
            client_key=client_key,
            client_cert=client_cert,
            server_cert=server_cert,
            action_id=action_id,
            tool_invocation_id=invocation_id,
            correlated_invocations_id=correlation_id,
        )

    except InvalidArgumentError as e:
        click.echo(f"Error: {e}.", err=True)
        sys.exit(-1)

    context.instance_name = instance_name

    interface = CapabilitiesInterface(context.channel)
    try:
        response = interface.get_capabilities(context.instance_name)
    except Exception as e:
        click.echo(f"Error: Getting capabilities: {e}", err=True)
        sys.exit(-1)

    click.echo(json_format.MessageToJson(response))
