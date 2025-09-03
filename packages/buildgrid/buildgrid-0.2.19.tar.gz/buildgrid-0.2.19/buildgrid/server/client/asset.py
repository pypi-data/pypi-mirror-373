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


from datetime import datetime
from typing import Any, Iterable, Mapping

import grpc
from google.protobuf.timestamp_pb2 import Timestamp

from buildgrid._protos.build.bazel.remote.asset.v1.remote_asset_pb2 import (
    PushBlobRequest,
    PushBlobResponse,
    PushDirectoryRequest,
    PushDirectoryResponse,
    Qualifier,
)
from buildgrid._protos.build.bazel.remote.asset.v1.remote_asset_pb2_grpc import FetchStub, PushStub
from buildgrid._protos.build.bazel.remote.execution.v2.remote_execution_pb2 import Digest
from buildgrid.server.client.retrier import GrpcRetrier
from buildgrid.server.logging import buildgrid_logger
from buildgrid.server.metadata import metadata_list

LOGGER = buildgrid_logger(__name__)


class AssetClient:
    """Client for Fetch and Push services defined in remote_asset protocol"""

    def __init__(
        self,
        channel: grpc.Channel,
        instance_name: str,
        retries: int = 0,
        max_backoff: int = 64,
        should_backoff: bool = True,
    ) -> None:
        self._channel = channel
        self._instance_name = instance_name
        self._push_stub = PushStub(channel)
        self._fetch_stub = FetchStub(channel)
        self._retrier = GrpcRetrier(retries=retries, max_backoff=max_backoff, should_backoff=should_backoff)

    def __enter__(self) -> "AssetClient":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self._channel.close()
        LOGGER.info("Stopped AssetClient.")

    def push_blob(
        self,
        *,
        uris: Iterable[str],
        qualifiers: Mapping[str, str],
        blob_digest: Digest,
        expire_at: datetime | None = None,
        referenced_blobs: Iterable[Digest] = [],
        referenced_directories: Iterable[Digest] = [],
    ) -> PushBlobResponse:
        def _push_blob() -> PushBlobResponse:
            qualifiers_pb = [Qualifier(name=name, value=value) for name, value in qualifiers.items()]
            expire_at_pb: Timestamp | None = None
            if expire_at is not None:
                expire_at_pb = Timestamp()
                expire_at_pb.FromDatetime(expire_at)

            request = PushBlobRequest(
                instance_name=self._instance_name,
                uris=uris,
                qualifiers=qualifiers_pb,
                expire_at=expire_at_pb,
                blob_digest=blob_digest,
                references_blobs=referenced_blobs,
                references_directories=referenced_directories,
            )
            return self._push_stub.PushBlob(request=request, metadata=metadata_list())

        return self._retrier.retry(_push_blob)

    def push_directory(
        self,
        *,
        uris: Iterable[str],
        qualifiers: Mapping[str, str],
        root_directory_digest: Digest,
        expire_at: datetime | None = None,
        referenced_blobs: Iterable[Digest] = [],
        referenced_directories: Iterable[Digest] = [],
    ) -> PushDirectoryResponse:
        def _push_directory() -> PushDirectoryResponse:
            qualifiers_pb = [Qualifier(name=name, value=value) for name, value in qualifiers.items()]
            expire_at_pb: Timestamp | None = None
            if expire_at is not None:
                expire_at_pb = Timestamp()
                expire_at_pb.FromDatetime(expire_at)

            request = PushDirectoryRequest(
                instance_name=self._instance_name,
                uris=uris,
                qualifiers=qualifiers_pb,
                expire_at=expire_at_pb,
                root_directory_digest=root_directory_digest,
                references_blobs=referenced_blobs,
                references_directories=referenced_directories,
            )
            return self._push_stub.PushDirectory(request=request, metadata=metadata_list())

        return self._retrier.retry(_push_directory)
