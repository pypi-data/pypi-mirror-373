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

import hashlib

from buildgrid.server.version import __version__

# Latest REAPI version supported:
HIGH_REAPI_VERSION = "2.2.0"

# Earliest non-deprecated REAPI version supported:
LOW_REAPI_VERSION = "2.0.0"

# Hash function used for computing digests:
HASH = hashlib.sha256

# Length in bytes of a hash string returned by HASH:
HASH_LENGTH = HASH().digest_size * 2

# Minimum required size for the gRPC handlers thread pool, ie.
# min. value for the 'thread-pool-size' configuration key.
MIN_THREAD_POOL_SIZE = 5

# Maximum number of client auth. credentials to cache:
AUTH_CACHE_SIZE = 200

# Period, in seconds, for the monitoring cycle:
MONITORING_PERIOD = 60.0

# Maximum size for a single gRPC request, minus a small delta:
MAX_REQUEST_SIZE = 4 * 1024 * 1024 - 1024

# Maximum number of elements per gRPC request:
MAX_REQUEST_COUNT = 500

# Value that establishes an upper bound on the size of a file that can
# be queued into a batch request. Expressed as a percentage of the
# batch size limit:
BATCH_REQUEST_SIZE_THRESHOLD = 0.25

# Maximum size that a blob can have to be stored completely in-memory
# for reading/writing.
# Blobs that exceed this limit will be written to a temporary file and
# read from disk.
MAX_IN_MEMORY_BLOB_SIZE_BYTES = 4 * 1024 * 1024

# Maximum time a worker can wait for work whilst connected to the Bots
# service, in seconds. Unset request-timeouts may be represented as
# max uint64 depending on the client, so capping it is important.
MAX_WORKER_TTL = 300

# Time to wait between retries caused by gRPC streaming issues
STREAM_ERROR_RETRY_PERIOD = 60

# String format for log records:
LOG_RECORD_FORMAT = "%(asctime)s:[%(request_id)s][%(name)36.36s][%(levelname)5.5s][%(threadName)s]: %(message)s"
# The different log record attributes are documented here:
# https://docs.python.org/3/library/logging.html#logrecord-attributes

# Name of the header key to attach optional `RequestMetadata`values.
# (This is defined in the REAPI specification.)
REQUEST_METADATA_HEADER_NAME = "build.bazel.remote.execution.v2.requestmetadata-bin"

# Name of the header key to attach client identity information.
CLIENT_IDENTITY_HEADER_NAME = "buildgrid.v2.clientidentity-bin"

# Name of the header key to attach scheduling metadata information.
SCHEDULING_METADATA_HEADER_NAME = "build.buildgrid.schedulingmetadata-bin"

# 'RequestMetadata' header values. These values will be used when
# attaching optional metadata to a gRPC request's header:
REQUEST_METADATA_TOOL_NAME = "buildgrid"
REQUEST_METADATA_TOOL_VERSION = __version__

S3_USERAGENT_NAME = f"{REQUEST_METADATA_TOOL_NAME}/{REQUEST_METADATA_TOOL_VERSION}"
S3_MAX_RETRIES = 4
S3_MAX_UPLOAD_SIZE = 8 * 1024 * 1024
S3_TIMEOUT_CONNECT = 120
S3_TIMEOUT_READ = 120
S3_MULTIPART_PART_SIZE = 8 * 1024 * 1024
S3_MULTIPART_MAX_CONCURRENT_PARTS = 10

# Minimum deadline in seconds that workers can set during work assignment.
# Requests with a deadline less than this value will never get work
NETWORK_TIMEOUT = 3

# Default Maximum execution timeout; lazily checked upon request of job status,
# directly or when doing de-duplication checks.
# If the job has been executing for longer than this amount of time (in seconds)
# it will be marked as cancelled (existing operations will be cancelled, and the job
# will not be de-duplicated)
DEFAULT_MAX_EXECUTION_TIMEOUT = 7200

# Default timeout to acquire locks or give up
DEFAULT_LOCK_ACQUIRE_TIMEOUT = 60

# Default platform property keys
DEFAULT_PLATFORM_PROPERTY_KEYS = {"OSFamily", "ISA"}

# Maximum size of a ListOperations request.
# In-memory schedulers do not have paging, so this does not apply there.
DEFAULT_MAX_LIST_OPERATION_PAGE_SIZE = 1000

# Default interval to refresh the JWKs.
DEFAULT_JWKS_REFETCH_INTERVAL_MINUTES = 60

# SQL Scheduler and IndexedCAS
# Least time between automated pool disposals when detecting errors
MIN_TIME_BETWEEN_SQL_POOL_DISPOSE_MINUTES = 15

# Amount of time between when the pool is disposed
# and when clients should retry requests
COOLDOWN_TIME_AFTER_POOL_DISPOSE_SECONDS = 30

# Number of seconds used as bounds for how many seconds
# to add/remove when asking clients to retry
COOLDOWN_TIME_JITTER_BASE = 5

# SQL Scheduler
SQL_SCHEDULER_METRICS_PUBLISH_INTERVAL_SECONDS = 300

# Time (seconds) to allow for shutdown before outputting running thread info
SHUTDOWN_ALARM_DELAY = 20

# bgd browser-backend settings
# ----------------------------
#
# Time to live for the in-memory ActionResult cache entries
BROWSER_RESULT_CACHE_TTL = 300

# Time-to-live for the in-memory generic blob cache entries
BROWSER_BLOB_CACHE_TTL = 300

# Maximum blob size to cache in the browser backend
BROWSER_MAX_CACHE_ENTRY_SIZE = 4 * 1024 * 1024

# Maximum number of entries in the ActionResult cache
BROWSER_RESULT_CACHE_MAX_LENGTH = 256

# Maximum number of entries in the blob cache
BROWSER_BLOB_CACHE_MAX_LENGTH = 256


SECURE_URI_SCHEMES = ["https", "grpcs"]
INSECURE_URI_SCHEMES = ["http", "grpc"]

# Maximum page size for paged list APIs
MAX_LIST_PAGE_SIZE = 100
