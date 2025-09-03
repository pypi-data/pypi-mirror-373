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


import sys
from typing import Any, Iterator

import click
from grpc import RpcError

from buildgrid._protos.build.bazel.remote.logstream.v1.remote_logstream_pb2 import CreateLogStreamRequest
from buildgrid._protos.build.bazel.remote.logstream.v1.remote_logstream_pb2_grpc import LogStreamServiceStub
from buildgrid._protos.google.bytestream.bytestream_pb2 import QueryWriteStatusRequest, ReadRequest, WriteRequest
from buildgrid._protos.google.bytestream.bytestream_pb2_grpc import ByteStreamStub
from buildgrid.server.client.channel import setup_channel

from ..cli import pass_context


def instanced_resource_name(instance_name: str, resource: str) -> str:
    """Prepend the resource name with the instance name if it is provided."""
    if instance_name:
        return f"{instance_name}/{resource}"
    return resource


@click.group(name="logstream", short_help="LogStream commands.")
@click.option(
    "--remote",
    type=click.STRING,
    default="http://localhost:50051",
    show_default=True,
    help="Remote execution server's URL (port defaults to 50051 if no specified).",
)
@click.option("--instance-name", type=click.STRING, default="", show_default=True, help="Targeted farm instance name.")
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
@pass_context
def cli(
    context: Any, remote: str, instance_name: str, auth_token: str, client_key: str, client_cert: str, server_cert: str
) -> None:
    context.channel, _ = setup_channel(
        remote, auth_token=auth_token, client_key=client_key, client_cert=client_cert, server_cert=server_cert
    )
    context.instance_name = instance_name


@cli.command("create", short_help="Create a LogStream.")
@click.argument("parent", nargs=1, type=click.STRING, required=True)
@pass_context
def create(context: Any, parent: str) -> None:
    stub = LogStreamServiceStub(context.channel)

    parent = instanced_resource_name(context.instance_name, parent)

    request = CreateLogStreamRequest(parent=parent)
    try:
        logstream = stub.CreateLogStream(request)
    except RpcError as e:
        click.echo(f"Error: {e.details()}", err=True)
        sys.exit(-1)

    click.echo(logstream)


@cli.command("read", short_help="Read from a LogStream.")
@click.argument("resource", nargs=1, type=click.STRING, required=True)
@pass_context
def read(context: Any, resource: str) -> None:
    stub = ByteStreamStub(context.channel)

    resource = instanced_resource_name(context.instance_name, resource)

    request = ReadRequest(resource_name=resource)
    try:
        for response in stub.Read(request):
            click.echo(response.data, nl=False)
    except RpcError as e:
        click.echo(f"Error: {e.details()}", err=True)
        sys.exit(-1)


@cli.command("write", short_help="Write to a LogStream.")
@click.argument("resource", nargs=1, type=click.STRING, required=True)
@click.option("--wait-for-reader", is_flag=True)
@pass_context
def write(context: Any, resource: str, wait_for_reader: bool) -> None:
    stub = ByteStreamStub(context.channel)

    resource = instanced_resource_name(context.instance_name, resource)

    if wait_for_reader:
        try:
            query_write_status = QueryWriteStatusRequest(resource_name=resource)
            stub.QueryWriteStatus(query_write_status)
        except RpcError as e:
            click.echo(f"Error calling QueryWriteStatus: {e.details()}", err=True)
            sys.exit(-1)

    def _write_request_stream(name: str) -> Iterator[WriteRequest]:
        offset = 0
        finished = False
        while not finished:
            line = input("log line (empty line ends the stream): ").strip()
            finished = line == ""

            request = WriteRequest()
            request.resource_name = name
            request.data = line.encode("utf-8")
            request.write_offset = offset
            request.finish_write = finished

            yield request

            offset += 1

    try:
        requests = _write_request_stream(resource)
        stub.Write(requests)
    except RpcError as e:
        click.echo(f"Writing to stream failed: {e.details()}", err=True)
        sys.exit(-1)
