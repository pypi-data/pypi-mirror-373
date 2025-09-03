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

import random
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from itertools import product
from threading import Event
from typing import Any, Iterator

from buildgrid.server.cleanup.janitor.config import S3Config
from buildgrid.server.cleanup.janitor.index import IndexLookup
from buildgrid.server.cleanup.janitor.utils import check_bucket_versioning, get_s3_client
from buildgrid.server.logging import buildgrid_logger
from buildgrid.server.metrics_names import METRIC
from buildgrid.server.metrics_tags import tag_blob_age, tag_blob_size
from buildgrid.server.metrics_utils import publish_distribution_metric
from buildgrid.server.threading import ContextWorker

LOGGER = buildgrid_logger(__name__)


@dataclass(frozen=True)
class ListObjectResult:
    key: str
    version_id: str
    last_modified: datetime
    size: int


def publish_s3_object_metrics(s3_objects: set[ListObjectResult]) -> None:
    for obj in s3_objects:
        age = datetime.now(tz=timezone.utc) - obj.last_modified
        age_in_ms = age / timedelta(milliseconds=1)
        age_range = tag_blob_age(age_in_ms)
        size_range = tag_blob_size(obj.size)
        publish_distribution_metric(
            METRIC.CLEANUP.JANITOR.BLOB_AGE, age_in_ms, objectAgeRange=age_range, objectSizeRange=size_range
        )
        publish_distribution_metric(
            METRIC.CLEANUP.JANITOR.BLOB_BYTES, obj.size, objectAgeRange=age_range, objectSizeRange=size_range
        )


class S3Janitor:

    def __init__(self, s3Config: S3Config, index: IndexLookup):
        self._bucket_regex = re.compile(s3Config.bucket_regex)
        self._index = index
        self._path_prefix = s3Config.path_prefix
        self._s3 = get_s3_client(s3Config)
        self._sleep_interval = s3Config.sleep_interval
        self._hash_prefix_size = s3Config.hash_prefix_size
        self._max_batch_size = s3Config.max_batch_size
        self._batch_sleep_interval = s3Config.batch_sleep_interval

        self._stop_requested = Event()
        self._worker = ContextWorker(target=self.run, name="Janitor", on_shutdown_requested=self._stop_requested.set)

    def enumerate_versioned_bucket(self, bucket: str, prefix: str) -> Iterator[set[ListObjectResult]]:
        pages = self._s3.get_paginator("list_object_versions").paginate(
            Bucket=bucket, Prefix=prefix, PaginationConfig={"PageSize": self._max_batch_size}
        )
        for page in pages:
            if "Versions" not in page:
                continue

            list_objects = {
                ListObjectResult(
                    key=item["Key"],
                    version_id=item["VersionId"],
                    last_modified=item["LastModified"],
                    size=item["Size"],
                )
                for item in page["Versions"]
            }
            yield list_objects

    def enumerate_unversioned_bucket(self, bucket: str, prefix: str) -> Iterator[set[ListObjectResult]]:
        pages = self._s3.get_paginator("list_objects").paginate(
            Bucket=bucket, Prefix=prefix, PaginationConfig={"PageSize": self._max_batch_size}
        )
        for page in pages:
            if "Contents" not in page:
                continue

            list_objects = {
                ListObjectResult(
                    key=item["Key"],
                    version_id="",
                    last_modified=item["LastModified"],
                    size=item["Size"],
                )
                for item in page["Contents"]
            }
            yield list_objects

    def delete_s3_entries(self, bucket: str, missing_objects: list[ListObjectResult]) -> list[str]:
        LOGGER.info("Deleting orphaned blobs from S3.", tags=dict(digest_count=len(missing_objects)))
        response = self._s3.delete_objects(
            Bucket=bucket,
            Delete={
                "Objects": [{"Key": obj.key, "VersionId": obj.version_id} for obj in missing_objects],
                "Quiet": False,
            },
        )
        return [
            deleted_object["Key"] for deleted_object in response.get("Deleted", []) if "Key" in deleted_object.keys()
        ]

    def get_buckets(self) -> list[str]:
        response = self._s3.list_buckets()
        return [
            bucket["Name"] for bucket in response["Buckets"] if self._bucket_regex.search(bucket["Name"]) is not None
        ]

    # Generate all the hash prefixes and shuffle them to reduce the likelihood of
    # two janitors cleaning the same hash prefix
    def generate_prefixes(self) -> list[str]:
        if self._hash_prefix_size:
            prefixes = [
                (self._path_prefix + "/" if self._path_prefix else "") + "".join(x)
                for x in product("0123456789abcdef", repeat=self._hash_prefix_size)
            ]
            random.shuffle(prefixes)
        else:
            prefixes = [self._path_prefix]
        return prefixes

    def cleanup_bucket(self, bucket: str) -> int:
        LOGGER.info("Cleaning up bucket.", tags=dict(bucket=bucket))

        deleted_count = 0
        if check_bucket_versioning(self._s3, bucket):
            enumeration = self.enumerate_versioned_bucket
        else:
            enumeration = self.enumerate_unversioned_bucket

        for prefix in self.generate_prefixes():
            deleted_count_for_prefix = 0
            for page in enumeration(bucket, prefix):
                if self._stop_requested.is_set():
                    LOGGER.info("Janitor stop requested.")
                    return deleted_count
                # Create a mapping between a digest as stored in S3 and a digest as stored in the index
                # by stripping off any prefix and removing all '/' used by hash_prefix_size
                digest_map = {obj.key: obj.key.replace(self._path_prefix, "").replace("/", "") for obj in page}
                publish_s3_object_metrics(page)
                missing_digests = self._index.get_missing_digests(set(digest_map.values()))
                missing_objects = [obj for obj in page if digest_map[obj.key] in missing_digests]
                if missing_objects:
                    self.delete_s3_entries(bucket, missing_objects)
                    deleted_count_for_prefix += len(missing_objects)
                if self._batch_sleep_interval:
                    self._stop_requested.wait(timeout=self._batch_sleep_interval)
            LOGGER.info(
                "Deleted blobs from bucket prefix.",
                tags=dict(digest_count=deleted_count_for_prefix, bucket=bucket, prefix=prefix),
            )
            deleted_count += deleted_count_for_prefix

        LOGGER.info("Deleted blobs total from bucket.", tags=dict(digest_count=deleted_count, bucket=bucket))
        return deleted_count

    def __enter__(self) -> "S3Janitor":
        self.start()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.stop()

    def start(self) -> None:
        self._worker.start()

    def stop(self, *args: Any, **kwargs: Any) -> None:
        self._worker.stop()

    def run(self, stop_requested: Event) -> None:
        random.seed()
        while not stop_requested.is_set():
            try:
                bucket_names = self.get_buckets()

                # Shuffle the bucket names to reduce the likelihood of two janitors
                # concurrently cleaning the same bucket.
                random.shuffle(bucket_names)

                for bucket in bucket_names:
                    self.cleanup_bucket(bucket)
            except Exception:
                LOGGER.exception("Exception while cleaning up S3 storage with janitor")
                continue

            stop_requested.wait(timeout=self._sleep_interval)
