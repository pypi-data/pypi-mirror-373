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


"""
CAS services
==================

Implements the Content Addressable Storage API and ByteStream API.
"""

import itertools
import re
from typing import Any, Iterator, cast

import grpc

from buildgrid._protos.build.bazel.remote.execution.v2.remote_execution_pb2 import DESCRIPTOR as RE_DESCRIPTOR
from buildgrid._protos.build.bazel.remote.execution.v2.remote_execution_pb2 import (
    BatchReadBlobsRequest,
    BatchReadBlobsResponse,
    BatchUpdateBlobsRequest,
    BatchUpdateBlobsResponse,
    Digest,
    FindMissingBlobsRequest,
    FindMissingBlobsResponse,
    GetTreeRequest,
    GetTreeResponse,
)
from buildgrid._protos.build.bazel.remote.execution.v2.remote_execution_pb2_grpc import (
    ContentAddressableStorageServicer,
    add_ContentAddressableStorageServicer_to_server,
)
from buildgrid._protos.google.bytestream import bytestream_pb2, bytestream_pb2_grpc
from buildgrid._protos.google.bytestream.bytestream_pb2 import (
    QueryWriteStatusRequest,
    QueryWriteStatusResponse,
    ReadRequest,
    ReadResponse,
    WriteRequest,
    WriteResponse,
)
from buildgrid._protos.google.rpc import code_pb2, status_pb2
from buildgrid.server.cas.instance import (
    EMPTY_BLOB,
    EMPTY_BLOB_DIGEST,
    ByteStreamInstance,
    ContentAddressableStorageInstance,
)
from buildgrid.server.decorators import rpc
from buildgrid.server.enums import ByteStreamResourceType
from buildgrid.server.exceptions import InvalidArgumentError
from buildgrid.server.logging import buildgrid_logger
from buildgrid.server.servicer import InstancedServicer
from buildgrid.server.settings import HASH_LENGTH

LOGGER = buildgrid_logger(__name__)


def _printable_batch_update_blobs_request(request: BatchUpdateBlobsRequest) -> dict[str, Any]:
    # Log the digests but not the data
    return {
        "instance_name": request.instance_name,
        "digests": [r.digest for r in request.requests],
    }


class ContentAddressableStorageService(
    ContentAddressableStorageServicer, InstancedServicer[ContentAddressableStorageInstance]
):
    SERVICE_NAME = "ContentAddressableStorage"
    REGISTER_METHOD = add_ContentAddressableStorageServicer_to_server
    FULL_NAME = RE_DESCRIPTOR.services_by_name[SERVICE_NAME].full_name

    @rpc(instance_getter=lambda r: cast(str, r.instance_name))
    def FindMissingBlobs(
        self, request: FindMissingBlobsRequest, context: grpc.ServicerContext
    ) -> FindMissingBlobsResponse:
        # No need to find the empty blob in the cas because the empty blob cannot be missing
        digests_to_find = [digest for digest in request.blob_digests if digest != EMPTY_BLOB_DIGEST]
        return self.get_instance(request.instance_name).find_missing_blobs(digests_to_find)

    @rpc(instance_getter=lambda r: cast(str, r.instance_name), request_formatter=_printable_batch_update_blobs_request)
    def BatchUpdateBlobs(
        self, request: BatchUpdateBlobsRequest, context: grpc.ServicerContext
    ) -> BatchUpdateBlobsResponse:
        return self.get_instance(request.instance_name).batch_update_blobs(request.requests)

    @rpc(instance_getter=lambda r: cast(str, r.instance_name))
    def BatchReadBlobs(self, request: BatchReadBlobsRequest, context: grpc.ServicerContext) -> BatchReadBlobsResponse:
        # No need to actually read the empty blob in the cas as it is always present
        digests_to_read = [digest for digest in request.digests if digest != EMPTY_BLOB_DIGEST]
        empty_digest_count = len(request.digests) - len(digests_to_read)

        instance = self.get_instance(request.instance_name)
        response = instance.batch_read_blobs(digests_to_read)

        # Append the empty blobs to the response
        for _ in range(empty_digest_count):
            response_proto = response.responses.add()
            response_proto.data = EMPTY_BLOB
            response_proto.digest.CopyFrom(EMPTY_BLOB_DIGEST)
            status_code = code_pb2.OK
            response_proto.status.CopyFrom(status_pb2.Status(code=status_code))

        return response

    @rpc(instance_getter=lambda r: cast(str, r.instance_name))
    def GetTree(self, request: GetTreeRequest, context: grpc.ServicerContext) -> Iterator[GetTreeResponse]:
        yield from self.get_instance(request.instance_name).get_tree(request)


class ResourceNameRegex:
    # CAS read name format: "{instance_name}/blobs/{hash}/{size}"
    READ = "^(.*?)/?(blobs/.*/[0-9]*)$"

    # CAS write name format: "{instance_name}/uploads/{uuid}/blobs/{hash}/{size}[optional arbitrary extra content]"
    WRITE = "^(.*?)/?(uploads/.*/blobs/.*/[0-9]*)"


def _parse_resource_name(resource_name: str, regex: str) -> tuple[str, str, "ByteStreamResourceType"]:
    cas_match = re.match(regex, resource_name)
    if cas_match:
        return cas_match[1], cas_match[2], ByteStreamResourceType.CAS
    else:
        raise InvalidArgumentError(f"Invalid resource name: [{resource_name}]")


def _read_instance_name(resource_name: str) -> str:
    return _parse_resource_name(resource_name, ResourceNameRegex.READ)[0]


def _write_instance_name(resource_name: str) -> str:
    return _parse_resource_name(resource_name, ResourceNameRegex.WRITE)[0]


def _printable_write_request(request: WriteRequest) -> dict[str, Any]:
    # Log all the fields except `data`:
    return {
        "resource_name": request.resource_name,
        "write_offset": request.write_offset,
        "finish_write": request.finish_write,
    }


class ByteStreamService(bytestream_pb2_grpc.ByteStreamServicer, InstancedServicer[ByteStreamInstance]):
    SERVICE_NAME = "ByteStream"
    REGISTER_METHOD = bytestream_pb2_grpc.add_ByteStreamServicer_to_server
    FULL_NAME = bytestream_pb2.DESCRIPTOR.services_by_name[SERVICE_NAME].full_name

    @rpc(instance_getter=lambda r: _read_instance_name(r.resource_name))
    def Read(self, request: ReadRequest, context: grpc.ServicerContext) -> Iterator[ReadResponse]:
        _, resource_name, resource_type = _parse_resource_name(request.resource_name, ResourceNameRegex.READ)
        if resource_type == ByteStreamResourceType.CAS:
            blob_details = resource_name.split("/")
            if len(blob_details[1]) != HASH_LENGTH:
                raise InvalidArgumentError(f"Invalid digest [{resource_name}]")
            try:
                digest = Digest(hash=blob_details[1], size_bytes=int(blob_details[2]))
            except ValueError:
                raise InvalidArgumentError(f"Invalid digest [{resource_name}]")

            bytes_returned = 0
            expected_bytes = digest.size_bytes - request.read_offset
            if request.read_limit:
                expected_bytes = min(expected_bytes, request.read_limit)

            try:
                if digest.size_bytes == 0:
                    if digest.hash != EMPTY_BLOB_DIGEST.hash:
                        raise InvalidArgumentError(f"Invalid digest [{digest.hash}/{digest.size_bytes}]")
                    yield bytestream_pb2.ReadResponse(data=EMPTY_BLOB)
                    return

                for blob in self.current_instance.read_cas_blob(digest, request.read_offset, request.read_limit):
                    bytes_returned += len(blob.data)
                    yield blob
            finally:
                if bytes_returned != expected_bytes:
                    LOGGER.warning(
                        "Read request exited early.",
                        tags=dict(
                            digest=digest,
                            bytes_returned=bytes_returned,
                            expected_bytes=expected_bytes,
                            read_offset=request.read_offset,
                            read_limit=request.read_limit,
                        ),
                    )
                else:
                    LOGGER.info("Read request completed.", tags=dict(digest=digest))

    @rpc(instance_getter=lambda r: _write_instance_name(r.resource_name), request_formatter=_printable_write_request)
    def Write(self, request_iterator: Iterator[WriteRequest], context: grpc.ServicerContext) -> WriteResponse:
        request = next(request_iterator)
        _, resource_name, resource_type = _parse_resource_name(
            request.resource_name,
            ResourceNameRegex.WRITE,
        )
        if resource_type == ByteStreamResourceType.CAS:
            blob_details = resource_name.split("/")
            _, hash_, size_bytes = blob_details[1], blob_details[3], blob_details[4]
            write_response = self.current_instance.write_cas_blob(
                hash_, size_bytes, itertools.chain([request], request_iterator)
            )
            if write_response.committed_size == int(size_bytes):
                LOGGER.info("Write request completed.", tags=dict(digest=f"{hash_}/{size_bytes}"))
            return write_response
        return bytestream_pb2.WriteResponse()

    @rpc(instance_getter=lambda r: _write_instance_name(r.resource_name))
    def QueryWriteStatus(
        self, request: QueryWriteStatusRequest, context: grpc.ServicerContext
    ) -> QueryWriteStatusResponse:
        context.abort(grpc.StatusCode.UNIMPLEMENTED, "Method not implemented!")
