# Copyright (C) 2021 Bloomberg LP
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  <http://www.apache.org/licenses/LICENSE-2.0>
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License' is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from typing import Any, Protocol, TypeVar

GrpcTrailingMetadata = tuple[tuple[str, str | bytes], ...]
LogStreamConnectionConfig = dict[str, str | dict[str, str]]


class OnServerStartCallback(Protocol):
    def __call__(self) -> Any: ...


class PortAssignedCallback(Protocol):
    def __call__(self, port_map: dict[Any, int]) -> Any: ...


Cls = TypeVar("Cls")


class MessageType(Protocol):
    # Acts like a protobuf message. Add methods as needed.

    @classmethod
    def FromString(cls: type[Cls], s: bytes) -> Cls:
        pass

    def SerializeToString(self: Any, *, deterministic: bool = ...) -> bytes:
        pass

    def ParseFromString(self, serialized: bytes) -> int:
        pass

    def Clear(self) -> None:
        pass
