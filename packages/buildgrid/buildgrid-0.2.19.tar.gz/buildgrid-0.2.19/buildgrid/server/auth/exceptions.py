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

from buildgrid.server.exceptions import ServerError


class AuthError(ServerError):
    pass


class MissingTokenError(AuthError):
    def __init__(self) -> None:
        super().__init__("Missing authentication header field")


class InvalidAuthorizationHeaderError(AuthError):
    def __init__(self) -> None:
        super().__init__("Invalid authentication header field")


class InvalidTokenError(AuthError):
    def __init__(self) -> None:
        super().__init__("Invalid authentication token")


class SigningKeyNotFoundError(AuthError):
    def __init__(self, message: str) -> None:
        super().__init__(f"Cannot find signing key for token: {message}")


class ExpiredTokenError(AuthError):
    def __init__(self) -> None:
        super().__init__("Expired authentication token")


class UnboundedTokenError(AuthError):
    def __init__(self, context: str = "") -> None:
        message = "Unbounded authentication token"
        if context:
            message = f"{message}: {context}"
        super().__init__(message)


class UnexpectedTokenParsingError(AuthError):
    def __init__(self) -> None:
        super().__init__("Unexpected error parsing authentication token")
