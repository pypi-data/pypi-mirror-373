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

from cachetools import TTLCache

from buildgrid.server.exceptions import InvalidArgumentError

DEFAULT_TOKEN_REFRESH_SECONDS = 60 * 60
_CACHE_KEY = "token"


class AuthTokenLoader:

    def __init__(self, token_path: str, refresh_in_seconds: int | None = None) -> None:
        self._token_path = token_path
        self._cache: TTLCache[str, str] = TTLCache(
            maxsize=1, ttl=refresh_in_seconds if refresh_in_seconds else DEFAULT_TOKEN_REFRESH_SECONDS
        )

    def _load_token_from_file(self) -> None:
        try:
            with open(self._token_path, mode="r") as token_file:
                token = token_file.read().strip()
                self._cache[_CACHE_KEY] = token
        except Exception as e:
            raise InvalidArgumentError(f"Cannot read token from filepath: {self._token_path}") from e

    def get_token(self) -> str:
        if _CACHE_KEY not in self._cache:
            self._load_token_from_file()

        assert _CACHE_KEY in self._cache
        return self._cache[_CACHE_KEY]
