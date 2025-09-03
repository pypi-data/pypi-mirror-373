# Copyright (C) 2022 Bloomberg LP
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


from contextvars import ContextVar
from typing import Any, Iterable, cast

from grpc.aio import Metadata

from buildgrid._protos.build.bazel.remote.execution.v2.remote_execution_pb2 import RequestMetadata, ToolDetails
from buildgrid._protos.build.buildgrid.identity_pb2 import ClientIdentity
from buildgrid._protos.build.buildgrid.scheduling_pb2 import SchedulingMetadata
from buildgrid.server.auth.manager import get_context_client_identity
from buildgrid.server.settings import (
    CLIENT_IDENTITY_HEADER_NAME,
    REQUEST_METADATA_HEADER_NAME,
    REQUEST_METADATA_TOOL_NAME,
    REQUEST_METADATA_TOOL_VERSION,
    SCHEDULING_METADATA_HEADER_NAME,
)
from buildgrid.server.sql.models import ClientIdentityEntry

ctx_request_metadata: ContextVar[RequestMetadata] = ContextVar(
    "ctx_request_metadata",
    default=RequestMetadata(
        tool_details=ToolDetails(
            tool_name=REQUEST_METADATA_TOOL_NAME,
            tool_version=REQUEST_METADATA_TOOL_VERSION,
        ),
    ),
)


def metadata_list() -> tuple[tuple[str, str | bytes], ...]:
    """Helper function to construct the metadata list from the ContextVar."""
    metadata = ctx_request_metadata.get()
    return ((REQUEST_METADATA_HEADER_NAME, metadata.SerializeToString()),)


ctx_grpc_request_id: ContextVar[str | None] = ContextVar("grpc_request_id", default=None)


def printable_request_metadata(metadata_entries: Any) -> str:
    """Given a metadata object, return a human-readable representation
    of its `RequestMetadata` entry.

    Args:
        metadata_entries: tuple of entries obtained from a gRPC context
            with, for example, `context.invocation_metadata()`.

    Returns:
        A string with the metadata contents.
    """
    metadata = extract_request_metadata(metadata_entries)
    return request_metadata_to_string(metadata)


def extract_request_metadata_dict(metadata_entries: Any) -> dict[str, str]:
    metadata = extract_request_metadata(metadata_entries)
    return request_metadata_to_dict(metadata)


def extract_request_metadata(metadata_entries: Any) -> RequestMetadata:
    """Given a list of string tuples, extract the RequestMetadata
    header values if they are present. If they were not provided,
    returns an empty message.

    Args:
        metadata_entries: tuple of entries obtained from a gRPC context
            with, for example, `context.invocation_metadata()`.

    Returns:
        A `RequestMetadata` proto. If the metadata is not defined in the
        request, the message will be empty.
    """
    request_metadata_entry = next(
        (entry for entry in metadata_entries if entry[0] == REQUEST_METADATA_HEADER_NAME), None
    )

    request_metadata = RequestMetadata()
    if request_metadata_entry:
        request_metadata.ParseFromString(request_metadata_entry[1])
    return request_metadata


def request_metadata_to_string(request_metadata: RequestMetadata) -> str:
    if request_metadata.tool_details:
        tool_name = request_metadata.tool_details.tool_name
        tool_version = request_metadata.tool_details.tool_version
    else:
        tool_name = tool_version = ""

    return (
        f'tool_name="{tool_name}", tool_version="{tool_version}", '
        f'action_id="{request_metadata.action_id}", '
        f'tool_invocation_id="{request_metadata.tool_invocation_id}", '
        f'correlated_invocations_id="{request_metadata.correlated_invocations_id}", '
        f'action_mnemonic="{request_metadata.action_mnemonic}", '
        f'target_id="{request_metadata.target_id}", '
        f'configuration_id="{request_metadata.configuration_id}"'
    )


def request_metadata_to_dict(request_metadata: RequestMetadata) -> dict[str, str]:
    if request_metadata.tool_details:
        tool_name = request_metadata.tool_details.tool_name
        tool_version = request_metadata.tool_details.tool_version
    else:
        tool_name = tool_version = ""

    return {
        "tool_name": tool_name,
        "tool_version": tool_version,
        "action_id": request_metadata.action_id,
        "tool_invocation_id": request_metadata.tool_invocation_id,
        "correlated_invocations_id": request_metadata.correlated_invocations_id,
        "action_mnemonic": request_metadata.action_mnemonic,
        "target_id": request_metadata.target_id,
        "configuration_id": request_metadata.configuration_id,
    }


def extract_scheduling_metadata(metadata_entries: Iterable[tuple[str, Any]]) -> SchedulingMetadata:
    """Given a list of string tuples, extract the SchedulingMetadata
    header values if they are present. If they were not provided,
    returns an empty message.

    Args:
        metadata_entries: tuple of entries obtained from a gRPC context
            with, for example, `context.invocation_metadata()`.

    Returns:
        A `SchedulingMetadata` proto. If the metadata is not defined in the
        request, the message will be empty.
    """
    scheduling_metadata_entry = next(
        (entry for entry in metadata_entries if entry[0] == SCHEDULING_METADATA_HEADER_NAME), None
    )

    scheduling_metadata = SchedulingMetadata()
    if scheduling_metadata_entry:
        try:
            scheduling_metadata.ParseFromString(scheduling_metadata_entry[1])
        except Exception:
            pass
    return scheduling_metadata


def extract_client_identity_dict(instance: str, invocation_metadata: Iterable[tuple[str, Any]]) -> dict[str, Any]:
    client_id = extract_client_identity(instance, invocation_metadata)
    return {
        "client_id": client_id.id if client_id else "",
        "instance": client_id.instance if client_id else instance,
        "workflow": client_id.workflow if client_id else "",
        "actor": client_id.actor if client_id else "",
        "subject": client_id.subject if client_id else "",
    }


def extract_client_identity(
    instance: str, invocation_metadata: Iterable[tuple[str, Any]]
) -> ClientIdentityEntry | None:
    """Checks for the existence of the client identity in the ClientIdentity
    context var. If the context var is not set then extracts
    the ClientIdentity from gRPC metadata

    Args:
        instance (str): the instance where the request was invoked from
        invocation_metadata (list[tuple[str, str]]): grpc metadata

    Returns:
        ClientIdentityEntry | None: identity of the client if exists
    """
    context_client_identity = get_context_client_identity()
    if (
        context_client_identity
        and context_client_identity.actor
        and context_client_identity.subject
        and context_client_identity.workflow
    ):
        return ClientIdentityEntry(
            instance=instance,
            workflow=context_client_identity.workflow,
            actor=context_client_identity.actor,
            subject=context_client_identity.subject,
        )

    metadata_dict = dict(invocation_metadata)
    workflow = metadata_dict.get("x-request-workflow", None)
    actor = metadata_dict.get("x-request-actor", None)
    subject = metadata_dict.get("x-request-subject", None)

    # None or empty strings are invalid
    if workflow and actor and subject:
        return ClientIdentityEntry(instance=instance, workflow=workflow, actor=actor, subject=subject)

    return None


def printable_client_identity(instance: str, invocation_metadata: Iterable[tuple[str, Any]]) -> str:
    """Given a metadata object, return a human-readable representation
    of its `ClientIdentity` entry.

    Args:
        instance: REAPI instance name
        invocation_metadata: tuple of entries obtained from a gRPC context
            with, for example, `context.invocation_metadata()`.

    Returns:
        A string with the ClientIdentity contents.
    """
    client_id = extract_client_identity(instance, invocation_metadata)
    return str(client_id)


def extract_trailing_client_identity(metadata_entries: Metadata) -> ClientIdentity:
    """Given a list of string tuples, extract the ClientIdentity
    header values if they are present. If they were not provided,
    returns an empty message.

    Args:
        metadata_entries: Sequence of gRPC trailing metadata headers.

    Returns:
        A `ClientIdentity` proto. If the metadata is not defined in the
        request, the message will be empty.
    """
    client_identity_entry = next(
        (entry for entry in metadata_entries if entry[0] == CLIENT_IDENTITY_HEADER_NAME), None
    )

    client_identity = ClientIdentity()
    if client_identity_entry:
        client_identity.ParseFromString(cast(bytes, client_identity_entry[1]))
    return client_identity
