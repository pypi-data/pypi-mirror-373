# Copyright (C) 2019 Bloomberg LP
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

from buildgrid._protos.build.bazel.remote.execution.v2 import remote_execution_pb2
from buildgrid.server.client.actioncache import query
from buildgrid.server.client.cas import download
from buildgrid.server.client.channel import setup_channel
from buildgrid.server.exceptions import InvalidArgumentError
from buildgrid.server.utils.digests import create_digest, parse_digest

from ..cli import pass_context


@click.group(name="action-cache", short_help="Query and update the action cache service.")
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
    help="Public server certificate for TLS (PEM-encoded)",
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
    """Entry-point for the ``bgd action-cache`` CLI command group."""
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


@cli.command("get", short_help="Retrieves a cached action-result.")
@click.argument("action-digest-string", nargs=1, type=click.STRING, required=True)
@click.option("--json", is_flag=True, show_default=True, help="Print action result in JSON format.")
@pass_context
def get(context: Any, action_digest_string: str, json: bool) -> None:
    """Entry-point of the ``bgd action-cache get`` CLI command.

    Note:
        Digest strings are expected to be like: ``{hash}/{size_bytes}``.
    """
    action_digest = parse_digest(action_digest_string)
    if action_digest is None:
        click.echo(f"Error: Invalid digest string '{action_digest_string}'.", err=True)
        sys.exit(-1)

    # Simply hit the action cache with the given action digest:
    with query(context.channel) as action_cache:
        try:
            action_result = action_cache.get(context.instance_name, action_digest)
        except Exception as e:
            click.echo(f"Error: Fetching from the action cache: {e}", err=True)
            sys.exit(-1)

    if action_result is not None:
        if not json:
            action_result_digest = create_digest(action_result.SerializeToString())

            click.echo(
                f"Hit: {action_digest.hash[:8]}/{action_digest.size_bytes}: "
                f"Result cached with digest=[{action_result_digest.hash}/{action_result_digest.size_bytes}]"
            )

            # TODO: Print ActionResult details?

        else:
            click.echo(json_format.MessageToJson(action_result))

    else:
        click.echo(
            f"Miss: {action_digest.hash[:8]}/{action_digest.size_bytes}: No associated result found in cache..."
        )


@cli.command("update", short_help="Maps an action to a given action-result.")
@click.argument("action-digest-string", nargs=1, type=click.STRING, required=True)
@click.argument("action-result-digest-string", nargs=1, type=click.STRING, required=True)
@pass_context
def update(context: Any, action_digest_string: str, action_result_digest_string: str) -> None:
    """Entry-point of the ``bgd action-cache update`` CLI command.

    Note:
        Digest strings are expected to be like: ``{hash}/{size_bytes}``.
    """
    action_digest = parse_digest(action_digest_string)
    if action_digest is None:
        click.echo(f"Error: Invalid digest string '{action_digest_string}'.", err=True)
        sys.exit(-1)

    action_result_digest = parse_digest(action_result_digest_string)
    if action_result_digest is None:
        click.echo(f"Error: Invalid digest string '{action_result_digest_string}'.", err=True)
        sys.exit(-1)

    # We have to download the ActionResult message from CAS first...
    with download(context.channel, instance=context.instance_name) as downloader:
        try:
            action_result = downloader.get_message(action_result_digest, remote_execution_pb2.ActionResult())
        except Exception as e:
            click.echo(f"Error: Fetching ActionResult from CAS: {e}", err=True)
            sys.exit(-1)

        # And only then we can update the action cache for the given digest:
        with query(context.channel) as action_cache:
            try:
                action_result_update = action_cache.update(context.instance_name, action_digest, action_result)
            except Exception as e:
                click.echo(f"Error: Uploading to ActionCache: {e}", err=True)
                sys.exit(-1)

            if action_result_update is None:
                click.echo(
                    "Error: Failed updating cache result for action="
                    f"[{action_digest.hash}/{action_digest.size_bytes}].",
                    err=True,
                )
                sys.exit(-1)
