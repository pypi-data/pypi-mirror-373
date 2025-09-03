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


import threading
import time
from contextlib import ExitStack
from datetime import datetime, timezone
from typing import Any

from buildgrid._protos.build.bazel.remote.execution.v2.remote_execution_pb2 import Digest
from buildgrid.server.app.settings.config import CleanupConfig
from buildgrid.server.cas.storage.index.index_abc import IndexABC
from buildgrid.server.context import instance_context
from buildgrid.server.logging import buildgrid_logger
from buildgrid.server.metrics_names import METRIC
from buildgrid.server.metrics_utils import publish_counter_metric, publish_gauge_metric, timer
from buildgrid.server.monitoring import get_monitoring_bus
from buildgrid.server.threading import ContextThreadPoolExecutor, ContextWorker

LOGGER = buildgrid_logger(__name__)


def _digests_str(digests: list[Digest]) -> str:
    return f"{len(digests)} digests ({sum(d.size_bytes for d in digests)} bytes)"


class CASCleanUp:
    """Creates a CAS cleanup service."""

    def __init__(
        self,
        dry_run: bool,
        sleep_interval: int,
        cleanup_configs: list[CleanupConfig],
        monitor: bool,
    ) -> None:
        self._stack = ExitStack()
        self._dry_run = dry_run
        self._sleep_interval = sleep_interval

        self._cleanup_configs = cleanup_configs

        self._is_instrumented = monitor

    # --- Public API ---

    def start(self, timeout: float | None = None) -> None:
        """Start cleanup service"""
        if self._is_instrumented:
            self._stack.enter_context(get_monitoring_bus())
        worker = self._stack.enter_context(ContextWorker(self._begin_cleanup, "CleanUpLauncher"))
        worker.wait(timeout=timeout)

    def stop(self, *args: Any, **kwargs: Any) -> None:
        """Stops the cleanup service"""
        LOGGER.info("Stopping Cleanup Service.")
        self._stack.close()

    def _begin_cleanup(self, stop_requested: threading.Event) -> None:
        if self._dry_run:
            for options in self._cleanup_configs:
                self._calculate_cleanup(options)
            return

        with ContextThreadPoolExecutor(max_workers=len(self._cleanup_configs)) as ex:
            futures = {
                config.name: ex.submit(self._retry_cleanup, config, stop_requested) for config in self._cleanup_configs
            }

            for instance_name, future in futures.items():
                try:
                    future.result()
                except Exception:
                    LOGGER.error("Cleanup exceeded retry limit.", tags=dict(instance_name=instance_name))

    def _retry_cleanup(self, config: CleanupConfig, stop_requested: threading.Event) -> None:
        attempts = 0
        while attempts <= config.retry_limit:
            try:
                self._cleanup_worker(config, stop_requested)
                LOGGER.info("Cleanup completed.", tags=dict(instance_name=config.name))
                break
            except Exception:
                LOGGER.exception("Cleanup failed.", tags=dict(instance_name=config.name))

                # Exponential backoff before retrying
                sleep_time = 1.6**attempts
                LOGGER.info("Retrying Cleanup after delay...", tags=dict(sleep_time_seconds=sleep_time))
                stop_requested.wait(timeout=sleep_time)
                attempts += 1
                continue

    def _calculate_cleanup(self, config: CleanupConfig) -> None:
        """Work out which blobs will be deleted by the cleanup command."""
        instance_name = config.name
        with instance_context(instance_name):
            LOGGER.info("Cleanup dry run.", tags=dict(instance_name=instance_name))
            index = config.index
            only_delete_before = datetime.now(timezone.utc) - config.only_if_unused_for
            large_blob_only_delete_before = (
                datetime.now(timezone.utc) - config.large_blob_lifetime if config.large_blob_lifetime else None
            )
            total_size = index.get_total_size()
            LOGGER.info(
                "Calculated CAS size.",
                tags=dict(
                    total_size=total_size,
                    high_watermark_bytes=config.high_watermark,
                    low_watermark_bytes=config.low_watermark,
                ),
            )
            if total_size >= config.high_watermark:
                required_space = total_size - config.low_watermark
                cleared_space = index.delete_n_bytes(
                    required_space,
                    dry_run=True,
                    protect_blobs_after=only_delete_before,
                    large_blob_threshold=config.large_blob_threshold,
                    large_blob_lifetime=large_blob_only_delete_before,
                )
                LOGGER.info(f"Determined {cleared_space} of the requested {required_space} bytes would be deleted.")
            else:
                LOGGER.info(f"Total size {total_size} is less than the high water mark, " f"nothing will be deleted.")

    def _do_cleanup_batch(
        self,
        index: IndexABC,
        only_delete_before: datetime,
        batch_size: int,
        large_blob_only_delete_before: datetime | None,
        large_blob_threshold: int | None,
    ) -> int:
        batch_start_time = time.time()

        LOGGER.info("Deleting bytes from the index.", tags=dict(batch_size=batch_size))
        bytes_deleted = index.delete_n_bytes(
            batch_size,
            protect_blobs_after=only_delete_before,
            large_blob_threshold=large_blob_threshold,
            large_blob_lifetime=large_blob_only_delete_before,
        )

        LOGGER.info("Bulk deleted bytes from index.", tags=dict(bytes_deleted=bytes_deleted))

        if self._is_instrumented and bytes_deleted > 0:
            batch_duration = time.time() - batch_start_time
            bytes_deleted_per_second = bytes_deleted / batch_duration
            publish_gauge_metric(METRIC.CLEANUP.BYTES_DELETED_PER_SECOND, bytes_deleted_per_second)
            publish_counter_metric(METRIC.CLEANUP.BYTES_DELETED_COUNT, bytes_deleted)
        return bytes_deleted

    def _cleanup_worker(self, cleanup_config: CleanupConfig, stop_requested: threading.Event) -> None:
        """Cleanup when full"""
        instance_name = cleanup_config.name
        with instance_context(instance_name):
            index = cleanup_config.index
            LOGGER.info("Cleanup started.", tags=dict(instance_name=instance_name))

            while not stop_requested.is_set():
                # When first starting a loop, we will also include any remaining delete markers as part of
                # the total size.
                total_size = index.get_total_size()
                self.publish_total_size_metric(total_size, cleanup_config.high_watermark, cleanup_config.low_watermark)

                blob_count = index.get_blob_count()
                blob_count_range: range | None = None
                if (
                    cleanup_config.high_blob_count_watermark is not None
                    and cleanup_config.low_blob_count_watermark is not None
                ):
                    blob_count_range = range(
                        cleanup_config.low_blob_count_watermark,
                        cleanup_config.high_blob_count_watermark,
                    )
                self.publish_blob_count_metric(blob_count, blob_count_range)

                if total_size >= cleanup_config.high_watermark or (
                    blob_count_range is not None and blob_count >= blob_count_range.stop
                ):
                    bytes_to_delete = total_size - cleanup_config.low_watermark
                    if bytes_to_delete > 0:
                        LOGGER.info(
                            "High bytes watermark exceeded. Deleting items from storage/index.",
                            tags=dict(
                                total_bytes=total_size,
                                min_bytes_to_delete=bytes_to_delete,
                                instance_name=instance_name,
                            ),
                        )
                    if blob_count_range is not None:
                        blobs_to_delete = blob_count - blob_count_range.start
                        if blobs_to_delete > 0:
                            LOGGER.info(
                                "High blob count watermark exceeded. Deleting items from storage/index.",
                                tags=dict(
                                    total_blobs=blob_count,
                                    min_blobs_to_delete=blobs_to_delete,
                                    instance_name=instance_name,
                                ),
                            )

                    with timer(METRIC.CLEANUP.DURATION):
                        while not stop_requested.is_set() and (
                            total_size > cleanup_config.low_watermark
                            or (blob_count_range is not None and blob_count > blob_count_range.start)
                        ):
                            only_delete_before = datetime.now(timezone.utc) - cleanup_config.only_if_unused_for
                            large_blob_only_delete_before = (
                                datetime.now(timezone.utc) - cleanup_config.large_blob_lifetime
                                if cleanup_config.large_blob_lifetime is not None
                                else None
                            )
                            with timer(METRIC.CLEANUP.BATCH_DURATION):
                                bytes_deleted = self._do_cleanup_batch(
                                    index=index,
                                    only_delete_before=only_delete_before,
                                    batch_size=cleanup_config.batch_size,
                                    large_blob_threshold=cleanup_config.large_blob_threshold,
                                    large_blob_only_delete_before=large_blob_only_delete_before,
                                )
                            if not bytes_deleted:
                                err = "Marked 0 digests for deletion, even though cleanup was triggered."
                                if total_size >= cleanup_config.high_watermark:
                                    LOGGER.error(f"{err} Total size still remains greater than high watermark!")
                                elif blob_count_range is not None and blob_count >= blob_count_range.stop:
                                    LOGGER.error(f"{err} Blob count remains greater than high watermark!")
                                else:
                                    LOGGER.warning(err)
                                stop_requested.wait(
                                    timeout=self._sleep_interval
                                )  # Avoid a busy loop when we can't make progress
                            total_size = index.get_total_size()
                            blob_count = index.get_blob_count()
                            self.publish_total_size_metric(
                                total_size, cleanup_config.high_watermark, cleanup_config.low_watermark
                            )
                            self.publish_blob_count_metric(blob_count, blob_count_range)
                            LOGGER.info("Finished cleanup batch.", tags=dict(non_stale_total_bytes=total_size))

                    LOGGER.info("Finished cleanup.", tags=dict(total_bytes=total_size))

                stop_requested.wait(timeout=self._sleep_interval)

    def publish_total_size_metric(self, total_size: int, high_watermark: int, low_watermark: int) -> None:
        if self._is_instrumented:
            high_watermark_percentage = float((total_size / high_watermark) * 100) if high_watermark > 0 else 0
            publish_gauge_metric(METRIC.CLEANUP.TOTAL_BYTES_COUNT, total_size)
            publish_gauge_metric(METRIC.CLEANUP.LOW_WATERMARK_BYTES_COUNT, low_watermark)
            publish_gauge_metric(METRIC.CLEANUP.HIGH_WATERMARK_BYTES_COUNT, high_watermark)
            publish_gauge_metric(METRIC.CLEANUP.TOTAL_BYTES_WATERMARK_PERCENT, high_watermark_percentage)

    def publish_blob_count_metric(self, blob_count: int, blob_count_range: range | None) -> None:
        if self._is_instrumented:
            publish_gauge_metric(METRIC.CLEANUP.TOTAL_BLOBS_COUNT, blob_count)
            if blob_count_range is not None:
                if blob_count_range.stop > 0:
                    high_watermark_percentage = float((blob_count / blob_count_range.stop) * 100)
                else:
                    high_watermark_percentage = 0
                publish_gauge_metric(METRIC.CLEANUP.LOW_WATERMARK_BLOBS_COUNT, blob_count_range.start)
                publish_gauge_metric(METRIC.CLEANUP.HIGH_WATERMARK_BLOBS_COUNT, blob_count_range.stop)
                publish_gauge_metric(METRIC.CLEANUP.TOTAL_BLOBS_WATERMARK_PERCENT, high_watermark_percentage)
