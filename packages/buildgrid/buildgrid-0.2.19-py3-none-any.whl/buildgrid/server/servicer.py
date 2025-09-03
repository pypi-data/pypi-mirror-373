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

from abc import ABC
from contextlib import ExitStack
from typing import Any, Callable, ClassVar, Generic, TypeVar, cast

import grpc

from buildgrid.server.context import current_instance
from buildgrid.server.exceptions import InvalidArgumentError

_Instance = TypeVar("_Instance", bound="Instance")


class Instance(ABC):
    """
    An Instance is the underlying implementation of a given Servicer.
    """

    SERVICE_NAME: ClassVar[str]
    """
    The expected FULL_NAME of the Service which will wrap this instance.
    This value should be declared on the class of any Instance implementations.
    """

    def __enter__(self: _Instance) -> _Instance:
        self.start()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.stop()

    def start(self) -> None:
        """
        A method called when the grpc service is starting.

        This method may be overriden if startup logic is required.
        """

    def stop(self) -> None:
        """
        A method called when the grpc service is shutting down.

        This method may be overriden if shutdown logic is required.
        """


_InstancedServicer = TypeVar("_InstancedServicer", bound="InstancedServicer[Any]")


class InstancedServicer(ABC, Generic[_Instance]):
    REGISTER_METHOD: ClassVar[Callable[[Any, grpc.Server], None]]
    """
    The method to be invoked when attaching the service to a grpc.Server instance.
    This value should be declared on the class of any Servicer implementations.
    """

    FULL_NAME: ClassVar[str]
    """
    The full name of the servicer, used to match instances to the servicer and configure reflection.
    This value should be declared on the class of any Servicer implementations.
    """

    def __init__(self) -> None:
        """
        The InstancedServicer base class allows easily creating implementations for services
        which require delegating logic to distinct instance implementations.

        The base class provides logic for registering new instances with the service.
        """

        self._stack = ExitStack()
        self.instances: dict[str, _Instance] = {}

    def setup_grpc(self, server: grpc.Server) -> None:
        """
        A method called when the Service is being attached to a grpc server.
        """

        if self.enabled:
            self.REGISTER_METHOD(server)

    def __enter__(self: _InstancedServicer) -> _InstancedServicer:
        self.start()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.stop()

    def start(self) -> None:
        for instance in self.instances.values():
            self._stack.enter_context(instance)

    def stop(self) -> None:
        self._stack.close()

    @property
    def enabled(self) -> bool:
        """
        By default, a servicer is disabled if there are no registered instances.
        If a servicer is not enabled, it will not be attached to the grpc.Server instance.

        This property may be overriden if servicer enablement follows other rules.
        """

        return len(self.instances) > 0

    def add_instance(self, name: str, instance: _Instance) -> None:
        """
        Adds an instance to the servicer.

        This method may be overriden if adding an instance requires additional setup.

        Args:
            name (str): The name of the instance.

            instance (_Instance): The instance implementation.
        """

        self.instances[name] = instance

    @property
    def current_instance(self) -> _Instance:
        return self.get_instance(current_instance())

    def get_instance(self, instance_name: str) -> _Instance:
        """
        Provides a wrapper to access the instance, throwing a InvalidArgumentError
        if the instance requested does not exist.

        This method may be overriden if you wish to create a custom error message.

        Args:
            instance_name (str): The name of the instance.

        Returns:
            _Instance: The requested instance.
        """

        try:
            return self.instances[instance_name]
        except KeyError:
            raise InvalidArgumentError(f"Invalid instance name: [{instance_name}]")

    def cast(self, instance: Instance) -> _Instance | None:
        """
        A helper tool used by the BuildGrid Server startup logic to determine the correct
        servicer to attach an instance to. This method will also cast the instance to the
        correct type required by the servicer implementation.

        Args:
            instance (Instance): The instance to check.

        Returns:
            _Instance | None: The validated instance or None if invalid.
        """

        if instance.SERVICE_NAME == self.FULL_NAME:
            return cast(_Instance, instance)
        return None
