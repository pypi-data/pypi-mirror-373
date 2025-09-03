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


import base64
import os
from collections import namedtuple
from typing import Any, TypedDict

import grpc

from buildgrid.server.client.auth_token_loader import AuthTokenLoader
from buildgrid.server.exceptions import InvalidArgumentError

ClientCredentials = TypedDict(
    "ClientCredentials",
    {
        "auth-token": str,
        "tls-client-key": str,
        "tls-client-cert": str,
        "tls-server-cert": str,
        "token-refresh-seconds": int,
    },
    total=False,
)


def load_tls_channel_credentials(
    client_key: str | None = None, client_cert: str | None = None, server_cert: str | None = None
) -> tuple[grpc.ChannelCredentials, tuple[str | None, str | None, str | None]]:
    """Looks-up and loads TLS gRPC client channel credentials.

    Args:
        client_key(str, optional): Client certificate chain file path.
        client_cert(str, optional): Client private key file path.
        server_cert(str, optional): Serve root certificate file path.

    Returns:
        ChannelCredentials: Credentials to be used for a TLS-encrypted gRPC
            client channel.
    """
    if server_cert and os.path.exists(server_cert):
        with open(server_cert, "rb") as f:
            server_cert_pem = f.read()
    else:
        server_cert_pem = None
        server_cert = None

    if client_key and os.path.exists(client_key):
        with open(client_key, "rb") as f:
            client_key_pem = f.read()
    else:
        client_key_pem = None
        client_key = None

    if client_key_pem and client_cert and os.path.exists(client_cert):
        with open(client_cert, "rb") as f:
            client_cert_pem = f.read()
    else:
        client_cert_pem = None
        client_cert = None

    credentials = grpc.ssl_channel_credentials(
        root_certificates=server_cert_pem, private_key=client_key_pem, certificate_chain=client_cert_pem
    )

    return credentials, (
        client_key,
        client_cert,
        server_cert,
    )


class AuthMetadataClientInterceptorBase:
    def __init__(
        self,
        auth_token_loader: AuthTokenLoader | None = None,
        auth_secret: bytes | None = None,
    ) -> None:
        """Initialises a new :class:`AuthMetadataClientInterceptorBase`.

        Important:
            One of `auth_token_path` or `auth_secret` must be provided.

        Args:
            auth_token_loader (AuthTokenLoader, optional): Auth token loader than fetches and passes the token
            auth_secret (bytes, optional): Authorization secret as bytes.

        Raises:
            InvalidArgumentError: If neither `auth_token_loader` or `auth_secret` are
                provided.
        """
        self._auth_token_loader: AuthTokenLoader | None = None
        self.__secret: str | None = None

        if auth_token_loader:
            self._auth_token_loader = auth_token_loader

        elif auth_secret:
            self.__secret = base64.b64encode(auth_secret.strip()).decode()

        else:
            raise InvalidArgumentError("A secret or token must be provided")

        self.__header_field_name = "authorization"

    def _get_secret(self) -> str:
        if self._auth_token_loader:
            token = self._auth_token_loader.get_token()
        else:
            assert self.__secret is not None
            token = self.__secret
        return f"Bearer {token}"

    def amend_call_details(  # type: ignore[no-untyped-def] # wait for client lib updates here
        self, client_call_details, grpc_call_details_class: Any
    ):
        """Appends an authorization field to given client call details."""
        if client_call_details.metadata is not None:
            new_metadata = list(client_call_details.metadata)
        else:
            new_metadata = []

        new_metadata.append(
            (
                self.__header_field_name,
                self._get_secret(),
            )
        )

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
