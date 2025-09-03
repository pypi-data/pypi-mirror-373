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


import os
import sys
from collections import defaultdict
from typing import TYPE_CHECKING, Any, Callable, Hashable, Iterable, Sequence, TypedDict, TypeVar
from urllib.parse import urlparse

import buildgrid_metering.client as metering
import click
import grpc
import jsonschema
import requests
import yaml
from buildgrid_metering.client.exceptions import MeteringServiceClientError, MeteringServiceError
from importlib_resources import files

from buildgrid.server.actioncache.caches.action_cache_abc import ActionCacheABC
from buildgrid.server.actioncache.caches.lru_cache import LruActionCache
from buildgrid.server.actioncache.caches.mirrored_cache import MirroredCache
from buildgrid.server.actioncache.caches.remote_cache import RemoteActionCache
from buildgrid.server.actioncache.caches.s3_cache import S3ActionCache
from buildgrid.server.actioncache.caches.sharded_cache import ShardedActionCache
from buildgrid.server.actioncache.caches.with_cache import WithCacheActionCache
from buildgrid.server.actioncache.caches.write_once_cache import WriteOnceActionCache
from buildgrid.server.actioncache.instance import ActionCache
from buildgrid.server.bots.instance import BotsInterface
from buildgrid.server.build_events.storage import BuildEventStreamStorage
from buildgrid.server.cas.instance import ByteStreamInstance, ContentAddressableStorageInstance
from buildgrid.server.cas.storage.disk import DiskStorage
from buildgrid.server.cas.storage.index.sql import SQLIndex
from buildgrid.server.cas.storage.lru_memory_cache import LRUMemoryCache
from buildgrid.server.cas.storage.remote import RemoteStorage
from buildgrid.server.cas.storage.replicated import ReplicatedStorage
from buildgrid.server.cas.storage.s3 import S3Storage
from buildgrid.server.cas.storage.sharded import ShardedStorage
from buildgrid.server.cas.storage.size_differentiated import SizeDifferentiatedStorage, SizeLimitedStorageType
from buildgrid.server.cas.storage.sql import SQLStorage
from buildgrid.server.cas.storage.storage_abc import StorageABC
from buildgrid.server.cas.storage.with_cache import WithCacheStorage
from buildgrid.server.client.asset import AssetClient
from buildgrid.server.client.authentication import ClientCredentials
from buildgrid.server.client.channel import setup_channel
from buildgrid.server.controller import ExecutionController
from buildgrid.server.enums import ActionCacheEntryType, MeteringThrottleAction, ServiceName
from buildgrid.server.introspection.instance import IntrospectionInstance
from buildgrid.server.limiter import Limiter, LimiterConfig
from buildgrid.server.scheduler import (
    AgedJobHandlerOptions,
    DynamicPropertySet,
    PropertyLabel,
    PropertySet,
    Scheduler,
    StaticPropertySet,
)
from buildgrid.server.scheduler.assigner import (
    AssignByCapacity,
    AssignByLocality,
    AssignerConfig,
    BotAssignmentStrategy,
    PriorityAgeAssignerConfig,
    SamplingConfig,
)
from buildgrid.server.sentry import Sentry
from buildgrid.server.settings import (
    DEFAULT_MAX_EXECUTION_TIMEOUT,
    DEFAULT_MAX_LIST_OPERATION_PAGE_SIZE,
    DEFAULT_PLATFORM_PROPERTY_KEYS,
    INSECURE_URI_SCHEMES,
    S3_MAX_RETRIES,
    S3_TIMEOUT_CONNECT,
    S3_TIMEOUT_READ,
    S3_USERAGENT_NAME,
    SECURE_URI_SCHEMES,
)
from buildgrid.server.sql.provider import SqlProvider

from .config import ChannelConfig

if TYPE_CHECKING:
    from buildgrid.server.actioncache.caches.redis_cache import RedisActionCache
    from buildgrid.server.cas.storage.index.redis import RedisIndex
    from buildgrid.server.cas.storage.redis import RedisStorage
    from buildgrid.server.redis.provider import RedisProvider


_Func = TypeVar("_Func", bound=Callable)  # type: ignore[type-arg]

# Stores the definitions of struct loaders for tags.
object_definitions: dict[str, Callable] = {}  # type: ignore[type-arg]

# Stores notes for keys that are marked deprecated. key=yaml-key, value=deprecation-message
deprecated_object_keys: dict[str, dict[str, str]] = {}

# Stores the definitions of string loaders for tags
string_definitions: dict[str, Callable] = {}  # type: ignore[type-arg]


def object_tag(kind: str, deprecated_keys: dict[str, str] | None = None) -> Callable[[_Func], _Func]:
    """
    Register a tag with custom decoder logic for a yaml object field.
    """

    def wrapper(f: _Func) -> _Func:
        object_definitions[kind] = f
        if deprecated_keys is not None:
            deprecated_object_keys[kind] = deprecated_keys
        return f

    return wrapper


def string_tag(kind: str) -> Callable[[_Func], _Func]:
    """
    Register a tag with custom decoder logic for a yaml string value field.
    """

    def wrapper(f: _Func) -> _Func:
        string_definitions[kind] = f
        return f

    return wrapper


@object_tag("!channel")
def load_channel(
    insecure_mode: bool,
    address: str,
    credentials: dict[str, str] | None = None,
) -> ChannelConfig:
    """Creates a GRPC channel.

    The :class:`Channel` class returns a `grpc.Channel` and is generated from
    the tag ``!channel``. Creates either a secure or insecure channel.

    Usage
        .. code:: yaml

            - !channel
              address (str): Address for the channel. (For example,
                'localhost:50055' or 'unix:///tmp/sock')
              port (int): A port for the channel (only if no address was specified).
              insecure-mode: false
              credentials:
                tls-server-key: !expand-path ~/.config/buildgrid/server.key
                tls-server-cert: !expand-path ~/.config/buildgrid/server.cert
                tls-client-certs: !expand-path ~/.config/buildgrid/client.cert

    Args:
        port (int): A port for the channel.
        insecure_mode (bool): If ``True``, generates an insecure channel, even
            if there are credentials. Defaults to ``True``.
        credentials (dict, optional): A dictionary in the form::

            tls-server-key: /path/to/server-key
            tls-server-cert: /path/to/server-cert
            tls-client-certs: /path/to/client-certs
    """

    if not insecure_mode:
        _validate_server_credentials(credentials)
        return ChannelConfig(insecure_mode=insecure_mode, address=address, credentials=credentials)
    return ChannelConfig(insecure_mode=False, address=address, credentials=None)


@string_tag("!expand-path")
def expand_path(path: str) -> str:
    """Returns a string of the user's path after expansion.

    The :class:`ExpandPath` class returns a string and is generated from the
    tag ``!expand-path``.

    Usage
        .. code:: yaml

            path: !expand-path ~/bgd-data/cas

    Args:
        path (str): Can be used with strings such as: ``~/dir/to/something``
            or ``$HOME/certs``
    """

    path = os.path.expanduser(path)
    path = os.path.expandvars(path)
    return path


@string_tag("!expand-vars")
def expand_vars(value: str) -> str:
    """Expand environment variables in a string.

    The :class:`ExpandVars` class returns a string and is generated from the
    tag ``!expand-vars``.

    Usage
        .. code:: yaml

            endpoint: !expand-vars $ENDPOINT

    Args:
        path (str): Can be used with strings such as: ``http://$ENDPOINT``
    """

    return os.path.expandvars(value)


@string_tag("!read-file")
def read_file(path: str) -> str:
    """Returns a string of the contents of the specified file.

    The :class:`ReadFile` class returns a string and is generated from the
    tag ``!read-file``.

    Usage
        .. code:: yaml

            secret_key: !read-file /var/bgd/s3-secret-key

    Args:
        path (str): Can be used with strings such as: ``~/path/to/some/file``
            or ``$HOME/myfile`` or ``/path/to/file``
    """

    path = os.path.expandvars(os.path.expanduser(path))

    if not os.path.exists(path):
        click.echo(
            click.style(
                f"ERROR: read-file `{path}` failed due to it not existing or bad permissions.",
                fg="red",
                bold=True,
            ),
            err=True,
        )
        sys.exit(-1)
    else:
        with open(path, "r", encoding="utf-8") as file:
            try:
                file_contents = "\n".join(file.readlines()).strip()
                return file_contents
            except IOError as e:
                click.echo(f"ERROR: read-file failed to read file `{path}`: {e}", err=True)
                sys.exit(-1)


@object_tag("!disk-storage")
def load_disk_storage(path: str) -> DiskStorage:
    """Generates :class:`buildgrid.server.cas.storage.disk.DiskStorage` using the tag ``!disk-storage``.

    Usage
        .. code:: yaml

            - !disk-storage
              path: /opt/bgd/cas-storage

    Args:
        path (str): Path to directory to storage.
    """

    return DiskStorage(path)


@object_tag("!lru-storage")
def load_lru_storage(size: str) -> LRUMemoryCache:
    """Generates :class:`buildgrid.server.cas.storage.lru_memory_cache.LRUMemoryCache` using the tag ``!lru-storage``.

    Usage
        .. code:: yaml

            - !lru-storage
              size: 2048M

    Args:
        size (int): Size e.g ``10kb``. Size parsed with
            :meth:`buildgrid.server.app.settings.parser._parse_size`.
    """

    return LRUMemoryCache(_parse_size(size))


@object_tag("!s3-storage")
def load_s3_storage(
    bucket: str,
    endpoint: str,
    access_key: str,
    secret_key: str,
    read_timeout_seconds_per_kilobyte: float | None = None,
    write_timeout_seconds_per_kilobyte: float | None = None,
    read_timeout_min_seconds: float = S3_TIMEOUT_READ,
    write_timeout_min_seconds: float = S3_TIMEOUT_READ,
    versioned_deletes: bool = False,
    hash_prefix_size: int | None = None,
    path_prefix_string: str | None = None,
) -> S3Storage:
    """Generates :class:`buildgrid.server.cas.storage.s3.S3Storage` using the tag ``!s3-storage``.

    Usage
        .. code:: yaml

            - !s3-storage
              bucket: bgd-bucket-{digest[0]}{digest[1]}
              endpoint: http://127.0.0.1:9000
              access_key: !read-file /var/bgd/s3-access-key
              secret_key: !read-file /var/bgd/s3-secret-key
              read_timeout_seconds_per_kilobyte: 0.01
              write_timeout_seconds_per_kilobyte: 0.01
              read_timeout_min_seconds: 120
              write_timeout_min_seconds: 120

    Args:
        bucket (str): Name of bucket
        endpoint (str): URL of endpoint.
        access-key (str): S3-ACCESS-KEY
        secret-key (str): S3-SECRET-KEY
        read_timeout_seconds_per_kilobyte (float): S3 Read timeout in seconds/kilobyte
        write_timeout_seconds_per_kilobyte (float): S3 Write timeout in seconds/kilobyte
        read_timeout_min_seconds (float): The minimal timeout for S3 read
        write_timeout_min_seconds (float): The minimal timeout for S3 writes
        versioned_deletes (bool): Query and use the VersionId when performing deletes.
        hash-prefix-size (int): Number of hash characters to use as prefix in s3 object name.
        path-prefix-string (str): Additional string for path prefix
    """

    return S3Storage(
        bucket,
        endpoint_url=endpoint,
        s3_read_timeout_seconds_per_kilobyte=read_timeout_seconds_per_kilobyte,
        s3_write_timeout_seconds_per_kilobyte=write_timeout_seconds_per_kilobyte,
        s3_read_timeout_min_seconds=read_timeout_min_seconds,
        s3_write_timeout_min_seconds=write_timeout_min_seconds,
        s3_versioned_deletes=versioned_deletes,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        s3_hash_prefix_size=hash_prefix_size,
        s3_path_prefix_string=path_prefix_string,
    )


@object_tag("!redis-connection")
def load_redis_connection(
    host: str | None = None,
    port: int | None = None,
    password: str | None = None,
    db: int | None = None,
    dns_srv_record: str | None = None,
    sentinel_master_name: str | None = None,
    retries: int = 3,
) -> "RedisProvider":
    """Generates :class:`buildgrid.server.redis.provider.RedisProvider` using the tag ``!redis-connection``

    Usage
        .. code:: yaml

            - !redis-connection
              host: redis
              port: 6379
              password: !read-file /var/bgd/redis-pass
              db: 0
              dns-srv-record: <Domain name of SRV record>
              sentinel-master-name: <service_name of Redis sentinel's master instance>
              retries: 3


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
    """

    # Import here so there is no global buildgrid dependency on redis
    from buildgrid.server.redis.provider import RedisProvider

    # ... validations like host/port xor dns srv record
    return RedisProvider(
        host=host,
        port=port,
        password=password,
        db=db,
        dns_srv_record=dns_srv_record,
        sentinel_master_name=sentinel_master_name,
        retries=retries,
    )


@object_tag("!redis-storage")
def load_redis_storage(redis: "RedisProvider") -> "RedisStorage":
    """Generates :class:`buildgrid.server.cas.storage.redis.RedisStorage` using the tag ``!redis-storage``.

    Usage
        .. code:: yaml

            # This assumes that the YAML anchors are defined elsewhere
            - !redis-storage
              redis: *redis-connection

    Args:
        redis (:class:`buildgrid.server.redis.provider.RedisProvider`): A configured Redis
            connection manager. This must be an object with an ``!redis-connection`` YAML tag.
    """

    # Import here so there is no global buildgrid dependency on redis
    from buildgrid.server.cas.storage.redis import RedisStorage

    return RedisStorage(redis)


@object_tag("!redis-index")
def load_redis_index(storage: StorageABC, redis: "RedisProvider", prefix: str | None = None) -> "RedisIndex":
    """Generates :class:`buildgrid.server.cas.storage.index.redis.RedisIndex`
    using the tag ``!redis-index``.

    Usage
        .. code:: yaml

            - !redis-index
              # This assumes that a storage instance is defined elsewhere
              # with a `&cas-storage` anchor
              storage: *cas-storage
              redis: *redis
              prefix: "B"

    Args:
        storage(:class:`buildgrid.server.cas.storage.storage_abc.StorageABC`):
            Instance of storage to use. This must be a storage object constructed using
            a YAML tag ending in ``-storage``, for example ``!disk-storage``.
        redis (:class:`buildgrid.server.redis.provider.RedisProvider`): A configured Redis
            connection manager. This must be an object with an ``!redis-connection`` YAML tag.
        prefix (str): An optional prefix to use to prefix keys written by this index. If not
            specified a prefix of "A" is used.
    """

    # Import here so there is no global buildgrid dependency on redis
    from buildgrid.server.cas.storage.index.redis import RedisIndex

    return RedisIndex(redis=redis, storage=storage, prefix=prefix)


@object_tag("!replicated-storage")
def load_replicated_storage(
    storages: list[StorageABC],
    replication_queue_size: int = 0,
    replication_threads: int = 1,
    read_replication: bool = True,
) -> ReplicatedStorage:
    """Generates :class:`buildgrid.server.cas.storage.replicated.ReplicatedStorage`
    using the tag ``!replicated-storage``.

    Usage
        .. code:: yaml

            - !replicated-storage
              storages:
                - &storageA
                - &storageB
              replication-queue-size: 10000
              replication-threads: 4
              read-replication: True


    Args:
        Storages (list): List of storages to mirror reads/writes for.
            A minimum of two storages is required.
        replication-queue-size (int): Length of the replication queue used
            to replicate inconsistent blobs found during FMB. If not present
            or set to 0 the replication queue is disabled (default 0).
        replication-threads (int): Number of threads to use for replication.
        read-replication (bool): If true replicate any missing blobs
            on BatchReadBlobs and Bytestream.Read calls. Defaults to true.
    """

    return ReplicatedStorage(
        storages=storages,
        replication_queue_size=replication_queue_size,
        replication_threadpool_size=replication_threads,
        read_replication=read_replication,
    )


@object_tag("!remote-storage")
def load_remote_storage(
    url: str,
    instance_name: str | None = None,
    credentials: ClientCredentials | None = None,
    channel_options: dict[str, Any] | None = None,
    retries: int = 3,
    max_backoff: int = 64,
    request_timeout: float | None = None,
) -> RemoteStorage:
    """Generates :class:`buildgrid.server.cas.storage.remote.RemoteStorage`
    using the tag ``!remote-storage``.

    Usage
        .. code:: yaml

            - !remote-storage
              url: https://storage:50052/
              instance-name: main
              credentials:
                tls-server-key: !expand-path ~/.config/buildgrid/server.key
                tls-server-cert: !expand-path ~/.config/buildgrid/server.cert
                tls-client-certs: !expand-path ~/.config/buildgrid/client.cert
                auth-token: /path/to/auth/token
                token-refresh-seconds: 6000
              channel-options:
                lb-policy-name: round_robin
              request-timeout: 15


    Args:
        url (str): URL to remote storage. If used with ``https``, needs credentials.
        instance_name (str): Instance of the remote to connect to. If none, defaults to the instance context.
        credentials (dict, optional): A dictionary in the form::

           tls-client-key: /path/to/client-key
           tls-client-cert: /path/to/client-cert
           tls-server-cert: /path/to/server-cert
           auth-token: /path/to/auth/token
           token-refresh-seconds (int): seconds to wait before reading the token from the file again

        channel-options (dict, optional): A dictionary of grpc channel options in the form::

          some-channel-option: channel_value
          other-channel-option: another-channel-value
        See https://github.com/grpc/grpc/blob/master/include/grpc/impl/codegen/grpc_types.h
        for the valid channel options
        retries (int): Max number of times to retry (default 3). Backoff between retries is about 2^(N-1),
            where N is the number of attempts
        max_backoff (int): Maximum backoff in seconds (default 64)
        request_timeout (float): gRPC request timeout in seconds (default None)
    """

    options_tuple: tuple[tuple[str, Any], ...] = ()
    if channel_options:
        # Transform the channel options into the format expected
        # by grpc channel creation
        parsed_options = []
        for option_name, option_value in channel_options.items():
            parsed_options.append((f"grpc.{option_name.replace('-', '_')}", option_value))
        options_tuple = tuple(parsed_options)

    if not _validate_url_and_credentials(url, credentials=credentials):
        sys.exit(-1)

    return RemoteStorage(
        remote=url,
        instance_name=instance_name,
        channel_options=options_tuple,
        credentials=credentials,
        retries=retries,
        max_backoff=max_backoff,
        request_timeout=request_timeout,
    )


@object_tag("!with-cache-storage")
def load_with_cache_storage(
    cache: StorageABC,
    fallback: StorageABC,
    defer_fallback_writes: bool = False,
    fallback_writer_threads: int = 20,
) -> WithCacheStorage:
    """Generates :class:`buildgrid.server.cas.storage.with_cache.WithCacheStorage`
    using the tag ``!with-cache-storage``.

    Usage
        .. code:: yaml

            - !with-cache-storage
              cache:
                !lru-storage
                size: 2048M
              fallback:
                !disk-storage
                path: /opt/bgd/cas-storage
              defer-fallback-writes: no

    Args:
        cache (StorageABC): Storage instance to use as a cache
        fallback (StorageABC): Storage instance to use as a fallback on
            cache misses
        defer-fallback-writes (bool): If true, `commit_write` returns once
            writing to the cache is done, and the write into the fallback
            storage is done in a background thread
        fallback-writer-threads (int): The maximum number of threads to use
            for writing blobs into the fallback storage. Defaults to 20.
    """

    return WithCacheStorage(
        cache,
        fallback,
        defer_fallback_writes=defer_fallback_writes,
        fallback_writer_threads=fallback_writer_threads,
    )


class ShardType(TypedDict):
    name: str
    storage: StorageABC


@object_tag("!sharded-storage")
def load_sharded_storage(shards: list[ShardType], thread_pool_size: int | None = None) -> ShardedStorage:
    """Generates :class:`buildgrid.server.cas.storage.Sharded.ShardedStorage`
    using the tag ``!sharded-storage``.

    Usage
        .. code:: yaml

            - !sharded-storage
              shards:
                - name: A
                  storage: &storageA
                - name: B
                  storage: !lru-storage
                    size: 2048M
              thread-pool-size: 40


    Args:
        shards (list): List of dictionaries. The dictionaries are expected to
            have ``name`` and ``storage`` keys defining a storage shard. The
            name must be unique within a configuration and should be the same
            for any configuration using the same underlying storage.
        thread-pool-size (int|None): Number of worker threads to use for bulk
            methods to allow parallel requests to each shard. If not set no
            threadpool is created and requests are made serially to each shard.
    """

    parsed_shards: dict[str, StorageABC] = {}
    for shard in shards:
        if shard["name"] in parsed_shards:
            click.echo(
                f"ERROR: Duplicate shard name '{shard['name']}'. Please fix the config.\n",
                err=True,
            )
            sys.exit(-1)
        parsed_shards[shard["name"]] = shard["storage"]
    return ShardedStorage(parsed_shards, thread_pool_size)


_SizeLimitedStorageConfig = TypedDict("_SizeLimitedStorageConfig", {"max-size": int, "storage": StorageABC})


@object_tag("!size-differentiated-storage")
def load_size_differentiated_storage(
    size_limited_storages: list[_SizeLimitedStorageConfig],
    fallback: StorageABC,
    thread_pool_size: int | None = None,
) -> SizeDifferentiatedStorage:
    """Generates :class:`buildgrid.server.cas.storage.size_differentiated.SizeDifferentiatedStorage`
    using the tag ``!size-differentiated-storage``.

    Usage
        .. code:: yaml

            - !size-differentiated-storage
              size-limited-storages:
                - max-size: 1M
                  storage:
                    !lru-storage
                    size: 2048M
              fallback:
                !disk-storage
                path: /opt/bgd/cas-storage
              thread-pool-size: 40

    Args:
        size_limited_storages (list): List of dictionaries. The dictionaries are expected
            to have ``max-size`` and ``storage`` keys, defining a storage provider to use
            to store blobs with size up to ``max-size``.
        fallback (StorageABC): Storage instance to use as a fallback for blobs which
            are too big for the options defined in ``size_limited_storages``.
        thread-pool-size (int|None): Number of worker threads to use for bulk
            methods to allow parallel requests to each storage. This thread pool
            is separate from the gRPC server thread-pool-size and should be tuned
            separately. If not set no threadpool is created and requests are made
            serially to each storage.
    """

    parsed_storages: list[SizeLimitedStorageType] = []
    for storage_config in size_limited_storages:
        parsed_storages.append(
            {"max_size": _parse_size(str(storage_config["max-size"])), "storage": storage_config["storage"]}
        )
    return SizeDifferentiatedStorage(parsed_storages, fallback, thread_pool_size)


@object_tag("!sql-storage")
def load_sql_storage(
    sql: SqlProvider,
    sql_ro: SqlProvider | None = None,
) -> SQLStorage:
    """Generates :class:`buildgrid.server.cas.storage.sql.SQLStorage`
    using the tag ``!sql-storage``.

    Usage
        .. code:: yaml

            - !sql-storage
              sql: *sql
              sql_ro: *sql
    Args:
        sql (:class:`buildgrid.server.sql.provider.SqlProvider`): A configured SQL
            connection manager. This must be an object with an ``!sql-connection`` YAML tag.
        sql_ro (:class:`buildgrid.server.sql.provider.SqlProvider`): Similar to `sql`,
            but used for readonly backend transactions.
            If set, it should be configured with a replica of main DB using an optional but
            encouraged readonly role. Permission check is not executed by BuildGrid.
            If not set, readonly transactions are executed by `sql` object.
    """

    return SQLStorage(sql, sql_ro_provider=sql_ro)


@object_tag("!sql-connection")
def load_sql_connection(
    connection_string: str | None = None,
    connection_timeout: int = 5,
    lock_timeout: int = 5,
    connect_args: dict[str, Any] | None = None,
    max_overflow: int | None = None,
    pool_pre_ping: bool | None = None,
    pool_recycle: int | None = None,
    pool_size: int | None = None,
    pool_timeout: int | None = None,
    name: str = "sql-provider",
) -> SqlProvider:
    """Generates :class:`buildgrid.server.sql.provider.SqlProvider` using the
    tag ``!sql-connection``.

    Example:
        .. code:: yaml

            - !sql-connection &sql
              connection-string: postgresql://bgd:insecure@database/bgd
              connection-timeout: 5
              lock-timeout: 5
              pool-size: 5
              pool-timeout: 30
              max-overflow: 10
              name: "sql-pool"

    """

    return SqlProvider(
        connection_string=connection_string,
        connection_timeout=connection_timeout,
        lock_timeout=lock_timeout,
        connect_args=connect_args,
        max_overflow=max_overflow,
        pool_pre_ping=pool_pre_ping,
        pool_recycle=pool_recycle,
        pool_size=pool_size,
        pool_timeout=pool_timeout,
        name=name,
    )


@object_tag(
    "!sql-scheduler",
    deprecated_keys={
        "property-keys": "Use a 'property-set' object instead. See '!dynamic-property-set'.",
        "wildcard-property-keys": "Use a 'property-set' object instead. See '!dynamic-property-set'.",
    },
)
def load_sql_scheduler(
    storage: StorageABC,
    sql: SqlProvider,
    sql_ro: SqlProvider | None = None,
    sql_notifier: SqlProvider | None = None,
    property_set: PropertySet | None = None,
    pruner_job_max_age: dict[str, float] | None = None,
    pruner_period: dict[str, float] | None = None,
    pruner_max_delete_window: int | None = None,
    queue_timeout_job_max_age: dict[str, float] | None = None,
    queue_timeout_period: dict[str, float] | None = None,
    queue_timeout_max_window: int | None = None,
    action_cache: ActionCacheABC | None = None,
    action_browser_url: str | None = None,
    max_execution_timeout: int = DEFAULT_MAX_EXECUTION_TIMEOUT,
    metering_service_client: metering.SyncMeteringServiceClient | None = None,
    metering_throttle_action: str | None = None,
    bot_session_keepalive_timeout: int = 600,
    logstream: dict[str, Any] | None = None,
    asset_client: AssetClient | None = None,
    queued_action_retention_hours: float | None = None,
    completed_action_retention_hours: float | None = None,
    action_result_retention_hours: float | None = None,
    max_job_attempts: int = 5,
    assigners: list[AssignerConfig] | None = None,
    poll_interval: float = 1.0,
    max_queue_size: int | None = None,
    execution_timer_interval: float = 60.0,
    session_expiry_timer_interval: float = 10.0,
    instance_pools: list[list[str]] | None = None,
    bot_locality_hint_limit: int = 10,
    # Deprecated values:
    property_keys: str | list[str] | None = None,
    wildcard_property_keys: str | list[str] | None = None,
    priority_assignment_percentage: int | None = None,
    job_assignment_interval: float | None = None,
    bot_poll_interval: float = 1.0,
) -> Scheduler:
    """Generates :class:`buildgrid.server.scheduler.Scheduler` using
    the tag ``!sql-scheduler``.

    Example:

        .. code:: yaml

            - !sql-scheduler
              storage: *cas-storage
              sql: *sql
              pruner-job-max-age:
                days: 90

        This usage example assumes that the ``cas-storage`` reference refers to a
        storage backend, eg. ``!disk-storage``, and the ``sql`` reference refers
        to an SQL connection manager using ``!sql-connection``.

    Args:

        storage(:class:`buildgrid.server.cas.storage.storage_abc.StorageABC`): Instance
            of storage to use for getting actions and storing job results. This must be
            an object constructed using a YAML tag ending in ``-storage``, for example
            ``!disk-storage``.

        sql (:class:`buildgrid.server.sql.provider.SqlProvider`): A configured SQL
            connection manager. This must be an object with an ``!sql-connection`` YAML tag.

        sql_ro (:class:`buildgrid.server.sql.provider.SqlProvider`): Similar to `sql`,
            but used for readonly backend transactions.
            If set, it should be configured with a replica of main DB using an optional but
            encouraged readonly role. Permission check is not executed by BuildGrid.
            If not set, readonly transactions are executed by `sql` object.

        sql_notifier (:class:`buildgrid.server.sql.provider.SqlProvider`): Similar to `sql`,
            but used for operation notifier.
            If not set, transactions are executed by `sql` object.

        property_set (PropertySet): Controls how execute requests are assigned to workers.

        pruner_job_max_age (dict): Allow the storage to remove old entries by specifying the
            maximum amount of time that a row should be kept after its job finished. If
            this value is None, pruning is disabled and the background pruning thread
            is never created.

        pruner_period (dict): How often to attempt to remove old entries. If pruning
            is enabled (see above) and this value is None, it is set to 5 minutes by default.

        pruner_max_delete_window (int): Maximum number of records removed in a single
            cleanup pass. If pruning is enabled and this value is None, it is set to 10000
            by default. This allows to put a limit on the time that the database
            will be blocked on a single invocation of the cleanup routine.
            (A smaller value reduces the performance impact of removing entries,
            but makes the recovery of storage space slower.)

        queue_timeout_job_max_age (dict): If set, allow storage to abort jobs that have been queued
            for a long period of time.

        queue_timeout_period (dict): How often to find aged queued jobs. If not set,
            default to 5 minutes.

        queue_timeout_max_window (int): Maximum number of jobs to timeout per batch.
            If not set, default to 10000.

        action_cache (:class:`ActionCache`): Instance of action cache to use.

        action_browser_url (str): The base URL to use to generate Action Browser links to users.
            If a single Web interface serves several Buildgrid installations then this URL
            should include the namespace configured for the current Buildgrid installation,
            see https://gitlab.com/BuildGrid/bgd-browser#multi-buildgrid-setup.

        max_execution_timeout (int): The maximum time jobs are allowed to be in
            'OperationStage.EXECUTING'. This is a periodic check.
            When this time is exceeded in executing stage, the job will be cancelled.

        metering_service_client: Optional client to check whether resource usage of a client
            is above a predefined threshold

        metering_throttle_action: The action to perform when metering service returns that job should
            be throttled. Can be set to "deprioritize" or "reject". Defaults to "deprioritize".

        bot_session_keepalive_timeout (int): The longest time (in seconds) we'll wait
            for a bot to send an update before it assumes it's dead. Defaults to 600s
            (10 minutes).

        logstream (Dict): Configuration options for connecting a logstream instance to ongoing
            jobs. Is a dict with items "url", "credentials", and "instance-name"

        asset_client (AssetClient | None): Client of remote-asset service

        queued_action_retention_hours (float | None): Minimum retention for queued actions in hours

        completed_action_retention_hours (float | None): Minimum retention for completed actions in hours

        action_result_retention_hours (float | None): Minimum retention for action results in hours

        max_job_attempts (int): The number of times a job will be assigned to workers before marking
            the job failed. Reassignment happens when a worker fails to report the outcome of a job.
            Minimum value allowed is 1. Default value is 5.

        assigners (list[AssignerConfig]): A list of job assigner configurations for this scheduler.

        poll_interval (float): Duration to wait between polling operation updates.

        max_queue_size (int): Maximum number of jobs queued per platform property set.

        execution_timer_interval (float): Duration to wait between attempts to executions
            exceeding timeout.

        session_expiry_timer_interval (float): Duration to wait between attempts to close unresponsive
            bot sessions

        instance_pools (list[list[str]] | None): List of lists of instance names to schedule together

        bot_locality_hint_limit (int): The maximum number of job locality hints to be associated with
            each bot

        bot_poll_interval (float): Duration to wait between bot polls for new jobs.

        property_keys (list): Deprecated. Use a property_set instead.
        wildcard_property_keys (list): Deprecated. Use a property_set instead.
        priority_assignment_percentage (int): Deprecated. Use assigners instead.
        job_assignment_interval (float): Deprecated. Use assigners instead.
    """

    click.echo(
        f"SQLScheduler: storage={type(storage).__name__}, "
        f"pruner_job_max_age={pruner_job_max_age}, "
        f"pruner_period={pruner_period}, "
        f"pruner_max_delete_window={pruner_max_delete_window}"
    )
    click.echo(click.style("Creating an SQL scheduler backend\n", fg="green", bold=True))

    if bot_session_keepalive_timeout <= 0:
        msg = f"ERROR: bot_session_keepalive_timeout must be greater than zero: {bot_session_keepalive_timeout}"
        click.echo(click.style(msg, fg="red", bold=True), err=True)
        sys.exit(-1)

    if max_job_attempts < 1:
        msg = f"ERROR: max_job_attempts must be greater than zero: {max_job_attempts}"
        click.echo(click.style(msg, fg="red", bold=True), err=True)
        sys.exit(-1)

    if instance_pools:
        instance_counts: dict[str, int] = defaultdict(int)
        for pool in instance_pools:
            for instance_name in pool:
                instance_counts[instance_name] += 1
        for instance_name, count in instance_counts.items():
            if count > 1:
                msg = f"ERROR: Instance name '{instance_name}' appears in multiple pools"
                click.echo(click.style(msg, fg="red", bold=True), err=True)
                sys.exit(-1)

    try:
        if property_set is None:
            if isinstance(property_keys, str):
                property_keys = [property_keys]
            if isinstance(wildcard_property_keys, str):
                wildcard_property_keys = [wildcard_property_keys]

            property_set = load_dynamic_property_set(
                match_property_keys=property_keys,
                wildcard_property_keys=wildcard_property_keys,
            )

        pruning_options = (
            AgedJobHandlerOptions.from_config(pruner_job_max_age, pruner_period, pruner_max_delete_window)
            if pruner_job_max_age
            else None
        )
        queue_timeout_options = (
            AgedJobHandlerOptions.from_config(
                queue_timeout_job_max_age, queue_timeout_period, queue_timeout_max_window
            )
            if queue_timeout_job_max_age
            else None
        )

        sql_ro = sql_ro or sql
        sql_notifier = sql_notifier or sql

        logstream_url, logstream_credentials, logstream_instance = get_logstream_connection_info(logstream)
        logstream_channel: grpc.Channel | None = None
        if logstream_url is not None:
            logstream_credentials = logstream_credentials or {}
            logstream_channel, _ = setup_channel(
                logstream_url,
                auth_token=None,
                client_key=logstream_credentials.get("tls-client-key"),
                client_cert=logstream_credentials.get("tls-client-cert"),
                server_cert=logstream_credentials.get("tls-server-cert"),
            )

        # TODO: Drop this fallback after a migration period
        if assigners is not None:
            if priority_assignment_percentage is not None:
                msg = "ERROR: Setting both `assigners` and `priority_assignment_percentage` is forbidden."
                click.echo(click.style(msg, fg="red", bold=True), err=True)
                sys.exit(-1)
            if job_assignment_interval is not None:
                msg = "ERROR: Setting both `assigners` and `job_assignment_interval` is forbidden."
                click.echo(click.style(msg, fg="red", bold=True), err=True)
                sys.exit(-1)
        else:
            # Deprecated old-style config, warn and auto-generate a basic
            # assigner configuration to match old behaviour.
            if priority_assignment_percentage is None:
                priority_assignment_percentage = 100
            assigners = [
                PriorityAgeAssignerConfig(
                    name="PriorityAgeAssigner",
                    count=1,
                    interval=job_assignment_interval or 1,
                    priority_assignment_percentage=priority_assignment_percentage,
                )
            ]

        return Scheduler(
            sql,
            storage,
            property_set=property_set,
            pruning_options=pruning_options,
            queue_timeout_options=queue_timeout_options,
            sql_ro_provider=sql_ro,
            sql_notifier_provider=sql_notifier,
            action_cache=action_cache,
            action_browser_url=action_browser_url,
            max_execution_timeout=max_execution_timeout,
            metering_client=metering_service_client,
            metering_throttle_action=(
                MeteringThrottleAction(metering_throttle_action)
                if metering_throttle_action
                else MeteringThrottleAction.DEPRIORITIZE
            ),
            bot_session_keepalive_timeout=bot_session_keepalive_timeout,
            logstream_channel=logstream_channel,
            logstream_instance=logstream_instance,
            asset_client=asset_client,
            queued_action_retention_hours=queued_action_retention_hours,
            completed_action_retention_hours=completed_action_retention_hours,
            action_result_retention_hours=action_result_retention_hours,
            assigner_configs=assigners,
            poll_interval=poll_interval,
            max_queue_size=max_queue_size,
            execution_timer_interval=execution_timer_interval,
            session_expiry_timer_interval=session_expiry_timer_interval,
            instance_pools=instance_pools,
            bot_locality_hint_limit=bot_locality_hint_limit,
            bot_poll_interval=bot_poll_interval,
        )

    except TypeError as type_error:
        click.echo(type_error, err=True)
        sys.exit(-1)


@object_tag("!priority-age-assigner")
def load_priority_age_assigner(
    count: int = 1,
    interval: float = 1.0,
    priority_assignment_percentage: int = 100,
    failure_backoff: float = 5.0,
    jitter_factor: float = 1.0,
    busy_sleep_factor: float = 0.01,
    instance_names: list[str] | None = None,
    bot_assignment_strategy: BotAssignmentStrategy = AssignByCapacity(),
    name: str | None = None,
) -> PriorityAgeAssignerConfig:
    """Configuration for a set of priority-order job assignment threads in a scheduler.

    Args:
        count (int): The number of assigner threads with this configuration to run concurrently.

        interval (float): The time to wait between each assignment attempt, in seconds.

        priority_assignment_percentage (int): The percentage of assignment attempts that should
            use priority order. The remaining assignment attempts will attempt to assign jobs in
            oldest-first order, to mitigate queue starvation.

        failure_backoff (float): The time to wait between assignment attempts of the same job.
            Setting this to 0 will cause unassignable jobs to block the queue.

        jitter_factor (float): Extra jitter to apply to the assignment interval.

        busy_sleep_factor (float): The factor to multiply the assignment interval by when the
            assigner is busy.

        instance_names (list[str] | None): A list of instance names to assign jobs for.
            If None, the assigner will assign jobs for all instances.

        bot_assignment_strategy (BotAssignmentStrategy): The strategy to use for finding a bot to assign the job to.
    """
    instance_set = None
    if instance_names is not None:
        instance_set = frozenset(instance_names)
    return PriorityAgeAssignerConfig(
        name or "PriorityAgeAssigner",
        count,
        interval,
        priority_assignment_percentage,
        failure_backoff,
        jitter_factor,
        busy_sleep_factor,
        instance_names=instance_set,
        bot_assignment_strategy=bot_assignment_strategy,
    )


@object_tag("!sampling-config")
def load_sampling_config(sample_size: int, max_attempts: int = 1) -> SamplingConfig:
    """Configuration for sampling bots when assigning a job.

    Args:
        sample_size (int): The number of bots to sample when assigning a job.
        max_attempts (int): The maximum number of attempts to sample bots.
    """

    return SamplingConfig(sample_size=sample_size, max_attempts=max_attempts)


@object_tag("!assign-by-capacity")
def load_assign_by_capacity_strategy(sampling: SamplingConfig | None = None) -> BotAssignmentStrategy:
    """Configuration for a job assigner that assigns jobs to workers based on their capacity.

    Args:
        sampling (SamplingConfig | None): Optional configuration for sampling bots when assigning a job.
            If None, no sampling is performed.
    """
    return AssignByCapacity(sampling=sampling)


@object_tag("!assign-by-locality")
def load_assign_by_locality_strategy(
    sampling: SamplingConfig | None = None, fallback: BotAssignmentStrategy = AssignByCapacity()
) -> BotAssignmentStrategy:
    """Configuration for a job assigner that assigns jobs to workers based on their locality hints.

    Args:
        sampling (SamplingConfig | None): Optional configuration for sampling bots when assigning a job.
            If None, no sampling is performed.
        fallback (BotAssignmentStrategy): The strategy to use when no bot with the locality hint is available.
    """
    return AssignByLocality(sampling=sampling, fallback=fallback)


@object_tag("!dynamic-property-set")
def load_dynamic_property_set(
    unique_property_keys: Iterable[str] | None = None,
    match_property_keys: Iterable[str] | None = None,
    wildcard_property_keys: Iterable[str] | None = None,
    label_key: str | None = None,
) -> DynamicPropertySet:
    """
    A dynamic property set allows scheduling jobs which may have unset values for properties.
    Dynamic queues can be flexible as they allow minimal configuration to add new properties,
    however, they have an exponential cost to scheduling. Using many different properties
    can lead to very slow scheduling rates.

    Args:
        unique_property_keys(set[str]): Properties which may only be set once.
            OSFamily is always considered unique.
        match_property_keys(set[str]): Properties which must match on the worker and execute request.
            OSFamily and ISA property keys are always added as match keys even if unlisted.
        wildcard_property_keys(set[str]): Properties which are available to workers, but not used for scheduling.
        label_key(str): A key used to identify job types in logging and metrics.
            Defaults to OSFamily
    """

    match_property_keys = set(match_property_keys or [])
    match_property_keys.update(DEFAULT_PLATFORM_PROPERTY_KEYS)

    unique_property_keys = set(unique_property_keys or [])
    unique_property_keys.add("OSFamily")

    wildcard_property_keys = set(wildcard_property_keys or [])

    label_key = label_key or "OSFamily"

    return DynamicPropertySet(
        unique_property_keys=unique_property_keys,
        match_property_keys=match_property_keys,
        wildcard_property_keys=wildcard_property_keys,
        label_key=label_key,
    )


_Properties = list[tuple[str, str]]


class _PropertyLabel(TypedDict):
    label: str
    properties: _Properties


@object_tag("!static-property-set")
def load_static_property_set(
    property_labels: list[_PropertyLabel],
    wildcard_property_keys: list[str] | None = None,
) -> StaticPropertySet:
    """
    A static property set allows scheduling jobs by resolving sane defaults for unspecified keys.
    Static queues can be more verbose as you require defining all sets of valid properties,
    however, they have a linear cost to scheduling. Using many different properties
    becomes less expensive to calculate assignment.

    Args:
        property_labels(list[_PropertyLabel]): Properties combinations which are allowed.
        wildcard_property_keys(list[str]): Properties which are available to workers, but not used for scheduling.
    """

    if wildcard_property_keys is None:
        wildcard_property_keys = []

    return StaticPropertySet(
        property_labels=[
            PropertyLabel(
                label=label["label"],
                properties={(k, v) for [k, v] in label["properties"]},
            )
            for label in property_labels
        ],
        wildcard_property_keys=set(wildcard_property_keys),
    )


@object_tag("!sql-index")
def load_sql_index(
    storage: StorageABC,
    sql: SqlProvider,
    window_size: int = 1000,
    inclause_limit: int = -1,
    fallback_on_get: bool = False,
    max_inline_blob_size: int = 0,
    refresh_accesstime_older_than: int = 0,
) -> SQLIndex:
    """Generates :class:`buildgrid.server.cas.storage.index.sql.SQLIndex`
    using the tag ``!sql-index``.

    Usage
        .. code:: yaml

            - !sql-index
              # This assumes that a storage instance is defined elsewhere
              # with a `&cas-storage` anchor
              storage: *cas-storage
              sql: *sql
              window-size: 1000
              inclause-limit: -1
              fallback-on-get: no
              max-inline-blob-size: 256
              refresh-accesstime-older-than: 0

    Args:
        storage(:class:`buildgrid.server.cas.storage.storage_abc.StorageABC`):
            Instance of storage to use. This must be a storage object constructed using
            a YAML tag ending in ``-storage``, for example ``!disk-storage``.
        window_size (uint): Maximum number of blobs to fetch in one SQL operation
            (larger resultsets will be automatically split into multiple queries)
        inclause_limit (int): If nonnegative, overrides the default number of variables
            permitted per "in" clause. See the buildgrid.server.cas.storage.index.sql.SQLIndex
            comments for more details.
        fallback_on_get (bool): By default, the SQL Index only fetches blobs from the
            underlying storage if they're present in the index on ``get_blob``/``bulk_read_blobs``
            requests to minimize interactions with the storage. If this is set, the index
            instead checks the underlying storage directly on ``get_blob``/``bulk_read_blobs``
            requests, then loads all blobs found into the index.
        max_inline_blob_size (int): Blobs of this size or smaller are stored directly in the index
            and not in the backing storage (must be nonnegative).
        refresh-accesstime-older-than (int): When reading a blob, its access timestamp will not be
            updated if the current time is not at least refresh-accesstime-older-than seconds newer
            than the access timestamp. Set this to reduce load associated with frequent timestamp updates.
    """

    storage_type = type(storage).__name__
    click.echo(
        f"SQLIndex: storage={storage_type}, "
        f"window_size={window_size}, "
        f"inclause_limit={inclause_limit}, "
        f"fallback_on_get={fallback_on_get}"
    )
    click.echo(click.style(f"Creating an SQL CAS Index for {storage_type}\n", fg="green", bold=True))
    return SQLIndex(
        sql,
        storage,
        window_size=window_size,
        inclause_limit=inclause_limit,
        fallback_on_get=fallback_on_get,
        max_inline_blob_size=max_inline_blob_size,
        refresh_accesstime_older_than=refresh_accesstime_older_than,
    )


@object_tag("!execution")
def load_execution_controller(
    scheduler: Scheduler,
    operation_stream_keepalive_timeout: int = 600,
    endpoints: Sequence[str] = ServiceName.default_services(),
    max_list_operations_page_size: int = DEFAULT_MAX_LIST_OPERATION_PAGE_SIZE,
) -> ExecutionController:
    """Generates :class:`buildgrid.server.execution.service.ExecutionService`
    using the tag ``!execution``.

    Usage
        .. code:: yaml

            # This assumes that the YAML anchors are defined elsewhere
            - !execution
              scheduler: *state-database
              operation-stream-keepalive-timeout: 600
              endpoints:
                - execution
                - operations
                - bots
              max-list-operations-page-size: 1000

    Args:
        scheduler(:class:`Scheduler`): Instance of scheduler to use for the scheduler's state.
        operation_stream_keepalive_timeout (int): The longest time (in seconds)
            we'll wait before sending the current status in an Operation response
            stream of an `Execute` or `WaitExecution` request. Defaults to 600s
            (10 minutes).
        endpoints (list): List of service/endpoint types to enable. Possible services are
            ``execution``, ``operations``, and ``bots``. By default all three are enabled.
        max_list_operations_page_size (int): The maximum number of operations that can
            be returned in a ListOperations response. A page token will be returned
            with the response to allow the client to get the next page of results.
    """

    click.echo(click.style(f"Creating a Execution service using {type(scheduler).__name__}\n", fg="green", bold=True))

    return ExecutionController(
        scheduler,
        operation_stream_keepalive_timeout=operation_stream_keepalive_timeout,
        services=endpoints,
        max_list_operations_page_size=max_list_operations_page_size,
    )


@object_tag("!bots")
def load_bots_controller(scheduler: Scheduler) -> BotsInterface:
    """Generates :class:`buildgrid.server.bots.instance.BotsInterface`
    using the tag ``!bots``.

    Usage
        .. code:: yaml

            # This assumes that the YAML anchors are defined elsewhere
            - !bots
              scheduler: *state-database

    Args:
        scheduler(:class:`Scheduler`): Instance of scheduler to use for the scheduler's state.
    """

    click.echo(click.style(f"Creating a Bots service using {type(scheduler).__name__}\n", fg="green", bold=True))
    return BotsInterface(scheduler)


@object_tag("!action-cache")
def load_action_cache_controller(cache: ActionCacheABC) -> ActionCache:
    """Generates :class:`buildgrid.server.actioncache.service.ActionCacheService`
    using the tag ``!action-cache``.

    Usage
        .. code:: yaml

            # This assumes that the YAML anchors are defined elsewhere
            - !action-cache
              cache: *lru-cache

    Args:
        cache (ActionCacheABC): The ActionCache backend to use for this cache.

    """

    click.echo(click.style(f"Creating a Action Cache service using {type(cache).__name__}\n", fg="green", bold=True))
    return ActionCache(cache)


@object_tag("!mirrored-action-cache")
def load_mirrored_action_cache(first: ActionCacheABC, second: ActionCacheABC) -> MirroredCache:
    """Generates:class:`buildgrid.server.actioncache.caches.mirrored_cache.MirroredCache`
    using the tag ``!mirrored-action-cache``.

    Usage
        .. code:: yaml

            # This assumes that the YAML anchors are defined elsewhere
            - !mirrored-action-cache
              first: *first-action-cache
              second: *second-action-cache
    """

    return MirroredCache(first=first, second=second)


@object_tag("!with-cache-action-cache")
def load_with_cache_action_cache(
    cache: ActionCacheABC,
    fallback: ActionCacheABC,
    allow_updates: bool = True,
    cache_failed_actions: bool = True,
) -> WithCacheActionCache:
    """Generates:class:`buildgrid.server.actioncache.caches.with_cache.WithCacheActionCache`
    using the tag ``!with-cache-action-cache``.

    Usage
        .. code:: yaml

            # This assumes that the YAML anchors are defined elsewhere
            - !with-cache-action-cache
              storage: *cas-storage
              cache: *cache-ac
              fallback: *fallback-ac

    Args:
        cache (ActionCacheABC): ActionCache instance to use as a local cache
        fallback (ActionCacheABC): ActionCache instance to use as a fallback on
            local cache misses
        allow_updates(bool): Allow updates pushed to the Action Cache.
            Defaults to ``True``.
        cache_failed_actions(bool): Whether to store failed (non-zero exit
            code) actions. Default to ``True``.
    """

    return WithCacheActionCache(
        cache, fallback, allow_updates=allow_updates, cache_failed_actions=cache_failed_actions
    )


@object_tag("!lru-action-cache")
def load_lru_action_cache(
    storage: StorageABC,
    max_cached_refs: int,
    allow_updates: bool = True,
    cache_failed_actions: bool = True,
) -> LruActionCache:
    """Generates :class:`buildgrid.server.actioncache.caches.lru_cache.LruActionCache`
    using the tag ``!lru-action-cache``.

    Usage
        .. code:: yaml

            # This assumes that the YAML anchors are defined elsewhere
            - !lru-action-cache
              storage: *cas-storage
              max-cached-refs: 1024
              cache-failed-actions: yes
              allow-updates: yes

    Args:
        storage(:class:`buildgrid.server.cas.storage.storage_abc.StorageABC`):
            Instance of storage to use.
        max_cached_refs(int): Max number of cached actions.
        allow_updates(bool): Allow updates pushed to the Action Cache.
            Defaults to ``True``.
        cache_failed_actions(bool): Whether to store failed (non-zero exit
            code) actions. Default to ``True``.

    """

    storage_type = type(storage).__name__
    click.echo(
        f"LruActionCache: storage={storage_type}, max_cached_refs={max_cached_refs}, "
        f"allow_updates={allow_updates}, cache_failed_actions={cache_failed_actions}"
    )
    click.echo(click.style(f"Creating an LruActionCache using `{storage_type}` storage\n", fg="green", bold=True))
    return LruActionCache(storage, max_cached_refs, allow_updates, cache_failed_actions)


@object_tag("!s3action-cache")
def load_s3_action_cache(
    storage: StorageABC,
    allow_updates: bool = True,
    cache_failed_actions: bool = True,
    entry_type: str | None = None,
    migrate_entries: bool | None = False,
    bucket: str | None = None,
    endpoint: str | None = None,
    access_key: str | None = None,
    secret_key: str | None = None,
    cache_key_salt: str | None = None,
) -> S3ActionCache:
    """Generates :class:`buildgrid.server.actioncache.caches.s3_cache.S3ActionCache`
    using the tag ``!s3action-cache``.

    Usage
        .. code:: yaml

            # This assumes that the YAML anchors are defined elsewhere
            - !s3action-cache
              storage: *cas-storage
              allow-updates: yes
              cache-failed-actions: yes
              entry-type: action-result-digest
              migrate-entries: no
              bucket: bgd-action-cache
              endpoint: http://localhost:9000/
              access-key: !read-file /var/bgd/s3-access-key
              secret-key: !read-file /var/bgd/s3-secret-key

    Args:
        storage(:class:`buildgrid.server.cas.storage.storage_abc.StorageABC`):
            Instance of storage to use. This must be an object constructed using
            a YAML tag ending in ``-storage``, for example ``!disk-storage``.
        allow_updates(bool): Allow updates pushed to the Action Cache.
            Defaults to ``True``.
        cache_failed_actions(bool): Whether to store failed (non-zero exit code)
            actions. Default to ``True``.
        entry_type (str): whether entries in S3 will store an ``'action-result'``
            or an ``'action-result-digest'`` (default).
        migrate_entries (bool): Whether to automatically update the values of
            entries that contain a different type of value to `entry_type` as
            they are queried. Default to ``False``.
        bucket (str): Name of bucket
        endpoint (str): URL of endpoint.
        access-key (str): S3-ACCESS-KEY
        secret-key (str): S3-SECRET-KEY
        cache_key_salt (str): Optional salt to use in S3 keys. Instances with
            the same salt will share cache contents.

    """

    storage_type = type(storage).__name__
    cache_entry_type = None

    if entry_type is None or entry_type.lower() == "action-result-digest":
        cache_entry_type = ActionCacheEntryType.ACTION_RESULT_DIGEST
    elif entry_type.lower() == "action-result":
        cache_entry_type = ActionCacheEntryType.ACTION_RESULT
    else:
        click.echo(
            click.style(f"ERROR: entry_type value is not valid: {cache_entry_type}", fg="red", bold=True), err=True
        )
        sys.exit(-1)

    click.echo(
        f"S3ActionCache: storage={storage_type}, allow_updates={allow_updates}, "
        f"cache_failed_actions={cache_failed_actions}, bucket={bucket}, "
        f"entry_type={entry_type}, migrate_entries={migrate_entries}, "
        f"endpoint={endpoint}"
    )
    click.echo(
        click.style(f"Creating an S3ActionCache service using `{storage_type}` storage\n", fg="green", bold=True)
    )

    from botocore.config import Config as BotoConfig  # pylint: disable=import-outside-toplevel

    boto_config = BotoConfig(
        user_agent=S3_USERAGENT_NAME,
        connect_timeout=S3_TIMEOUT_CONNECT,
        read_timeout=S3_TIMEOUT_READ,
        retries={"max_attempts": S3_MAX_RETRIES},
    )

    return S3ActionCache(
        storage,
        allow_updates=allow_updates,
        cache_failed_actions=cache_failed_actions,
        entry_type=cache_entry_type,
        migrate_entries=migrate_entries,
        bucket=bucket,
        endpoint_url=endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        config=boto_config,
        cache_key_salt=cache_key_salt,
    )


@object_tag("!remote-action-cache")
def load_remote_action_cache(
    url: str,
    instance_name: str | None = None,
    retries: int = 3,
    max_backoff: int = 64,
    request_timeout: float | None = None,
    credentials: ClientCredentials | None = None,
    channel_options: dict[str, Any] | None = None,
) -> RemoteActionCache:
    """Generates :class:`buildgrid.server.actioncache.caches.remote.RemoteActionCache`
    using the tag ``!remote-action-cache``.

    Usage
        .. code:: yaml

            - !remote-action-cache
              url: https://action-cache:50053
              instance-name: main
              credentials:
                tls-server-key: !expand-path ~/.config/buildgrid/server.key
                tls-server-cert: !expand-path ~/.config/buildgrid/server.cert
                tls-client-certs: !expand-path ~/.config/buildgrid/client.cert
                auth-token: /path/to/auth/token
                token-refresh-seconds: 6000
              channel-options:
                lb-policy-name: round_robin

    Args:
        url (str): URL to remote action cache
        instance_name (str | None): Instance of the remote to connect to.
            Defaults to the instance context if none.
        credentials (dict, optional): A dictionary in the form::

           tls-client-key: /path/to/client-key
           tls-client-cert: /path/to/client-cert
           tls-server-cert: /path/to/server-cert
           auth-token: /path/to/auth/token
           token-refresh-seconds (int): seconds to wait before reading the token from the file again

        channel-options (dict, optional): A dictionary of grpc channel options in the form::

          some-channel-option: channel_value
          other-channel-option: another-channel-value
        See https://github.com/grpc/grpc/blob/master/include/grpc/impl/codegen/grpc_types.h
        for the valid channel options

    """

    options_tuple: tuple[tuple[str, Any], ...] = ()
    if channel_options:
        # Transform the channel options into the format expected
        # by grpc channel creation
        parsed_options = []
        for option_name, option_value in channel_options.items():
            parsed_options.append((f"grpc.{option_name.replace('-', '_')}", option_value))
        options_tuple = tuple(parsed_options)

    if not _validate_url_and_credentials(url, credentials=credentials):
        sys.exit(-1)

    click.echo(f"RemoteActionCache: url={url}, instance_name={instance_name}, ")
    click.echo(click.style(f"Creating an RemoteActionCache service for {url}\n", fg="green", bold=True))

    return RemoteActionCache(
        url,
        instance_name,
        retries,
        max_backoff,
        request_timeout,
        channel_options=options_tuple,
        credentials=credentials,
    )


@object_tag("!write-once-action-cache")
def load_write_once_action_cache(action_cache: ActionCacheABC) -> WriteOnceActionCache:
    """Generates :class:`buildgrid.server.actioncache.caches.write_once_cache.WriteOnceActionCache`
    using the tag ``!write-once-action-cache``.

    This allows a single update for a given key, essentially making it possible
    to create immutable ActionCache entries, rather than making the cache read-only
    as the ``allow-updates`` property of other ActionCache implementations does.

    Usage
        .. code:: yaml

            # This assumes that the YAML anchors are defined elsewhere
            - !write-once-action-cache
              action-cache: *remote-cache

    Args:
        action_cache (ActionCache): The action cache instance to make immutable.

    """

    return WriteOnceActionCache(action_cache)


@object_tag("!redis-action-cache")
def load_redis_action_cache(
    storage: StorageABC,
    # Should be RedisProvider, but we are trying to avoid a global dependency on redis.
    # Parser should have validated this already and we assert below
    redis: Any,
    allow_updates: bool = True,
    cache_failed_actions: bool = True,
    entry_type: str | None = None,
    migrate_entries: bool | None = False,
    cache_key_salt: str | None = None,
) -> "RedisActionCache":
    """Generates :class:`buildgrid.server.actioncache.caches.redis_cache.RedisActionCache`
    using the tag ``!redis-action-cache``.

    This creates an Action Cache which stores the mapping from Action digests to
    ActionResults in Redis.

    Usage
        .. code:: yaml

            # This assumes that the YAML anchors are defined elsewhere
            - !redis-action-cache
              storage: *cas-storage
              allow-updates: yes
              cache-failed-actions: yes
              entry-type: action-result-digest
              migrate-entries: no
              redis: *redis-connection

    Args:
        storage(:class:`buildgrid.server.cas.storage.storage_abc.StorageABC`):
            Instance of storage to use. This must be an object constructed using
            a YAML tag ending in ``-storage``, for example ``!disk-storage``.
        allow_updates(bool): Allow updates pushed to the Action Cache.
            Defaults to ``True``.
        cache_failed_actions(bool): Whether to store failed (non-zero exit code)
            actions. Default to ``True``.
        entry_type (str): whether entries in Redis will store an ``'action-result'``
            or an ``'action-result-digest'`` (default).
        migrate_entries (bool): Whether to automatically update the values of
            entries that contain a different type of value to `entry_type` as
            they are queried. Default to ``False``.
        redis (:class:`buildgrid.server.redis.provider.RedisProvider`): A configured Redis
            connection manager. This must be an object with an ``!redis-connection`` YAML tag.
        cache_key_salt (str): Optional salt to use in Redis keys. Instances with the same salt
            will share cache contents.
    """

    cache_entry_type = None
    if entry_type is None or entry_type.lower() == "action-result-digest":
        cache_entry_type = ActionCacheEntryType.ACTION_RESULT_DIGEST
    elif entry_type.lower() == "action-result":
        cache_entry_type = ActionCacheEntryType.ACTION_RESULT
    else:
        click.echo(
            click.style(f"ERROR: entry_type value is not valid: {cache_entry_type}", fg="red", bold=True), err=True
        )
        sys.exit(-1)
    # Import here so there is no global buildgrid dependency on redis
    from buildgrid.server.actioncache.caches.redis_cache import RedisActionCache
    from buildgrid.server.redis.provider import RedisProvider

    try:
        assert isinstance(redis, RedisProvider)
        return RedisActionCache(
            storage,
            redis,
            allow_updates=allow_updates,
            cache_failed_actions=cache_failed_actions,
            entry_type=cache_entry_type,
            migrate_entries=migrate_entries,
            cache_key_salt=cache_key_salt,
        )
    except Exception as e:
        click.echo(click.style(f"ERROR: {e},", fg="red", bold=True), err=True)
        sys.exit(-1)


class ActionCacheShardType(TypedDict):
    name: str
    cache: ActionCacheABC


@object_tag("!sharded-action-cache")
def load_sharded_action_cache(
    shards: list[ActionCacheShardType],
    allow_updates: bool = True,
    cache_failed_actions: bool = True,
    cache_key_salt: str | None = None,
) -> ShardedActionCache:
    """Generates:class:`buildgrid.server.actioncache.caches.sharded_cache.ShardedActionCache`
    using the tag ``!sharded-action-cache``.

    This creates an Action Cache whose contents are split among multiple child caches.

    Usage
        .. code:: yaml

            # This assumes that the YAML anchors are defined elsewhere
            - !sharded-action-cache
              shards:
                - name: a
                  cache:
                    !lru-action-cache
                    storage: *cas-storage
                    max-cached-refs: 1024
                    cache-failed-actions: yes
                    allow-updates: yes
                - name: b
                  cache:
                    !lru-action-cache
                    storage: *cas-storage
                    max-cached-refs: 1024
                    cache-failed-actions: yes
                    allow-updates: yes
              allow-updates: yes
              cache-failed-actions: no

    Args:
        shards (list[ActionCacheShardType]): List of shards. Shards are defined as
            dictionaries with a ``name`` and ``cache``. Shard names must be unique
            per Sharded Action Cache.

        allow_updates (bool): Allow updates to be pushed to the Action Cache.
            Both this and the shards' ``allow_updates`` settings must be ``True``
            to allow updates. Defaults to ``True``.

        cache_failed_actions (bool): Whether to store failed (non-zero exit
            code) actions. Both this and the shards' ``cache_failed_actions`` settings
            must be ``True`` to enable caching of failed actions. Default to ``True``.

        cache_key_salt (str): Optional salt to use in shard key calculation. Instances
            with the same salt will map the same digest to the same shard name.

    """
    parsed_shards = {}
    for shard in shards:
        if shard["name"] in parsed_shards:
            click.echo(
                f"ERROR: Duplicate shard name '{shard['name']}'. Please fix the config.\n",
                err=True,
            )
            sys.exit(-1)
        parsed_shards[shard["name"]] = shard["cache"]
    return ShardedActionCache(
        parsed_shards,
        allow_updates=allow_updates,
        cache_failed_actions=cache_failed_actions,
        cache_key_salt=cache_key_salt,
    )


@object_tag("!cas")
def load_cas_controller(
    storage: StorageABC,
    read_only: bool = False,
    tree_cache_size: int | None = None,
    tree_cache_ttl_minutes: float = 60,
) -> ContentAddressableStorageInstance:
    """Generates :class:`buildgrid.server.cas.service.ContentAddressableStorageService`
    using the tag ``!cas``.

    Usage
        .. code:: yaml

            # This assumes that the YAML anchors are defined elsewhere
            - !cas
              storage: *cas-storage

    Args:
        storage(:class:`buildgrid.server.cas.storage.storage_abc.StorageABC`):
            Instance of storage to use. This must be an object constructed using
            a YAML tag ending in ``-storage``, for example ``!disk-storage``.

        tree_cache_size (int | None): Size of GetTreeResponse cache, default to None.
            This feature is experimental for testing purposes.
            It could be deprecated in favor of a redis cache in future.

        tree_cache_ttl_minutes (float): TTL of GetTreeResponse cache, default to 60 minutes.
            This feature is experimental for testing purposes.
            It could be deprecated in favor of a redis cache in future.
    """

    click.echo(click.style(f"Creating a CAS service using {type(storage).__name__}\n", fg="green", bold=True))
    return ContentAddressableStorageInstance(
        storage,
        read_only=read_only,
        tree_cache_size=tree_cache_size,
        tree_cache_ttl_minutes=tree_cache_ttl_minutes,
    )


@object_tag("!bytestream")
def load_bytestream_controller(
    storage: StorageABC,
    read_only: bool = False,
    disable_overwrite_early_return: bool = False,
    stream_blob: bool = True,
) -> ByteStreamInstance:
    """Generates :class:`buildgrid.server.cas.service.ByteStreamService`
    using the tag ``!bytestream``.

    Usage
        .. code:: yaml

            # This assumes that the YAML anchors are defined elsewhere
            - !bytestream
              storage: *cas-storage

    Args:
        storage(:class:`buildgrid.server.cas.storage.storage_abc.StorageABC`):
            Instance of storage to use. This must be an object constructed using
            a YAML tag ending in ``-storage``, for example ``!disk-storage``.

        stream-blob (bool): Fetch the blob as a stream from backend storage.
    """

    click.echo(
        click.style(f"Creating a ByteStream service using storage {type(storage).__name__}", fg="green", bold=True)
    )
    return ByteStreamInstance(
        storage,
        read_only=read_only,
        disable_overwrite_early_return=disable_overwrite_early_return,
        stream_blob=stream_blob,
    )


@object_tag("!memory-build-events")
def load_memory_build_events_controller() -> BuildEventStreamStorage:
    """Generates :class:`buildgrid.server.build_events.storage.BuildEventStreamStorage`
    using the tag ``!memory-build-events-storage``.

    Usage
        .. code:: yaml

            - !memory-build-events
    """

    return BuildEventStreamStorage()


@object_tag("!metering-service-client")
def load_metering_service_client(
    base_url: str,
    token_path: str | None = None,
    retry_max_attempts: int = 0,  # Default to no retry
    retry_exp_base: float = 1.5,
    retry_multiplier: float = 1.0,
    retry_max_wait: float = 10.0,
    retry_http_statuses: list[int] | None = None,
    retry_exceptions: list[str] | None = None,
    retry_cause_exceptions: list[str] | None = None,
) -> metering.SyncMeteringServiceClient:
    """Generates :class:`buildgrid_metering.client.SyncMeteringServiceClient`
    using the tag ``!metering-service-client``.

    Usage
        .. code:: yaml

            - !metering-service-client
              token-path: /tmp/path/to/token
              retry-max-attempts: 3
              retry-exp-base: 2
              retry-multiplier: 1
              retry-http-statuses: [503]
              retry-exceptions: ["metering-service-client-error"]
    """

    if token_path is not None:
        auth_config = metering.auth.AuthTokenConfig(mode=metering.auth.AuthTokenMode.FILEPATH, value=token_path)
    else:
        auth_config = metering.auth.AuthTokenConfig(mode=metering.auth.AuthTokenMode.NONE, value="")

    def _get_exception_class(name: str) -> type[Exception]:
        exception_classes = {
            "metering-service-error": MeteringServiceError,
            "metering-service-client-error": MeteringServiceClientError,
            "timeout-error": requests.ConnectionError,
        }
        try:
            return exception_classes[name]
        except KeyError:
            raise ValueError(f"Unsupported exception class: {name}. Supported classes: {exception_classes.keys()}")

    retry_config = metering.RetryConfig(
        max_attempts=retry_max_attempts,
        exp_base=retry_exp_base,
        multiplier=retry_multiplier,
        max_wait=retry_max_wait,
        http_statuses=tuple(retry_http_statuses or []),
        exception_types=tuple(_get_exception_class(e) for e in (retry_exceptions or [])),
        cause_exception_types=tuple(_get_exception_class(e) for e in (retry_cause_exceptions or [])),
    )
    click.echo(f"Metering service client {retry_config=}")

    return metering.SyncMeteringServiceClient(
        base_url, token_loader=metering.auth.AuthTokenLoader(auth_config), retry_config=retry_config
    )


@object_tag("!asset-client")
def load_asset_client(
    url: str,
    credentials: ClientCredentials | None = None,
    instance_name: str = "",
    request_timeout: float = 5.0,
    retries: int = 3,
) -> AssetClient:
    """Generates :class:`buildgrid_metering.client.AssetClient`
    using the tag ``!asset-client``.

    Usage
        .. code:: yaml

            - !asset-client
              url: https://remote-asset.com
              instance-name: dev
              credentials:
                tls-client-cert: /path/to/cert
                auth-token: /path/to/token
              request-timeout: 5
              retries: 3
    """

    credentials = credentials or {}
    channel, *_ = setup_channel(
        remote_url=url,
        auth_token=credentials.get("auth-token"),
        client_key=credentials.get("tls-client-key"),
        client_cert=credentials.get("tls-client-cert"),
        server_cert=credentials.get("tls-server-cert"),
        timeout=request_timeout,
    )
    return AssetClient(channel=channel, instance_name=instance_name, retries=retries)


@object_tag("!introspection")
def load_introspection_instance(scheduler: Scheduler) -> IntrospectionInstance:
    return IntrospectionInstance(scheduler)


@object_tag("!sentry")
def load_sentry(dsn: str = "", sample_rate: float = 0, proxy: str = "") -> Sentry:
    """Generates :class:`buildgrid.server.sentry.Sentry`
    using the tag ``!sentry``.

    Usage
        .. code:: yaml

            - !sentry
              dsn: https://public@sentry.example.com/1
              sample-rate: 0.5
              proxy: https://proxy.example.com:80
    """

    return Sentry(dsn=dsn, sample_rate=sample_rate, proxy=proxy)


@object_tag("!limiter")
def load_limiter(concurrent_request_limit: int = 0) -> Limiter:
    return Limiter(
        LimiterConfig(
            concurrent_request_limit=concurrent_request_limit,
        ),
    )


def _parse_size(size: str) -> int:
    """Convert a string containing a size in bytes (e.g. '2GB') to a number."""
    _size_prefixes = {"k": 2**10, "m": 2**20, "g": 2**30, "t": 2**40}
    size = size.lower()

    if size[-1] == "b":
        size = size[:-1]
    if size[-1] in _size_prefixes:
        return int(size[:-1]) * _size_prefixes[size[-1]]
    return int(size)


def _validate_url_and_credentials(url: str, credentials: ClientCredentials | None) -> bool:
    """Validate a URL and set of credentials for the URL.

    This parses the given URL, to determine if it should be used with
    credentials (ie. to create a secure gRPC channel), or not (ie. to create
    an insecure gRPC channel).

    ClientCredentials will be ignored for insecure channels, but if specified need
    to be valid for secure channels. Secure client channels with no specified
    credentials are valid, since gRPC will attempt to fall back to a default
    root certificate location used with no private key or certificate chain.

    If the credentials are invalid, then this function will output the error
    using ``click.echo``, and return ``False``. Otherwise this function will
    return True

    Args:
        url (str): The URL to use for validation.
        credentials (dict, optional): The credentials configuration to validate.

    """
    try:
        parsed_url = urlparse(url)
    except ValueError:
        click.echo(
            click.style(
                "ERROR: Failed to parse URL for gRPC channel construction.\n" + f"The problematic URL was: {url}.\n",
                fg="red",
                bold=True,
            ),
            err=True,
        )
        return False
    unix_socket = parsed_url.scheme == "unix"

    if parsed_url.scheme in INSECURE_URI_SCHEMES:
        # Its a URL for an insecure channel that we recognize
        if credentials is not None:
            click.echo(
                click.style(
                    "WARNING: credentials were specified for a gRPC channel, but "
                    f"`{url}` uses an insecure scheme. The credentials will be "
                    "ignored.\n",
                    fg="bright_yellow",
                )
            )
        return True

    elif parsed_url.scheme not in SECURE_URI_SCHEMES and not unix_socket:
        # Its not insecure, and its not a recognized secure scheme, so error out.
        click.echo(click.style(f"ERROR: URL {url} uses an unsupported scheme.\n", fg="red", bold=True), err=True)
        return False

    if not credentials:
        # Unix sockets are treated as secure only if credentials are set
        if not unix_socket:
            click.echo(
                click.style(
                    f"WARNING: {url} uses a secure scheme but no credentials were "
                    "specified. gRPC will attempt to fall back to defaults.\n",
                    fg="bright_yellow",
                )
            )
        return True

    client_key = credentials.get("tls-client-key")
    client_cert = credentials.get("tls-client-cert")
    server_cert = credentials.get("tls-server-cert")

    valid = True
    missing = {}
    if server_cert is not None and not os.path.exists(server_cert):
        valid = False
        missing["tls-server-cert"] = server_cert
    if client_key is not None and not os.path.exists(client_key):
        valid = False
        missing["tls-client-key"] = client_key
    if client_cert is not None and not os.path.exists(client_cert):
        valid = False
        missing["tls-client-cert"] = client_cert

    if not valid:
        click.echo(
            click.style(
                "ERROR: one or more configured TLS credentials files were "
                + "missing.\nSet remote url scheme to `http` or `grpc` in order to "
                + "deactivate TLS encryption.\nMissing files:",
                fg="red",
                bold=True,
            ),
            err=True,
        )
        for key, path in missing.items():
            click.echo(click.style(f"  - {key}: {path}", fg="red", bold=True), err=True)
        return False
    return True


def _validate_server_credentials(credentials: dict[str, str] | None) -> None:
    """Validate a configured set of credentials.

    If the credentials are invalid, then this function will call ``sys.exit``
    and stop the process, since there's no point continuing. If this function
    returns without exiting the program, then the credentials were valid.

    Args:
        credentials (dict): The credentials configuration to validate.

    """
    if not credentials:
        click.echo(
            click.style(
                "ERROR: no TLS certificates were specified for the server's network config.\n"
                + "Set `insecure-mode` to True to deactivate TLS encryption.\n",
                fg="red",
                bold=True,
            ),
            err=True,
        )
        sys.exit(-1)

    server_key = credentials.get("tls-server-key")
    server_cert = credentials.get("tls-server-cert")
    client_certs = credentials.get("tls-client-certs")

    valid = True
    missing = {}
    if server_cert is None or not os.path.exists(server_cert):
        valid = False
        missing["tls-server-cert"] = server_cert
    if server_key is None or not os.path.exists(server_key):
        valid = False
        missing["tls-server-key"] = server_key
    if client_certs is not None and not os.path.exists(client_certs):
        valid = False
        missing["tls-client-certs"] = client_certs

    if not valid:
        click.echo(
            click.style(
                "ERROR: Couldn't find certificates for secure server port.\n"
                "Set `insecure-mode` to True to deactivate TLS encryption.\n"
                "Missing files:",
                fg="red",
                bold=True,
            ),
            err=True,
        )
        for key, path in missing.items():
            click.echo(click.style(f"  - {key}: {path}", fg="red", bold=True), err=True)
        sys.exit(-1)


def get_logstream_connection_info(logstream: Any) -> tuple[str | None, dict[str, str] | None, str | None]:
    logstream_url = None
    credentials = None
    logstream_instance_name = None
    if logstream:
        logstream_url = logstream["url"]
        credentials = logstream.get("credentials")
        if not _validate_url_and_credentials(logstream_url, credentials=credentials):
            sys.exit(-1)
        logstream_instance_name = logstream.get("instance-name", "")

    return logstream_url, credentials, logstream_instance_name


def get_schema(strict: bool = False) -> Any:
    """
    Gets a schema for the buildgrid configuration.
    If in strict mode, all object definitions will set additionalProperties to false
    """

    schema_text = files("buildgrid.server.app.settings").joinpath("schema.yml").read_text()
    schema = yaml.safe_load(schema_text)

    if strict:

        def disable_unknown_properties(item: Any) -> None:
            if isinstance(item, dict):
                if "properties" in item and "additionalProperties" not in item:
                    item["additionalProperties"] = False
                for value in item.values():
                    disable_unknown_properties(value)
            if isinstance(item, list):
                for value in item:
                    disable_unknown_properties(value)

        disable_unknown_properties(schema)

    return schema


def validate_config(path: "os.PathLike[str]", strict: bool = False, fail_deprecations: bool = False) -> None:
    """
    Validate a buildgrid configuration against its schema.
    In this mode, no real components are loaded, it simply detects invalid argument values.
    If in strict mode, all object definitions will set additionalProperties to false
    """

    with open(path) as f:
        return validate_config_value(f.read(), strict=strict, fail_deprecations=fail_deprecations)


def validate_config_value(data: str, strict: bool = False, fail_deprecations: bool = False) -> None:
    """
    Validate a buildgrid configuration against its schema.
    In this mode, no real components are loaded, it simply detects invalid argument values.
    If in strict mode, all object definitions will set additionalProperties to false
    """

    schema = get_schema(strict=strict)

    class Loader(yaml.SafeLoader):
        """
        This loader class mocks out the response value for all components by returning simple dicts.
        Additionally, each item is validated against its object definition to avoid confusing oneOf error outputs.
        """

        def struct_loader(self, node: yaml.MappingNode) -> Any:
            if node.value == "":
                args: dict[Hashable, Any] = {"kind": node.tag}
            else:
                args = {"kind": node.tag, **self.construct_mapping(node, deep=True)}

            component_schema = {
                "$schema": schema["$schema"],
                "$ref": f"#/definitions/{node.tag[1:]}",
                "definitions": schema["definitions"],
            }
            jsonschema.validate(args, component_schema)

            if deprecation_notes := deprecated_object_keys.get(node.tag):
                for deprecated_key, deprecation_note in deprecation_notes.items():
                    if deprecated_key in args:
                        error = f"Deprecated key {deprecated_key} used in {node.tag}: {deprecation_note}"
                        click.echo(click.style(f"WARNING: {error}", fg="bright_yellow"))
                        if fail_deprecations:
                            raise ValueError(error)

            return args

        def string_loader(self, node: yaml.Node) -> Any:
            return node.value

    for kind in object_definitions:
        Loader.add_constructor(kind, Loader.struct_loader)
    for kind in string_definitions:
        Loader.add_constructor(kind, Loader.string_loader)

    instance = yaml.load(data, Loader=Loader)
    jsonschema.validate(instance, schema)


def load_config(path: "os.PathLike[str]") -> Any:
    """
    Load and validate a buildgrid configuration.
    """

    with open(path) as f:
        return load_config_value(f.read())


def load_config_value(data: str) -> Any:
    """
    Load and validate a buildgrid configuration.
    """

    validate_config_value(data, strict=False)

    class Loader(yaml.SafeLoader):
        """
        This loader class proxies tag lookups to concreate loader factory methods.
        """

        def struct_loader(self, node: yaml.MappingNode) -> Any:
            loader = object_definitions[node.tag]
            if node.value == "":
                args: dict[str, Any] = {}
            else:
                args = {str(k): v for k, v in self.construct_mapping(node, deep=True).items()}

            for key, value in dict(args).items():
                args[key.replace("-", "_")] = args.pop(key)

            return loader(**args)

        def string_loader(self, node: yaml.Node) -> Any:
            return string_definitions[node.tag](node.value)

    for kind in object_definitions:
        Loader.add_constructor(kind, Loader.struct_loader)
    for kind in string_definitions:
        Loader.add_constructor(kind, Loader.string_loader)

    return yaml.load(data, Loader=Loader)
