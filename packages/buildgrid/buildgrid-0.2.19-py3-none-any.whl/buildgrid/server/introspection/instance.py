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

from google.protobuf.timestamp_pb2 import Timestamp

from buildgrid._protos.build.buildgrid.introspection_pb2 import (
    DESCRIPTOR,
    ListWorkersRequest,
    ListWorkersResponse,
    OperationFilter,
    OperationFilters,
    OperationStats,
    OperationStatsRequest,
    RegisteredWorker,
    WorkerOperation,
)
from buildgrid.server.enums import BotStatus
from buildgrid.server.exceptions import InvalidArgumentError
from buildgrid.server.operations.filtering.interpreter import VALID_OPERATION_FILTERS, OperationFilterSpec
from buildgrid.server.operations.filtering.sanitizer import DatetimeValueSanitizer, SortKeyValueSanitizer
from buildgrid.server.scheduler.impl import Scheduler
from buildgrid.server.servicer import Instance
from buildgrid.server.settings import MAX_LIST_PAGE_SIZE


class IntrospectionInstance(Instance):
    SERVICE_NAME = DESCRIPTOR.services_by_name["Introspection"].full_name

    def __init__(self, sql: Scheduler) -> None:
        self._scheduler = sql

    def list_workers(self, request: ListWorkersRequest) -> ListWorkersResponse:
        if request.page_size < 0:
            raise InvalidArgumentError("Page size must be a positive integer")
        if request.page < 0:
            raise InvalidArgumentError("Page number must be a positive integer")

        page = request.page or 1
        page_size = min(request.page_size, MAX_LIST_PAGE_SIZE) or MAX_LIST_PAGE_SIZE
        bot_entries, count = self._scheduler.list_workers(request.worker_name, page, page_size)

        workers = []
        for bot in bot_entries:
            last_update = Timestamp()
            last_update.FromDatetime(bot.last_update_timestamp)
            expiry: Timestamp | None = None
            if bot.expiry_time is not None:
                expiry = Timestamp()
                expiry.FromDatetime(bot.expiry_time)
            worker = RegisteredWorker(
                worker_name=bot.bot_id,
                session_name=bot.name,
                last_updated=last_update,
                bot_status=BotStatus(bot.bot_status).value,
                expiry_time=expiry,
            )
            for operation_name, action_digest in self._scheduler.get_operations_for_bot(bot.bot_id):
                worker.action_digest.CopyFrom(action_digest)
                worker_operation = WorkerOperation(
                    operation_name=operation_name,
                    action_digest=action_digest,
                )
                worker.operations.append(worker_operation)
            workers.append(worker)

        return ListWorkersResponse(workers=workers, total=count, page=page, page_size=page_size)

    def get_operation_filters(self) -> OperationFilters:
        def _generate_filter_spec(key: str, spec: OperationFilterSpec) -> OperationFilter:
            comparators = ["<", "<=", "=", "!=", ">=", ">"]
            filter_type = "text"
            if isinstance(spec.sanitizer, SortKeyValueSanitizer):
                comparators = ["="]
            elif isinstance(spec.sanitizer, DatetimeValueSanitizer):
                filter_type = "datetime"

            try:
                values = spec.sanitizer.valid_values
            except NotImplementedError:
                values = []

            return OperationFilter(
                key=key,
                name=spec.name,
                type=filter_type,
                description=spec.description,
                comparators=comparators,
                values=values,
            )

        return OperationFilters(
            filters=[_generate_filter_spec(key, spec) for key, spec in VALID_OPERATION_FILTERS.items()]
        )

    def get_operation_stats(self, request: OperationStatsRequest) -> OperationStats:
        stats = OperationStats(
            queue_position=self._scheduler.get_queue_position(request.operation_name, request.instance_name)
        )
        return stats
