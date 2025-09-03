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


"""
Execution Controller
====================

An instance of the Execution controller.

All this stuff you need to make the execution service work.

Contains scheduler, execution instance, an interface to the bots
and an operations instance.
"""
from typing import Iterable

from buildgrid.server.bots.instance import BotsInterface
from buildgrid.server.enums import ServiceName
from buildgrid.server.execution.instance import ExecutionInstance
from buildgrid.server.operations.instance import OperationsInstance
from buildgrid.server.scheduler import Scheduler
from buildgrid.server.settings import DEFAULT_MAX_LIST_OPERATION_PAGE_SIZE


class ExecutionController:
    def __init__(
        self,
        scheduler: Scheduler,
        *,
        operation_stream_keepalive_timeout: int | None = None,
        services: Iterable[str] = ServiceName.default_services(),
        max_list_operations_page_size: int = DEFAULT_MAX_LIST_OPERATION_PAGE_SIZE,
    ) -> None:
        self.execution_instance: ExecutionInstance | None = None
        if ServiceName.EXECUTION.value in services:
            self.execution_instance = ExecutionInstance(scheduler, operation_stream_keepalive_timeout)

        self.operations_instance: OperationsInstance | None = None
        if ServiceName.OPERATIONS.value in services:
            self.operations_instance = OperationsInstance(scheduler, max_list_operations_page_size)

        self.bots_interface: BotsInterface | None = None
        if ServiceName.BOTS.value in services:
            self.bots_interface = BotsInterface(scheduler)
