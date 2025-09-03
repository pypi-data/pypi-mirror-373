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
OperationsInstance
==================
An instance of the LongRunningOperations Service.
"""

from buildgrid._protos.build.bazel.remote.execution.v2.remote_execution_pb2 import RequestMetadata
from buildgrid._protos.build.buildgrid.identity_pb2 import ClientIdentity
from buildgrid._protos.google.longrunning.operations_pb2 import DESCRIPTOR as OPS_DESCRIPTOR
from buildgrid._protos.google.longrunning.operations_pb2 import ListOperationsResponse, Operation
from buildgrid.server.exceptions import InvalidArgumentError, NotFoundError
from buildgrid.server.logging import buildgrid_logger
from buildgrid.server.operations.filtering import DEFAULT_OPERATION_FILTERS, FilterParser
from buildgrid.server.scheduler import Scheduler
from buildgrid.server.servicer import Instance
from buildgrid.server.settings import DEFAULT_MAX_LIST_OPERATION_PAGE_SIZE

LOGGER = buildgrid_logger(__name__)


class OperationsInstance(Instance):
    SERVICE_NAME = OPS_DESCRIPTOR.services_by_name["Operations"].full_name

    def __init__(
        self, scheduler: Scheduler, max_list_operations_page_size: int = DEFAULT_MAX_LIST_OPERATION_PAGE_SIZE
    ) -> None:
        self.scheduler = scheduler
        self._max_list_operations_page_size = max_list_operations_page_size

    # --- Public API ---

    def start(self) -> None:
        self.scheduler.start()

    def stop(self) -> None:
        self.scheduler.stop()
        LOGGER.info("Stopped Operations.")

    def get_operation(self, operation_name: str) -> tuple[Operation, RequestMetadata | None, ClientIdentity | None]:
        operation = self.scheduler.load_operation(operation_name)
        metadata = self.scheduler.get_operation_request_metadata_by_name(operation_name)
        client_identity = self.scheduler.get_client_identity_by_operation(operation_name)
        return operation, metadata, client_identity

    def list_operations(
        self, filter_string: str, page_size: int | None, page_token: str | None
    ) -> ListOperationsResponse:
        if page_size and page_size > self._max_list_operations_page_size:
            raise InvalidArgumentError(f"The maximum page size is {self._max_list_operations_page_size}.")
        if not page_size:
            page_size = self._max_list_operations_page_size

        operation_filters = FilterParser.parse_listoperations_filters(filter_string)
        if not operation_filters:
            operation_filters = DEFAULT_OPERATION_FILTERS

        response = ListOperationsResponse()

        results, next_token = self.scheduler.list_operations(operation_filters, page_size, page_token)
        response.operations.extend(results)
        response.next_page_token = next_token

        return response

    def delete_operation(self, job_name: str) -> None:
        """DeleteOperation is not supported in BuildGrid."""
        pass

    def cancel_operation(self, operation_name: str) -> None:
        try:
            self.scheduler.cancel_operation(operation_name)

        except NotFoundError:
            raise InvalidArgumentError(f"Operation name does not exist: [{operation_name}]")
