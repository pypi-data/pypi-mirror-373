# Copyright (C) 2020 Bloomberg LP
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


import operator
from dataclasses import dataclass
from typing import Any

from lark import Tree
from lark.visitors import Interpreter

from buildgrid.server.exceptions import InvalidArgumentError
from buildgrid.server.operations.filtering import OperationFilter
from buildgrid.server.operations.filtering.sanitizer import (
    DatetimeValueSanitizer,
    OperationStageValueSanitizer,
    RegexValueSanitizer,
    SortKeyValueSanitizer,
    ValueSanitizer,
)


@dataclass
class OperationFilterSpec:
    name: str
    description: str
    sanitizer: ValueSanitizer


# Valid operation filters mapped to regexes representing valid values.
VALID_OPERATION_FILTERS = {
    "stage": OperationFilterSpec(
        name="Stage",
        description="Operation stage, for example QUEUED or EXECUTING.",
        sanitizer=OperationStageValueSanitizer("stage"),
    ),
    # The operation name can technically be parsed as a UUID4, but this
    # parses it as an arbitrary string in case the naming scheme changes
    # in the future
    "name": OperationFilterSpec(
        name="Name",
        description="Operation name, without the BuildGrid instance name.",
        sanitizer=RegexValueSanitizer("name", r"\S+"),
    ),
    # The command is an arbitrary string
    "command": OperationFilterSpec(
        name="Command",
        description="Command to be executed by the remote worker.",
        sanitizer=RegexValueSanitizer("command", r".+"),
    ),
    # The platform properties are `key:value`
    "platform": OperationFilterSpec(
        name="Platform",
        description="Platform property specified by the Action, in the form `key:value`.",
        sanitizer=RegexValueSanitizer("platform", r"\S+:.+"),
    ),
    "action_digest": OperationFilterSpec(
        name="Action Digest",
        description="Digest of the Action message, in the form `hash/size_bytes`.",
        sanitizer=RegexValueSanitizer("action_digest", r"[a-f0-9]+/[0-9]+"),
    ),
    # The request metadata is all arbitrary strings
    "invocation_id": OperationFilterSpec(
        name="Invocation ID",
        description="The unique ID for a given invocation of the tool which started the Operation.",
        sanitizer=RegexValueSanitizer("invocation_id", r".+"),
    ),
    "correlated_invocations_id": OperationFilterSpec(
        name="Correlated Invocations ID",
        description="The unique ID for a set of related tool invocations.",
        sanitizer=RegexValueSanitizer("correlated_invocations_id", r".+"),
    ),
    "tool_name": OperationFilterSpec(
        name="Tool Name",
        description="The name of the tool which started the Operation.",
        sanitizer=RegexValueSanitizer("tool_name", r".+"),
    ),
    "tool_version": OperationFilterSpec(
        name="Tool Version",
        description="The version of the tool that started the Operation.",
        sanitizer=RegexValueSanitizer("tool_version", r".+"),
    ),
    "action_mnemonic": OperationFilterSpec(
        name="Action Mnemonic",
        description="A brief description of the kind of action. This is not "
        "standardized and contents are up to the client tooling used.",
        sanitizer=RegexValueSanitizer("action_mnemonic", r".+"),
    ),
    "target_id": OperationFilterSpec(
        name="Target ID",
        description="An identifier for the target which produced this action. "
        "A single target may relate to one or many actions.",
        sanitizer=RegexValueSanitizer("target_id", r".+"),
    ),
    "configuration_id": OperationFilterSpec(
        name="Configuration ID",
        description="An identifier for the configuration in which the target was built, "
        "e.g. for differentiating host tooling or different target platforms.",
        sanitizer=RegexValueSanitizer("configuration_id", r".+"),
    ),
    # Validate timestamps with a special sanitizer
    "queued_time": OperationFilterSpec(
        name="Queued Time",
        description="The time at which the Action was queued.",
        sanitizer=DatetimeValueSanitizer("queued_time"),
    ),
    "start_time": OperationFilterSpec(
        name="Start Time",
        description="The time at which a worker started executing the Action.",
        sanitizer=DatetimeValueSanitizer("start_time"),
    ),
    "completed_time": OperationFilterSpec(
        name="Completed Time",
        description="The time at which a worker finished executing the Action.",
        sanitizer=DatetimeValueSanitizer("completed_time"),
    ),
    # Client identity metadata is all arbitrary strings
    "client_workflow": OperationFilterSpec(
        name="Client Workflow",
        description="The client workflow information that was used to authorize the Action.",
        sanitizer=RegexValueSanitizer("action_mnemonic", r".+"),
    ),
    "client_actor": OperationFilterSpec(
        name="Client Actor",
        description="The client actor that was used to authorize the Action.",
        sanitizer=RegexValueSanitizer("target_id", r".+"),
    ),
    "client_subject": OperationFilterSpec(
        name="Client Subject",
        description="The client subject that was used to authorize the Action.",
        sanitizer=RegexValueSanitizer("configuration_id", r".+"),
    ),
    # Backends determine what sort orders are acceptable
    "sort_order": OperationFilterSpec(
        name="Sort Order",
        description="Define an ordering for the results.",
        sanitizer=SortKeyValueSanitizer("sort_order"),
    ),
}


OPERATOR_MAP = {
    "=": operator.eq,
    ">": operator.gt,
    ">=": operator.ge,
    "<": operator.lt,
    "<=": operator.le,
    "!=": operator.ne,
}


class FilterTreeInterpreter(Interpreter[Any]):
    """Interpreter for the parse tree.

    Calling FilterTreeInterpreter().visit(tree) walks the parse tree and
    outputs a list of OperationFilters."""

    def filter_phrase(self, tree: Tree) -> list[OperationFilter]:
        return self.visit_children(tree)

    def filter_elem(self, tree: Tree) -> OperationFilter:
        try:
            token_map = {token.type: str(token) for token in tree.children}  # type: ignore

            # Check that the parameter is valid
            parameter = token_map["PARAMETER"]
            if parameter not in VALID_OPERATION_FILTERS:
                raise InvalidArgumentError(f"Invalid filter parameter [{parameter}].")

            # Sanitize the value
            sanitizer = VALID_OPERATION_FILTERS[parameter].sanitizer
            sanitized_value = sanitizer.sanitize(token_map["VALUE"])

            return OperationFilter(
                parameter=token_map["PARAMETER"], operator=OPERATOR_MAP[token_map["OPERATOR"]], value=sanitized_value
            )
        except KeyError as e:
            raise InvalidArgumentError(f"Invalid filter element. Token map: {token_map}") from e
