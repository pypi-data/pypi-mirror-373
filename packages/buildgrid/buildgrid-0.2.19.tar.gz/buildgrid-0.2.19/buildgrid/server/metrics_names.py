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

# flake8: noqa
# fmt: off
class METRIC:
    class RPC:
        DURATION                            = "rpc.duration.ms"
        INPUT_BYTES                         = "rpc.input_bytes.count"
        OUTPUT_BYTES                        = "rpc.output_bytes.count"
        AUTH_DURATION                       = "rpc.auth.duration.ms"

    class ACTION_CACHE:
        INVALID_CACHE_COUNT                 = "action_cache.invalid_cache.count"
        MIRRORED_MATCH_COUNT                = "action_cache.mirrored_matches.count"
        MIRRORED_MISMATCH_COUNT             = "action_cache.mirrored_mismatches.count"
        RESULT_AGE                          = "action_cache.result_age.ms"

    class CAS:
        BLOBS_COUNT                         = "cas.blobs.count"
        BLOBS_MISSING_COUNT                 = "cas.blobs_missing.count"
        BLOBS_MISSING_PERCENT               = "cas.blobs_missing.percent"
        BLOB_BYTES                          = "cas.blob_bytes.count"
        TREE_CACHE_HIT_COUNT                = "cas.tree_cache_hit.count"
        TREE_CACHE_MISS_COUNT               = "cas.tree_cache_miss.count"

    class STORAGE:
        STAT_DURATION                       = "storage.stat.duration.ms"
        BULK_STAT_DURATION                  = "storage.bulk_stat.duration.ms"

        READ_DURATION                       = "storage.read.duration.ms"
        STREAM_READ_DURATION                = "storage.stream_read.duration.ms"
        BULK_READ_DURATION                  = "storage.bulk_read.duration.ms"

        DELETE_DURATION                     = "storage.delete_blob.duration.ms"
        BULK_DELETE_DURATION                = "storage.bulk_delete.duration.ms"
        DELETE_ERRORS_COUNT                 = "storage.delete_errors.count"

        WRITE_DURATION                      = "storage.write.duration.ms"
        STREAM_WRITE_DURATION               = "storage.stream_write.duration.ms"
        BULK_WRITE_DURATION                 = "storage.bulk_write.duration.ms"

        GET_TREE_DURATION                   = "storage.get_tree.duration.ms"

        class WITH_CACHE:
            CACHE_HIT_COUNT                 = "storage.with_cache.cache_hit.count"
            CACHE_MISS_COUNT                = "storage.with_cache.cache_miss.count"
            CACHE_HIT_PERCENT               = "storage.with_cache.cache_hit.percent"

        class SQL_INDEX:
            UPDATE_TIMESTAMP_DURATION       = "storage.sql_index.update_timestamp.duration.ms"
            SAVE_DIGESTS_DURATION           = "storage.sql_index.save_digest.duration.ms"
            SIZE_CALCULATION_DURATION       = "storage.sql_index.size_calculation.duration.ms"
            DELETE_N_BYTES_DURATION         = "storage.sql_index.delete_n_bytes.duration.ms"
            BULK_DELETE_INDEX_DURATION      = "storage.sql_index.bulk_delete_index.duration.ms"
            MARK_DELETED_DURATION           = "storage.sql_index.mark_deleted.duration.ms"
            PREMARKED_DELETED_COUNT         = "storage.sql_index.premarked_deleted.count"

        class REPLICATED:
            REQUIRED_REPLICATION_COUNT      = "storage.replicated.required_replication.count"
            REPLICATION_COUNT               = "storage.replicated.replication.count"
            REPLICATION_QUEUE_FULL_COUNT    = "storage.replicated.replication_queue_full.count"
            REPLICATION_ERROR_COUNT         = "storage.replicated.replication.errors.count"

        class S3:
            BLOB_AGE                        = "storage.s3.total_age.ms"
            BLOB_BYTES                      = "storage.s3.blob_bytes.count"

    class CLEANUP:
        DURATION                            = "cleanup.duration.ms"
        BATCH_DURATION                      = "cleanup.batch.duration.ms"
        BLOBS_DELETED_PER_SECOND            = "cleanup.blobs_deleted.per_second"
        BYTES_DELETED_PER_SECOND            = "cleanup.bytes_deleted.per_second"
        BYTES_DELETED_COUNT                 = "cleanup.bytes_deleted.count"
        TOTAL_BYTES_COUNT                   = "cleanup.total_bytes.count"
        LOW_WATERMARK_BYTES_COUNT           = "cleanup.low_watermark_bytes.count"
        HIGH_WATERMARK_BYTES_COUNT          = "cleanup.high_watermark_bytes.count"
        TOTAL_BYTES_WATERMARK_PERCENT       = "cleanup.total_bytes_watermark.percent"
        TOTAL_BLOBS_COUNT                   = "cleanup.total_blobs.count"
        LOW_WATERMARK_BLOBS_COUNT           = "cleanup.low_watermark_blobs.count"
        HIGH_WATERMARK_BLOBS_COUNT          = "cleanup.high_watermark_blobs.count"
        TOTAL_BLOBS_WATERMARK_PERCENT       = "cleanup.total_blobs_watermark.percent"

        class JANITOR:
            BLOB_AGE                        = "cleanup.janitor.blob_age.ms"
            BLOB_BYTES                      = "cleanup.janitor.blob_bytes.count"

    class SCHEDULER:
        JOB_COUNT                           = "scheduler.jobs.count"
        BOTS_COUNT                          = "scheduler.bots.count"

        ASSIGNMENT_DURATION                 = "scheduler.assignment.duration.ms"
        SYNCHRONIZE_DURATION                = "scheduler.synchronize.duration.ms"

        PRUNE_DURATION                      = "scheduler.prune.duration.ms"
        PRUNE_COUNT                         = "scheduler.prune.count"

        QUEUE_TIMEOUT_DURATION              = "scheduler.queue_timeout.duration.ms"
        QUEUE_TIMEOUT_COUNT                 = "scheduler.queue_timeout.count"

        EXECUTION_TIMEOUT_DURATION          = "scheduler.execution_timeout.duration.ms"
        EXECUTION_TIMEOUT_COUNT             = "scheduler.execution_timeout.count"

    class CONNECTIONS:
        CLIENT_COUNT                        = "connections.clients.count"
        WORKER_COUNT                        = "connections.workers.count"

    class SQL:
        SQL_SESSION_COUNT_TEMPLATE          = "sql.session.count.{name}"
        SQL_ACTIVE_SESSION_GAUGE_TEMPLATE   = "sql.active.session.gauge.{name}"

    class JOB:
        DURATION                            = "job.duration.ms"
