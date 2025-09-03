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


from time import sleep
from typing import Callable, TypeVar

import dns.resolver
import redis
from dns.rdtypes.IN.SRV import SRV
from redis.backoff import EqualJitterBackoff
from redis.exceptions import ConnectionError as RedisConnectionError
from redis.exceptions import TimeoutError as RedisTimeoutError
from redis.sentinel import Sentinel

from buildgrid.server.logging import buildgrid_logger

LOGGER = buildgrid_logger(__name__)

T = TypeVar("T")


class RedisProvider:
    """Provides and manages a Redis connection

    This class manages the connection to a Redis cache.

    The connection can be configured by specifying host/port or by specifying
    a DNS SRV record to use to discover the host/port.

    If a sentinel master name is provided then it is assumed the connection is
    to a Redis sentinel and the master and replica clients will be obtained
    from the sentinel.

    Args:
        host (str | None): The hostname of the Redis server to use.
        port (int | None): The port that Redis is served on.
        password (str | None): The Redis database password to use.
        db (int): The Redis database number to use.
        dns-srv-record (str): Domain name of SRV record used to discover host/port
        sentinel-master-name (str): Service name of Redis master instance, used
            in a Redis sentinel configuration
        retries (int): Max number of times to retry (default 3). Backoff between retries is about 2^(N-1),
            where N is the number of attempts

    Raises:
        RuntimeError: when unable to resolve a host/port to connect to

    """

    def __init__(
        self,
        *,
        host: str | None = None,
        port: int | None = None,
        password: str | None = None,
        db: int | None = None,
        dns_srv_record: str | None = None,
        sentinel_master_name: str | None = None,
        retries: int = 3,
    ) -> None:
        self._password = password
        self._db = db
        self._dns_srv_record = dns_srv_record
        self._sentinel_master_name = sentinel_master_name
        self._retries = retries
        self._retriable_errors = (RedisConnectionError, RedisTimeoutError)

        self._host_infos: list[tuple[str, int]] = []
        self._sentinel: Sentinel | None = None

        self._socket_timeout = 1.0

        if host is not None and port is not None:
            self._host_infos = [(host, port)]

        if self._dns_srv_record is not None:
            self._host_infos = self._perform_dns_srv_request(self._dns_srv_record)

        if not self._host_infos:
            raise RuntimeError("Either host/port or dns_srv_record must be specified")

        self._conns = self._connect()

    def _perform_dns_srv_request(self, domain_name: str) -> list[tuple[str, int]]:
        srv_list: list[tuple[str, int]] = []

        try:
            srv_records = dns.resolver.resolve(domain_name, "SRV")
        except Exception:
            LOGGER.debug("Unable to resolve DNS name.")
            raise RuntimeError

        for srv in srv_records:
            if isinstance(srv, SRV):
                srv_list.append((str(srv.target).rstrip("."), srv.port))

        if not srv_list:
            raise RuntimeError("Host/port not resolvable from DNS SRV record")

        return srv_list

    def _connect(self) -> tuple["redis.Redis[bytes]", "redis.Redis[bytes]"]:
        if self._sentinel_master_name is None:
            r = redis.Redis(
                host=self._host_infos[0][0],
                port=self._host_infos[0][1],
                socket_timeout=self._socket_timeout,
                db=self._db,  # type: ignore
                password=self._password,
            )
            return (r, r)
        else:
            if not self._sentinel:
                self._sentinel = Sentinel(
                    self._host_infos,
                    socket_timeout=self._socket_timeout,
                    db=self._db,
                    password=self._password,
                )
            return (
                self._sentinel.master_for(self._sentinel_master_name, socket_timeout=self._socket_timeout),
                self._sentinel.slave_for(self._sentinel_master_name, socket_timeout=self._socket_timeout),
            )

    def _reresolve_reconnect(self) -> None:
        if self._dns_srv_record:
            self._host_infos = self._perform_dns_srv_request(self._dns_srv_record)
        self._conns = self._connect()

    def execute_rw(self, func: Callable[["redis.Redis[bytes]"], T]) -> T:
        """Calls ``func`` with the redis read/write client as argument.

        The ``func`` may be called more than once if the host has changed.
        """
        retry_num = 0
        backoff = EqualJitterBackoff()
        while True:
            try:
                return func(self._conns[0])
            except self._retriable_errors:
                retry_num += 1
                if retry_num > self._retries:
                    raise
                sleep(backoff.compute(retry_num))
                self._reresolve_reconnect()

    def execute_ro(self, func: Callable[["redis.Redis[bytes]"], T]) -> T:
        """Calls ``func`` with a redis read-only client as argument.

        The ``func`` may be called more than once if the host has changed.
        """
        retry_num = 0
        backoff = EqualJitterBackoff()
        while True:
            try:
                return func(self._conns[1])
            except self._retriable_errors:
                retry_num += 1
                if retry_num > self._retries:
                    raise
                sleep(backoff.compute(retry_num))
                self._reresolve_reconnect()
