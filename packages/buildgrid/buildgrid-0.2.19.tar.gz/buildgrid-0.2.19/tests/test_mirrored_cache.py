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


from typing import Iterator

import pytest

from buildgrid._protos.build.bazel.remote.execution.v2.remote_execution_pb2 import ActionResult, Digest
from buildgrid.server.actioncache.caches.action_cache_abc import ActionCacheABC
from buildgrid.server.actioncache.caches.lru_cache import LruActionCache
from buildgrid.server.actioncache.caches.mirrored_cache import MirroredCache
from buildgrid.server.cas.storage import lru_memory_cache
from buildgrid.server.exceptions import NotFoundError


@pytest.fixture
def first_cache() -> ActionCacheABC:
    storage = lru_memory_cache.LRUMemoryCache(1024 * 1024)
    return LruActionCache(storage, max_cached_refs=1024)


@pytest.fixture
def second_cache() -> ActionCacheABC:
    storage = lru_memory_cache.LRUMemoryCache(1024 * 1024)
    return LruActionCache(storage, max_cached_refs=1024)


@pytest.fixture
def cache(first_cache: ActionCacheABC, second_cache: ActionCacheABC) -> Iterator[MirroredCache]:
    yield MirroredCache(first=first_cache, second=second_cache)


def test_mirrored_cache_both_missing(cache: ActionCacheABC):
    digest = Digest(hash="foo", size_bytes=123)
    with pytest.raises(NotFoundError):
        cache.get_action_result(digest)


def test_mirrored_first_missing(cache: ActionCacheABC, first_cache: ActionCacheABC, second_cache: ActionCacheABC):
    ar = ActionResult(exit_code=42)
    digest = Digest(hash="foo", size_bytes=123)
    second_cache.update_action_result(digest, ar)

    result = cache.get_action_result(digest)
    # copied into the first cache
    first_result = first_cache.get_action_result(digest)
    assert ar == result == first_result


def test_mirrored_second_missing(cache: ActionCacheABC, first_cache: ActionCacheABC, second_cache: ActionCacheABC):
    ar = ActionResult(exit_code=42)
    digest = Digest(hash="foo", size_bytes=123)
    first_cache.update_action_result(digest, ar)

    result = cache.get_action_result(digest)
    # copied into the second cache
    second_result = second_cache.get_action_result(digest)
    assert ar == result == second_result


def test_mirrored_both_existing_choose_first(
    cache: ActionCacheABC, first_cache: ActionCacheABC, second_cache: ActionCacheABC
):
    ar1 = ActionResult(exit_code=42)
    ar2 = ActionResult(exit_code=43)
    digest = Digest(hash="foo", size_bytes=123)
    first_cache.update_action_result(digest, ar1)
    second_cache.update_action_result(digest, ar2)

    result = cache.get_action_result(digest)
    assert ar1 == result
    assert ar2 != result


def test_mirrored_cache_update(cache: ActionCacheABC, first_cache: ActionCacheABC, second_cache: ActionCacheABC):
    ar = ActionResult(exit_code=42)
    digest = Digest(hash="foo", size_bytes=123)
    cache.update_action_result(digest, ar)

    assert ar == first_cache.get_action_result(digest)
    assert ar == second_cache.get_action_result(digest)
