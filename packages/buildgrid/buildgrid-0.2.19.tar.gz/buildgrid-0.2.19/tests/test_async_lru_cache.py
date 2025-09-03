# Copyright (C) 2021 Bloomberg LP
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

import asyncio

from buildgrid.server.utils.async_lru_cache import LruCache


def test_get_missing_key():
    async def _test():
        cache = LruCache(10)
        assert await cache.get("foo") is None
        return True

    assert asyncio.run(_test())


def test_set_and_get():
    async def _test():
        cache: LruCache[str] = LruCache(10)
        key = "foo"
        value = "foo value"

        await cache.set(key, value, 10)

        assert await cache.size() == 1
        assert await cache.get(key) == value
        return True

    assert asyncio.run(_test())


def test_expiry():
    async def _test():
        cache: LruCache[str] = LruCache(2)
        await cache.set("a", "vala", 10)
        await cache.set("b", "valb", 10)

        # Add a third key, taking us over the max size
        await cache.set("c", "valc", 10)

        # Ensure that the oldest key was dropped
        assert await cache.get("a") is None
        assert await cache.get("b") == "valb"
        assert await cache.get("c") == "valc"
        return True

    assert asyncio.run(_test())


def test_ttl_expiry():
    async def _test():
        cache: LruCache[str] = LruCache(10)

        # Set a value with a short ttl
        await cache.set("key", "value", 1)

        # Wait for longer than the ttl
        await asyncio.sleep(1.1)

        # Check that the value isn't returned
        assert await cache.get("key") is None
        assert await cache.size() == 0
        return True

    assert asyncio.run(_test())


def test_zero_ttl():
    async def _test():
        cache: LruCache[str] = LruCache(1)

        # Set a value with a zero ttl (ie. live forever)
        await cache.set("key", "value", 0)

        # Wait for a second
        await asyncio.sleep(1)

        # Check that the value hasn't expired
        assert await cache.get("key") == "value"

        # Set a new key, to force expiry via LRU
        await cache.set("new", "value", 10)
        assert await cache.get("key") is None
        return True

    assert asyncio.run(_test())


def test_set():
    async def _test():
        cache: LruCache[str] = LruCache(2)
        await cache.set("a", "vala", 10)
        await cache.set("b", "valb", 10)

        # Check that setting updates the value
        await cache.set("a", "value a", 10)
        assert await cache.get("a") == "value a"

        # Check that setting updates the ttl
        await cache.set("c", "valc", 1)
        await cache.set("c", "valc", 10)
        await asyncio.sleep(1.1)
        assert await cache.get("c") == "valc"

        # Check that expiry is actually LRU
        assert await cache.get("b") is None
        return True

    assert asyncio.run(_test())


def test_get_updates_lru():
    async def _test():
        cache: LruCache[str] = LruCache(2)
        await cache.set("a", "vala", 10)
        await cache.set("b", "valb", 10)

        # Touch the first key we set
        await cache.get("a")

        # Add a new key, taking us over the max size
        await cache.set("c", "valc", 10)

        # Ensure that the second key we set was dropped
        assert await cache.get("b") is None
        assert await cache.get("a") == "vala"
        return True

    assert asyncio.run(_test())
