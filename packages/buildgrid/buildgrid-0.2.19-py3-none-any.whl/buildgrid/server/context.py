# Copyright (C) 2024 Bloomberg LP
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

from contextlib import contextmanager
from contextvars import ContextVar
from typing import Iterator

from buildgrid.server.exceptions import InvalidArgumentError

_instance_name: "ContextVar[str | None]" = ContextVar("_instance_name", default=None)
_service_name: "ContextVar[str | None]" = ContextVar("_service_name", default=None)
_method_name: "ContextVar[str | None]" = ContextVar("_method_name", default=None)


@contextmanager
def instance_context(instance_name: str | None) -> Iterator[None]:
    token = _instance_name.set(instance_name)
    try:
        yield
    finally:
        _instance_name.reset(token)


def try_current_instance() -> str | None:
    return _instance_name.get()


def current_instance() -> str:
    instance_name = try_current_instance()
    if instance_name is None:
        raise InvalidArgumentError("Instance name not set")
    return instance_name


@contextmanager
def service_context(service_name: str | None) -> Iterator[None]:
    token = _service_name.set(service_name)
    try:
        yield
    finally:
        _service_name.reset(token)


def try_current_service() -> str | None:
    return _service_name.get()


def current_service() -> str:
    service_name = try_current_service()
    if service_name is None:
        raise InvalidArgumentError("Service name not set")
    return service_name


@contextmanager
def method_context(method_name: str | None) -> Iterator[None]:
    token = _method_name.set(method_name)
    try:
        yield
    finally:
        _method_name.reset(token)


def try_current_method() -> str | None:
    return _method_name.get()


def current_method() -> str:
    method_name = try_current_method()
    if method_name is None:
        raise InvalidArgumentError("Method name not set")
    return method_name
