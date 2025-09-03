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
from typing import Union

from buildgrid._protos.build.bazel.remote.execution.v2.remote_execution_pb2 import DESCRIPTOR as RE_DESCRIPTOR
from buildgrid._protos.build.bazel.remote.execution.v2.remote_execution_pb2 import (
    ActionCacheUpdateCapabilities,
    CacheCapabilities,
    ExecutionCapabilities,
    ServerCapabilities,
    SymlinkAbsolutePathStrategy,
)
from buildgrid._protos.build.bazel.semver.semver_pb2 import SemVer
from buildgrid.server.actioncache.caches.action_cache_abc import ActionCacheABC
from buildgrid.server.actioncache.instance import ActionCache
from buildgrid.server.cas.instance import ContentAddressableStorageInstance
from buildgrid.server.execution.instance import ExecutionInstance
from buildgrid.server.servicer import Instance
from buildgrid.server.settings import HIGH_REAPI_VERSION, LOW_REAPI_VERSION, MAX_REQUEST_SIZE
from buildgrid.server.utils.digests import get_hash_type

ActionCacheInstance = Union[ActionCache, ActionCacheABC]


class CapabilitiesInstance(Instance):
    SERVICE_NAME = RE_DESCRIPTOR.services_by_name["Capabilities"].full_name

    def __init__(
        self,
        cas_instance: ContentAddressableStorageInstance | None = None,
        action_cache_instance: ActionCacheInstance | None = None,
        execution_instance: ExecutionInstance | None = None,
    ) -> None:
        self._cas_instance = cas_instance
        self._action_cache_instance = action_cache_instance
        self._execution_instance = execution_instance
        self._high_api_version = _split_semantic_version(HIGH_REAPI_VERSION)
        self._low_api_version = _split_semantic_version(LOW_REAPI_VERSION)

    def add_cas_instance(self, cas_instance: ContentAddressableStorageInstance) -> None:
        self._cas_instance = cas_instance

    def add_action_cache_instance(self, action_cache_instance: ActionCacheInstance) -> None:
        self._action_cache_instance = action_cache_instance

    def add_execution_instance(self, execution_instance: ExecutionInstance) -> None:
        self._execution_instance = execution_instance

    def get_capabilities(self) -> ServerCapabilities:
        # The caching capabilities are VERY hardcoded by the buildgrid server components.
        # Simply forwarding abilities from remote storage or local components does more
        # harm than good, as the remote capabilities do not feed into usage by most components.
        #
        # The most sane way to override these values would be via server configuration,
        # not by dynamically fetching the capabilities remotely.
        #
        # If we want to properly support this functionality, a large refactor would be needed.
        return ServerCapabilities(
            cache_capabilities=CacheCapabilities(
                digest_functions=[get_hash_type()],
                max_batch_total_size_bytes=MAX_REQUEST_SIZE,
                symlink_absolute_path_strategy=SymlinkAbsolutePathStrategy.DISALLOWED,
                action_cache_update_capabilities=ActionCacheUpdateCapabilities(
                    update_enabled=bool(self._action_cache_instance and self._action_cache_instance.allow_updates)
                ),
            ),
            execution_capabilities=ExecutionCapabilities(
                exec_enabled=self._execution_instance is not None,
                digest_function=get_hash_type(),
                digest_functions=[get_hash_type()],
            ),
            low_api_version=self._low_api_version,
            high_api_version=self._high_api_version,
        )


def _split_semantic_version(version_string: str) -> SemVer:
    major_version, minor_version, patch_version = version_string.split(".")

    semantic_version = SemVer()
    semantic_version.major = int(major_version)
    semantic_version.minor = int(minor_version)
    semantic_version.patch = int(patch_version)

    return semantic_version
