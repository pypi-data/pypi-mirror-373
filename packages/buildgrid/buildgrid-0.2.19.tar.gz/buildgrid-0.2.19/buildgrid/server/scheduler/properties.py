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
import hashlib
import json
from collections import defaultdict
from dataclasses import dataclass
from itertools import chain, combinations
from typing import Iterable, Protocol

from buildgrid._protos.build.bazel.remote.execution.v2.remote_execution_pb2 import Platform
from buildgrid._protos.google.devtools.remoteworkers.v1test2.bots_pb2 import BotSession
from buildgrid.server.exceptions import FailedPreconditionError
from buildgrid.server.logging import buildgrid_logger

CAPABILITIES_WARNING_THRESHOLD = 10
LOGGER = buildgrid_logger(__name__)


def hash_from_dict(dictionary: dict[str, list[str]]) -> str:
    """Get the hash represntation of a dictionary"""
    return hashlib.sha1(json.dumps(dictionary, sort_keys=True).encode()).hexdigest()


class PropertySet(Protocol):
    def execution_properties(self, platform: Platform) -> tuple[str, dict[str, list[str]]]:
        """
        Parses a platform value and returns the match properties used for scheduling.
        Returns a label which can be used for applying metrics.
        """

    def worker_properties(self, bot_session: BotSession) -> list[dict[str, list[str]]]:
        """
        Find all the valid property combinations which can be used to assign work to a bot.
        """

    def bot_property_labels(self, bot_session: BotSession) -> list[str]:
        """
        Find all label_key's which can be used to identify bot types in logging and metrics.
        """


class DynamicPropertySet:
    def __init__(
        self,
        *,
        unique_property_keys: set[str],
        match_property_keys: set[str],
        wildcard_property_keys: set[str],
        label_key: str | None = None,
    ) -> None:
        if unregistered_unique_keys := (unique_property_keys - match_property_keys) - wildcard_property_keys:
            raise ValueError(f"Unique keys configured which are not match or wildcards: {unregistered_unique_keys}")

        if label_key and label_key not in match_property_keys and label_key not in wildcard_property_keys:
            raise ValueError(f"Label key is not registered as a match or wildcard key: {label_key}")

        self.unique_property_keys = set(unique_property_keys)
        self.match_property_keys = set(match_property_keys)
        self.wildcard_property_keys = set(wildcard_property_keys)
        self.all_property_keys = match_property_keys | wildcard_property_keys
        self.label_key = label_key

    def execution_properties(self, platform: Platform) -> tuple[str, dict[str, list[str]]]:
        properties: dict[str, set[str]] = defaultdict(set)
        for platform_property in platform.properties:
            properties[platform_property.name].add(platform_property.value)

        label = "unknown"
        if self.label_key in properties:
            label = sorted(properties[self.label_key])[0]

        for name, values in properties.items():
            if name not in self.all_property_keys:
                raise FailedPreconditionError(
                    f"Unregistered platform property [{name}={values}]."
                    f" Known properties are: [{self.all_property_keys}]"
                )
            if name in self.unique_property_keys and len(values) > 1:
                raise FailedPreconditionError(
                    f"Unique platform property [{name}] can only be set once. Got: [{values}]"
                )

        result = {k: sorted(v) for k, v in properties.items() if k in self.match_property_keys}
        return label, result

    def worker_properties(self, bot_session: BotSession) -> list[dict[str, list[str]]]:
        properties = bot_properties(bot_session)
        properties = {k: v for k, v in properties.items() if k in self.match_property_keys}
        return partial_bot_properties(properties)

    def bot_property_labels(self, bot_session: BotSession) -> list[str]:
        properties = bot_properties(bot_session)
        if self.label_key in properties:
            return sorted(properties[self.label_key])
        return []


Properties = set[tuple[str, str]]


@dataclass
class PropertyLabel:
    label: str
    properties: Properties


class StaticPropertySet:
    def __init__(
        self,
        *,
        property_labels: list[PropertyLabel],
        wildcard_property_keys: set[str],
    ) -> None:
        self.property_labels = property_labels
        self.wildcard_property_keys = wildcard_property_keys

    def execution_properties(self, platform: Platform) -> tuple[str, dict[str, list[str]]]:
        execute_properties = {
            (platform_property.name, platform_property.value)
            for platform_property in platform.properties
            if platform_property.name not in self.wildcard_property_keys
        }

        for property_label in self.property_labels:
            if len(execute_properties - property_label.properties) == 0:
                return property_label.label, merge_property_pairs(property_label.properties)

        raise FailedPreconditionError(f"Could not find property set for {execute_properties}")

    def worker_properties(self, bot_session: BotSession) -> list[dict[str, list[str]]]:
        bots_properties = bot_properties(bot_session)
        property_pairs = {
            (key, value)
            for key, values in bots_properties.items()
            for value in values
            if key not in self.wildcard_property_keys
        }

        property_sets = []
        for property_set in self.property_labels:
            if len(property_set.properties - property_pairs) == 0:
                property_sets.append(merge_property_pairs(property_set.properties))

        if len(property_sets) == 0:
            raise FailedPreconditionError(f"Could not find property set for {bots_properties}")
        return [{k: sorted(v) for k, v in props.items()} for props in property_sets]

    def bot_property_labels(self, bot_session: BotSession) -> list[str]:
        # To gain a label the bot must have all the properties for that label.
        bot_props = bot_properties(bot_session)
        return [
            property_label.label
            for property_label in self.property_labels
            if all(key in bot_props and value in bot_props[key] for [key, value] in property_label.properties)
        ]


def bot_properties(bot_session: BotSession) -> dict[str, set[str]]:
    worker_capabilities: dict[str, set[str]] = {}
    if bot_session.worker.devices:
        # According to the spec:
        #   "The first device in the worker is the "primary device" -
        #   that is, the device running a bot and which is
        #   responsible for actually executing commands."
        primary_device = bot_session.worker.devices[0]

        for device_property in primary_device.properties:
            if device_property.key not in worker_capabilities:
                worker_capabilities[device_property.key] = set()
            worker_capabilities[device_property.key].add(device_property.value)
    return worker_capabilities


def partial_bot_properties(properties: dict[str, set[str]]) -> list[dict[str, list[str]]]:
    property_pairs = flatten_properties(properties)

    if len(property_pairs) > CAPABILITIES_WARNING_THRESHOLD:
        LOGGER.warning(
            "A worker with a large capabilities dictionary has been connected. "
            f"Processing its capabilities may take a while. Capabilities: {property_pairs}"
        )

    # Using the itertools powerset recipe, construct the powerset of the tuples
    powerset = chain.from_iterable(combinations(property_pairs, r) for r in range(len(property_pairs) + 1))
    return list(map(merge_property_pairs, powerset))


def flatten_properties(properties: dict[str, set[str]]) -> list[tuple[str, str]]:
    return [(name, value) for name in sorted(properties) for value in sorted(properties[name])]


def merge_property_pairs(property_pairs: Iterable[tuple[str, str]]) -> dict[str, list[str]]:
    properties: dict[str, list[str]] = {}
    for name, value in property_pairs:
        properties.setdefault(name, []).append(value)
    return {k: sorted(v) for k, v in properties.items()}
