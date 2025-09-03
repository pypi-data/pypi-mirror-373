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

from collections import namedtuple
from typing import TYPE_CHECKING, Any
from urllib.parse import urlparse

import grpc
from grpc import aio

from buildgrid._protos.build.bazel.remote.execution.v2 import remote_execution_pb2
from buildgrid.server.client.auth_token_loader import AuthTokenLoader
from buildgrid.server.client.authentication import AuthMetadataClientInterceptorBase, load_tls_channel_credentials
from buildgrid.server.client.interceptors import (
    AsyncStreamStreamInterceptor,
    AsyncStreamUnaryInterceptor,
    AsyncUnaryStreamInterceptor,
    AsyncUnaryUnaryInterceptor,
    SyncStreamStreamInterceptor,
    SyncStreamUnaryInterceptor,
    SyncUnaryStreamInterceptor,
    SyncUnaryUnaryInterceptor,
)
from buildgrid.server.exceptions import InvalidArgumentError
from buildgrid.server.settings import (
    INSECURE_URI_SCHEMES,
    REQUEST_METADATA_HEADER_NAME,
    REQUEST_METADATA_TOOL_NAME,
    REQUEST_METADATA_TOOL_VERSION,
    SECURE_URI_SCHEMES,
)


def setup_channel(
    remote_url: str,
    auth_token: str | None = None,
    auth_token_refresh_seconds: int | None = None,
    client_key: str | None = None,
    client_cert: str | None = None,
    server_cert: str | None = None,
    action_id: str | None = None,
    tool_invocation_id: str | None = None,
    correlated_invocations_id: str | None = None,
    asynchronous: bool = False,
    timeout: float | None = None,
) -> tuple[grpc.Channel, tuple[str | None, ...]]:
    """Creates a new gRPC client communication chanel.

    If `remote_url` does not point to a socket and does not specify a
    port number, defaults 50051.

    Args:
        remote_url (str): URL for the remote, including protocol and,
            if not a Unix domain socket, a port.
        auth_token (str): Authorization token file path.
        auth_token_refresh_seconds(int): Time in seconds to read the authorization token again from file
        server_cert(str): TLS certificate chain file path.
        client_key (str): TLS root certificate file path.
        client_cert (str): TLS private key file path.
        action_id (str): Action identifier to which the request belongs to.
        tool_invocation_id (str): Identifier for a related group of Actions.
        correlated_invocations_id (str): Identifier that ties invocations together.
        timeout (float): Request timeout in seconds.

    Returns:
        Channel: Client Channel to be used in order to access the server
            at `remote_url`.

    Raises:
        InvalidArgumentError: On any input parsing error.
    """
    url = urlparse(remote_url)

    url_is_socket = url.scheme == "unix"
    if url_is_socket:
        remote = remote_url
    else:
        remote = f"{url.hostname}:{url.port or 50051}"

    details: tuple[str | None, str | None, str | None] = None, None, None
    credentials_provided = any((server_cert, client_cert, client_key))
    auth_token_loader: AuthTokenLoader | None = None
    if auth_token:
        auth_token_loader = AuthTokenLoader(auth_token, auth_token_refresh_seconds)

    if asynchronous:
        async_interceptors = _create_async_interceptors(
            auth_token_loader=auth_token_loader,
            action_id=action_id,
            tool_invocation_id=tool_invocation_id,
            correlated_invocations_id=correlated_invocations_id,
            timeout=timeout,
        )

        if url.scheme in INSECURE_URI_SCHEMES or (url_is_socket and not credentials_provided):
            async_channel = aio.insecure_channel(remote, interceptors=async_interceptors)
        elif url.scheme in SECURE_URI_SCHEMES or (url_is_socket and credentials_provided):
            credentials, details = load_tls_channel_credentials(client_key, client_cert, server_cert)
            if not credentials:
                raise InvalidArgumentError("Given TLS details (or defaults) could be loaded")
            async_channel = aio.secure_channel(remote, credentials, interceptors=async_interceptors)
        else:
            raise InvalidArgumentError("Given remote does not specify a protocol")

        # TODO use overloads to make this return an async channel when asynchronous == True
        return async_channel, details  # type: ignore[return-value]

    else:
        sync_interceptors = _create_sync_interceptors(
            auth_token_loader=auth_token_loader,
            action_id=action_id,
            tool_invocation_id=tool_invocation_id,
            correlated_invocations_id=correlated_invocations_id,
            timeout=timeout,
        )

        if url.scheme in INSECURE_URI_SCHEMES or (url_is_socket and not credentials_provided):
            sync_channel = grpc.insecure_channel(remote)
        elif url.scheme in SECURE_URI_SCHEMES or (url_is_socket and credentials_provided):
            credentials, details = load_tls_channel_credentials(client_key, client_cert, server_cert)
            if not credentials:
                raise InvalidArgumentError("Given TLS details (or defaults) could be loaded")
            sync_channel = grpc.secure_channel(remote, credentials)
        else:
            raise InvalidArgumentError("Given remote does not specify a protocol")

        for interceptor in sync_interceptors:
            sync_channel = grpc.intercept_channel(sync_channel, interceptor)

        return sync_channel, details


class RequestMetadataInterceptorBase:
    def __init__(
        self,
        action_id: str | None = None,
        tool_invocation_id: str | None = None,
        correlated_invocations_id: str | None = None,
    ) -> None:
        """Appends optional `RequestMetadata` header values to each call.

        Args:
            action_id (str): Action identifier to which the request belongs to.
            tool_invocation_id (str): Identifier for a related group of Actions.
            correlated_invocations_id (str): Identifier that ties invocations together.
        """
        self._action_id = action_id
        self._tool_invocation_id = tool_invocation_id
        self._correlated_invocations_id = correlated_invocations_id

        self.__header_field_name = REQUEST_METADATA_HEADER_NAME
        self.__header_field_value = self._request_metadata()

    def _request_metadata(self) -> bytes:
        """Creates a serialized RequestMetadata entry to attach to a gRPC
        call header. Arguments should be of type str or None.
        """
        request_metadata = remote_execution_pb2.RequestMetadata()
        request_metadata.tool_details.tool_name = REQUEST_METADATA_TOOL_NAME
        request_metadata.tool_details.tool_version = REQUEST_METADATA_TOOL_VERSION

        if self._action_id:
            request_metadata.action_id = self._action_id
        if self._tool_invocation_id:
            request_metadata.tool_invocation_id = self._tool_invocation_id
        if self._correlated_invocations_id:
            request_metadata.correlated_invocations_id = self._correlated_invocations_id

        return request_metadata.SerializeToString()

    def amend_call_details(  # type: ignore[no-untyped-def] # wait for client lib updates here
        self, client_call_details, grpc_call_details_class: Any
    ):
        if client_call_details.metadata is not None:
            new_metadata = list(client_call_details.metadata)
        else:
            new_metadata = []

        new_metadata.append((self.__header_field_name, self.__header_field_value))

        class _ClientCallDetails(
            namedtuple(
                "_ClientCallDetails",
                (
                    "method",
                    "timeout",
                    "credentials",
                    "metadata",
                    "wait_for_ready",
                ),
            ),
            grpc_call_details_class,  # type: ignore
        ):
            pass

        return _ClientCallDetails(
            client_call_details.method,
            client_call_details.timeout,
            client_call_details.credentials,
            new_metadata,
            client_call_details.wait_for_ready,
        )


class TimeoutInterceptorBase:
    def __init__(self, timeout: float) -> None:
        """Applies a request timeout to each call.

        Args:
            timeout (float): Request timeout in seconds.
        """
        self._timeout = timeout

    def amend_call_details(  # type: ignore[no-untyped-def] # wait for client lib updates here
        self, client_call_details, grpc_call_details_class: Any
    ):
        # If there are multiple timeouts, apply the shorter timeout (earliest deadline wins)
        if client_call_details.timeout is not None:
            new_timeout = min(self._timeout, client_call_details.timeout)
        else:
            new_timeout = self._timeout

        class _ClientCallDetails(
            namedtuple(
                "_ClientCallDetails",
                (
                    "method",
                    "timeout",
                    "credentials",
                    "metadata",
                    "wait_for_ready",
                ),
            ),
            grpc_call_details_class,  # type: ignore
        ):
            pass

        return _ClientCallDetails(
            client_call_details.method,
            new_timeout,
            client_call_details.credentials,
            client_call_details.metadata,
            client_call_details.wait_for_ready,
        )


if TYPE_CHECKING:
    SyncInterceptorsList = list[
        grpc.UnaryUnaryClientInterceptor[Any, Any]
        | grpc.UnaryStreamClientInterceptor[Any, Any]
        | grpc.StreamUnaryClientInterceptor[Any, Any]
        | grpc.StreamStreamClientInterceptor[Any, Any]
    ]


def _create_sync_interceptors(
    auth_token_loader: AuthTokenLoader | None = None,
    action_id: str | None = None,
    tool_invocation_id: str | None = None,
    correlated_invocations_id: str | None = None,
    timeout: float | None = None,
) -> "SyncInterceptorsList":
    interceptors: "SyncInterceptorsList" = []

    request_metadata_interceptor = RequestMetadataInterceptorBase(
        action_id=action_id,
        tool_invocation_id=tool_invocation_id,
        correlated_invocations_id=correlated_invocations_id,
    )

    interceptors += [
        SyncUnaryUnaryInterceptor(request_metadata_interceptor),
        SyncUnaryStreamInterceptor(request_metadata_interceptor),
        SyncStreamUnaryInterceptor(request_metadata_interceptor),
        SyncStreamStreamInterceptor(request_metadata_interceptor),
    ]

    if auth_token_loader is not None:
        auth_metadata_client_interceptor = AuthMetadataClientInterceptorBase(auth_token_loader=auth_token_loader)
        interceptors += [
            SyncUnaryUnaryInterceptor(auth_metadata_client_interceptor),
            SyncUnaryStreamInterceptor(auth_metadata_client_interceptor),
            SyncStreamUnaryInterceptor(auth_metadata_client_interceptor),
            SyncStreamStreamInterceptor(auth_metadata_client_interceptor),
        ]

    if timeout is not None:
        timeout_interceptor_base = TimeoutInterceptorBase(timeout)
        interceptors += [
            SyncUnaryUnaryInterceptor(timeout_interceptor_base),
            SyncUnaryStreamInterceptor(timeout_interceptor_base),
            SyncStreamUnaryInterceptor(timeout_interceptor_base),
            SyncStreamStreamInterceptor(timeout_interceptor_base),
        ]

    return interceptors


def _create_async_interceptors(
    auth_token_loader: AuthTokenLoader | None = None,
    action_id: str | None = None,
    tool_invocation_id: str | None = None,
    correlated_invocations_id: str | None = None,
    timeout: float | None = None,
) -> list[aio.ClientInterceptor]:
    # FIXME Types not happy...  "list" has incompatible type "..."; expected "_PartialStubMustCastOrIgnore"
    interceptors: list[Any] = []

    request_metadata_interceptor = RequestMetadataInterceptorBase(
        action_id=action_id,
        tool_invocation_id=tool_invocation_id,
        correlated_invocations_id=correlated_invocations_id,
    )

    interceptors += [
        AsyncUnaryUnaryInterceptor(request_metadata_interceptor),
        AsyncUnaryStreamInterceptor(request_metadata_interceptor),
        AsyncStreamUnaryInterceptor(request_metadata_interceptor),
        AsyncStreamStreamInterceptor(request_metadata_interceptor),
    ]

    if auth_token_loader is not None:
        auth_metadata_client_interceptor = AuthMetadataClientInterceptorBase(auth_token_loader=auth_token_loader)
        interceptors += [
            AsyncUnaryUnaryInterceptor(auth_metadata_client_interceptor),
            AsyncUnaryStreamInterceptor(auth_metadata_client_interceptor),
            AsyncStreamUnaryInterceptor(auth_metadata_client_interceptor),
            AsyncStreamStreamInterceptor(auth_metadata_client_interceptor),
        ]

    if timeout is not None:
        timeout_interceptor_base = TimeoutInterceptorBase(timeout)
        interceptors += [
            AsyncUnaryUnaryInterceptor(timeout_interceptor_base),
            AsyncUnaryStreamInterceptor(timeout_interceptor_base),
            AsyncStreamUnaryInterceptor(timeout_interceptor_base),
            AsyncStreamStreamInterceptor(timeout_interceptor_base),
        ]

    return interceptors
