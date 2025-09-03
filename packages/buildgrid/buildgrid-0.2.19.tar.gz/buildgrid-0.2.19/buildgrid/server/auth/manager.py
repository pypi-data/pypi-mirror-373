# Copyright (C) 2023 Bloomberg LP
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


from abc import ABC, abstractmethod
from contextvars import ContextVar
from typing import Any, Mapping, Union, cast

import grpc
import jwt

from buildgrid._protos.build.buildgrid.identity_pb2 import ClientIdentity
from buildgrid.server.auth.config import InstanceAuthorizationConfig
from buildgrid.server.auth.enums import AuthMetadataAlgorithm
from buildgrid.server.auth.exceptions import (
    AuthError,
    ExpiredTokenError,
    InvalidAuthorizationHeaderError,
    InvalidTokenError,
    MissingTokenError,
    SigningKeyNotFoundError,
    UnboundedTokenError,
    UnexpectedTokenParsingError,
)
from buildgrid.server.exceptions import InvalidArgumentError
from buildgrid.server.logging import buildgrid_logger
from buildgrid.server.settings import AUTH_CACHE_SIZE

LOGGER = buildgrid_logger(__name__)


AlgorithmType = Union[
    type[jwt.algorithms.RSAAlgorithm], type[jwt.algorithms.ECAlgorithm], type[jwt.algorithms.HMACAlgorithm]
]

# Algorithm classes defined in: https://github.com/jpadilla/pyjwt/blob/master/jwt/algorithms.py
ALGORITHM_TO_PYJWT_CLASS: dict[str, AlgorithmType] = {
    "RSA": jwt.algorithms.RSAAlgorithm,
    "EC": jwt.algorithms.ECAlgorithm,
    "oct": jwt.algorithms.HMACAlgorithm,
}


def _log_and_raise(request_name: str, exception: AuthError) -> str:
    LOGGER.info("Authorization error. Rejecting.", tags=dict(request_name=request_name, reason=str(exception)))
    raise exception


def _check_acls(
    acls: Mapping[str, InstanceAuthorizationConfig] | None,
    instance_name: str,
    request_name: str,
    actor: str | None = None,
    subject: str | None = None,
    workflow: str | None = None,
) -> bool:
    # If no ACL config was provided at all, don't do any more validation
    if acls is None:
        return True

    instance_acl_config = acls.get(instance_name)
    # If there is an ACL, but no config for this instance, deny all
    if instance_acl_config is None:
        return False

    return instance_acl_config.is_authorized(request_name, actor, subject, workflow)


class JwtParser:
    def __init__(
        self,
        secret: str | None = None,
        algorithm: AuthMetadataAlgorithm = AuthMetadataAlgorithm.UNSPECIFIED,
        jwks_urls: list[str] | None = None,
        audiences: list[str] | None = None,
        jwks_fetch_minutes: int = 60,
    ) -> None:
        self._check_jwt_support(algorithm)

        self._algorithm = algorithm
        self._audiences = audiences

        if (secret is None and jwks_urls is None) or (secret is not None and jwks_urls is not None):
            raise TypeError("Exactly one of `secret` or `jwks_url` must be set")
        self._secret = secret
        self._jwks_clients = [
            jwt.PyJWKClient(url, lifespan=60 * jwks_fetch_minutes, max_cached_keys=AUTH_CACHE_SIZE)
            for url in (jwks_urls or [])
        ]

    def _check_jwt_support(self, algorithm: AuthMetadataAlgorithm) -> None:
        """Ensures JWT and possible dependencies are available."""
        if algorithm == AuthMetadataAlgorithm.UNSPECIFIED:
            raise InvalidArgumentError("JWT authorization method requires an algorithm to be specified")

    def parse(self, token: str) -> dict[str, Any]:
        payload: dict[str, Any] | None = None
        try:
            if self._secret is not None:
                payload = jwt.decode(
                    token,
                    self._secret,
                    algorithms=[self._algorithm.value.upper()],
                    audience=self._audiences,
                    options={"require": ["exp"], "verify_exp": True},
                )

            elif self._jwks_clients:
                # Find the signing_key in jkus
                signing_key: jwt.PyJWK | None = None
                errors: list[tuple[str, jwt.PyJWKClientError]] = []
                for jwks_client in self._jwks_clients:
                    try:
                        signing_key = jwks_client.get_signing_key_from_jwt(token)
                        break
                    except jwt.PyJWKClientError as e:
                        errors.append((jwks_client.uri, e))

                if signing_key is None:
                    error_msg = ", ".join(f"{uri}:{str(err)}" for uri, err in errors)
                    raise SigningKeyNotFoundError(error_msg)

                payload = jwt.decode(
                    token,
                    signing_key.key,
                    algorithms=[self._algorithm.value.upper()],
                    audience=self._audiences,
                    options={"require": ["exp"], "verify_exp": True},
                )

        except AuthError:
            raise

        except jwt.exceptions.ExpiredSignatureError as e:
            raise ExpiredTokenError() from e

        except jwt.exceptions.MissingRequiredClaimError as e:
            raise UnboundedTokenError("Missing required JWT claim, likely 'exp' was not set") from e

        except jwt.exceptions.InvalidTokenError as e:
            raise InvalidTokenError() from e

        except Exception as e:
            raise UnexpectedTokenParsingError() from e

        if payload is None:
            raise InvalidTokenError()

        return payload

    def identity_from_jwt_payload(self, payload: dict[str, Any]) -> ClientIdentity:
        """
        Extract the relevant claims from the JWT
            "aud" -> workflow
            "sub" -> subject
            "act" -> actor
        If the "act" field is not set then the subject is considered the actor
        The audience for the identity is taken from the config if set
        If "aud" field is an array of strings then the first element is set as the audience'
        Args:
            payload: the decoded payload from the jwt
        Returns:
            A dictionary containing workflow, actor, subject
        """

        workflow = ""
        if audience_from_payload := payload.get("aud"):
            if isinstance(audience_from_payload, str):
                workflow = audience_from_payload
            elif isinstance(audience_from_payload, list):
                workflow = audience_from_payload[0]
        elif self._audiences is not None and len(self._audiences) > 0:
            workflow = self._audiences[0]

        actor = payload.get("act")
        subject = payload.get("sub")

        if not actor:
            actor = subject
        return ClientIdentity(
            actor=actor if isinstance(actor, str) else "",
            subject=subject if isinstance(subject, str) else "",
            workflow=workflow if isinstance(workflow, str) else "",
        )

    def identity_from_token(self, token: str) -> ClientIdentity:
        payload = self.parse(token)
        return self.identity_from_jwt_payload(payload)


class AuthManager(ABC):
    @abstractmethod
    def authorize(self, context: grpc.ServicerContext, instance_name: str, request_name: str) -> bool:
        """Determine whether or not a request is authorized.

        This method takes a ``ServicerContext`` for an incoming gRPC request,
        along with the name of the request, and the name of the instance that
        the request is intended for. Information about the identity of the
        requester is extracted from the context, for example a JWT token.

        This identity information is compared to the ACL configuration given
        to this class at construction time to determine authorization for the
        request.

        Args:
            context (ServicerContext): The context for the gRPC request to check
                the authz status of.

            instance_name (str): The name of the instance that the gRPC request
                will be interacting with. This is used for per-instance ACLs.

            request_name (str): The name of the request being authorized, for
                example `Execute`.

        Returns:
            bool: Whether the request is authorized.

        """


class JWTAuthManager(AuthManager):
    def __init__(
        self,
        secret: str | None = None,
        algorithm: AuthMetadataAlgorithm = AuthMetadataAlgorithm.UNSPECIFIED,
        jwks_urls: list[str] | None = None,
        audiences: list[str] | None = None,
        jwks_fetch_minutes: int = 60,
        acls: Mapping[str, InstanceAuthorizationConfig] | None = None,
        allow_unauthenticated_instances: set[str] | None = None,
    ) -> None:
        """Initializes a new :class:`JWTAuthManager`.

        Args:
            secret (str): The secret or key to be used for validating request,
                depending on `method`. Defaults to ``None``.

            algorithm (AuthMetadataAlgorithm): The crytographic algorithm used
                to encode `secret`. Defaults to ``UNSPECIFIED``.

            jwks_urls (list[str]): The urls to fetch the JWKs. Either secret or
                this field must be specified if the authentication method is JWT.
                Defaults to ``None``.

            audiences (list[str]): The audience used to validate jwt tokens against.
                The tokens must have an audience field.

            jwks_fetch_minutes (int): The number of minutes to cache JWKs fetches
                for. Defaults to 60.

            acls (Mapping[str, InstanceAuthorizationConfig] | None): An optional
                map of instance name -> ACL config to use for per-instance
                authorization.

            allow_unauthenticated_instances(set[str] | None): List of instances that should
                be allowed to have unautheticated access

        Raises:
            InvalidArgumentError: If `algorithm` is not supported.

        """
        self._acls = acls
        self._allow_unauthenticated_instances = allow_unauthenticated_instances
        self._token_parser = JwtParser(secret, algorithm, jwks_urls, audiences, jwks_fetch_minutes)

    def _token_from_request_context(self, context: grpc.ServicerContext, request_name: str) -> str:
        try:
            bearer = cast(str, dict(context.invocation_metadata())["authorization"])

        except KeyError:
            # Reject requests not carrying a token
            _log_and_raise(request_name, MissingTokenError())

        # Reject requests with malformatted bearer
        if not bearer.startswith("Bearer "):
            _log_and_raise(request_name, InvalidAuthorizationHeaderError())

        return bearer[7:]

    def authorize(self, context: grpc.ServicerContext, instance_name: str, request_name: str) -> bool:
        # For instances with unauthenticated access, skip identity verification but still validate the
        # request against the ACLs.
        if self._allow_unauthenticated_instances and instance_name in self._allow_unauthenticated_instances:
            return _check_acls(self._acls, instance_name, request_name)
        try:
            token = self._token_from_request_context(context, request_name)
            identity_from_token = self._token_parser.identity_from_token(token)
            workflow = identity_from_token.workflow
            actor = identity_from_token.actor
            subject = identity_from_token.subject
            set_context_client_identity(identity_from_token)
        except NameError:
            LOGGER.error("JWT auth is enabled but PyJWT is not installed.")
            return False
        except AuthError as e:
            LOGGER.info(f"Error authorizing JWT token: {str(e)}")
            return False

        return _check_acls(self._acls, instance_name, request_name, actor=actor, subject=subject, workflow=workflow)


class HeadersAuthManager(AuthManager):
    def __init__(
        self,
        acls: Mapping[str, InstanceAuthorizationConfig] | None = None,
        allow_unauthenticated_instances: set[str] | None = None,
    ) -> None:
        """Initializes a new :class:`HeadersAuthManager`.

        Args:
            acls (Mapping[str, InstanceAuthorizationConfig] | None): An optional
                map of instance name -> ACL config to use for per-instance
                authorization.

            allow_unauthenticated_instances(set[str] | None): List of instances that should
                be allowed to have unautheticated access

        """
        self._acls = acls
        self._allow_unauthenticated_instances = allow_unauthenticated_instances

    def authorize(self, context: grpc.ServicerContext, instance_name: str, request_name: str) -> bool:
        # For instances with unauthenticated access, skip identity verification but still validate the
        # request against the ACLs.
        if self._allow_unauthenticated_instances and instance_name in self._allow_unauthenticated_instances:
            return _check_acls(self._acls, instance_name, request_name)
        metadata_dict = dict(context.invocation_metadata())
        actor = str(metadata_dict.get("x-request-actor"))
        subject = str(metadata_dict.get("x-request-subject"))
        workflow = str(metadata_dict.get("x-request-workflow"))
        set_context_client_identity(ClientIdentity(actor=actor, subject=subject, workflow=workflow))
        return _check_acls(self._acls, instance_name, request_name, actor=actor, subject=subject, workflow=workflow)


# TODO: Once https://github.com/grpc/grpc/issues/33071 is resolved this AuthContext can be
# replaced with a gRPC interceptor stores the AuthManager in a request-local ContextVar.
AuthContext: "ContextVar[AuthManager | None]" = ContextVar("AuthManager", default=None)


def set_auth_manager(manager: AuthManager | None) -> None:
    AuthContext.set(manager)


def get_auth_manager() -> AuthManager | None:
    return AuthContext.get()


def authorize_request(request_context: grpc.ServicerContext, instance_name: str, request_name: str) -> None:
    manager = get_auth_manager()

    # If no auth is configured, don't do authz
    if manager is None:
        return

    if manager.authorize(request_context, instance_name, request_name):
        return

    LOGGER.info(
        "Authentication failed for request.", tags=dict(request_name=request_name, peer=request_context.peer())
    )
    # No need to yield here since calling `abort` raises an Exception
    request_context.abort(grpc.StatusCode.UNAUTHENTICATED, "No valid authorization or authentication provided")


ContextClientIdentity: "ContextVar[ClientIdentity | None]" = ContextVar("ClientIdentity", default=None)


def set_context_client_identity(clientIdentity: ClientIdentity) -> None:
    ContextClientIdentity.set(clientIdentity)


def get_context_client_identity() -> ClientIdentity | None:
    return ContextClientIdentity.get()
