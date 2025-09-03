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

import io
import os
import random
import threading
import time
from tempfile import TemporaryFile
from typing import IO, TYPE_CHECKING, Any, BinaryIO, Callable, Iterator, Mapping, Sequence, cast

import botocore
import pycurl

from buildgrid.server.logging import buildgrid_logger
from buildgrid.server.settings import (
    S3_MAX_RETRIES,
    S3_MULTIPART_MAX_CONCURRENT_PARTS,
    S3_MULTIPART_PART_SIZE,
    S3_TIMEOUT_CONNECT,
    S3_TIMEOUT_READ,
    S3_USERAGENT_NAME,
)

LOGGER = buildgrid_logger(__name__)

# https://boto3.amazonaws.com/v1/documentation/api/latest/guide/retries.html
_RETRIABLE_HTTP_STATUS_CODES = (408, 429, 500, 502, 503, 504, 509)
_RETRIABLE_S3_ERROR_CODES = (
    "Throttling",
    "ThrottlingException",
    "ThrottledException",
    "RequestThrottledException",
    "ProvisionedThroughputExceededException",
)
# Maximum backoff in seconds
_MAX_BACKOFF = 20
# Maximum requests to run in parallel via CurlMulti
_MAX_CURLMULTI_CONNECTIONS = 10

if TYPE_CHECKING:
    from mypy_boto3_s3 import Client as S3Client


class _CurlLocal(threading.local):
    def __init__(self) -> None:
        self.curlmulti = pycurl.CurlMulti()
        self.curlmulti.setopt(pycurl.M_MAX_TOTAL_CONNECTIONS, _MAX_CURLMULTI_CONNECTIONS)
        # Default the connection cache size to the number of connections we allow, instead of 4 x number of handles
        self.curlmulti.setopt(pycurl.M_MAXCONNECTS, _MAX_CURLMULTI_CONNECTIONS)


_curlLocal = _CurlLocal()


class S3Object:
    def __init__(self, bucket: str, key: str) -> None:
        self.bucket = bucket
        self.key = key
        self.fileobj: IO[bytes] | None = None
        self.filesize: int | None = None
        self.error: Exception | None = None
        self.status_code: int | None = None
        self._method: str = ""
        self._errfileobj: IO[bytes] | None = None
        self._response_headers: dict[str, str] = {}

    @property
    def response_headers(self) -> dict[str, str]:
        return self._response_headers

    # Function to process HTTP response headers
    def _header_function(self, header_line: bytes) -> None:
        header = header_line.decode("ascii")

        # Skip status line
        if ":" not in header:
            return

        name, value = header.split(":", maxsplit=1)
        name = name.strip().lower()
        value = value.strip()

        self._response_headers[name] = value

    def reset(self) -> None:
        """Reset the state mutated by sent requests to prepare for a retry"""
        if self.fileobj is not None:
            self.fileobj.truncate(0)
        if self._errfileobj is not None:
            self._errfileobj.truncate(0)
        self._response_headers.clear()
        self.error = None
        self.status_code = None


class UploadPart(io.BufferedIOBase):
    def __init__(self, upload_id: str, number: int, file: IO[bytes], eof: int, size: int, offset: int) -> None:
        super().__init__()
        self._upload_id = upload_id
        self._number = number
        self._response = io.BytesIO()
        self._file = file
        self._content = None
        try:
            self._fd: int | None = file.fileno()
        except OSError:
            # The "file" doesn't have a file descriptor, its probably a BytesIO.
            # Read our part now so that we don't need to cope with thread safety
            # when `UploadPart.read` is called.
            self._fd = None
            old_position = file.tell()
            file.seek(offset)
            self._content = file.read(size)
            file.seek(old_position)

        self._size = size
        self._start = offset
        self._end = min(eof, offset + size)
        self._read_offset = 0

    @property
    def upload_id(self) -> str:
        return self._upload_id

    @property
    def number(self) -> int:
        return self._number

    @property
    def response(self) -> BinaryIO:
        return self._response

    def __len__(self) -> int:
        return self._end - self._start

    def readable(self) -> bool:
        return True

    def seekable(self) -> bool:
        return False

    def writable(self) -> bool:
        return True

    def read(self, size: int | None = -1) -> bytes:
        # If we have a real file underlying this part, then we want to do an
        # `os.pread` for just the part that is relevant.
        if self._fd is not None:
            if size is None or size == -1:
                size = self._size

            # Calculate the actual read offset and make sure we're within our
            # section of the file.
            offset = self._start + self._read_offset
            if offset >= self._end:
                return b""

            # Make sure we only read up to the end of our section of the file,
            # in case the size requested is larger than the number of bytes
            # remaining in our section
            size = min(size, self._end - offset)
            content = os.pread(self._fd, size, offset)
            self._read_offset += size
            return content

        # Otherwise we can just return our pre-determined slice of the actual
        # contents. This case should only be reached when MAX_IN_MEMORY_BLOB_SIZE_BYTES
        # is the same as or larger than S3_MAX_UPLOAD_SIZE, which should ideally
        # never be the case.
        else:
            if self._content is None:
                raise ValueError(
                    f"Part {self._number} of upload {self._upload_id} is backed "
                    "by a BytesIO but the content couldn't be read when the part "
                    "was instantiated."
                )
            return self._content

    def write(self, b: bytes) -> int:  # type: ignore[override]
        return self._response.write(b)


def _curl_handle_for_s3(
    s3: "S3Client",
    method: str,
    s3object: S3Object,
    extra_params: Mapping[str, str | int] | None = None,
    headers: Mapping[str, str] | None = None,
) -> pycurl.Curl:
    if extra_params is None:
        extra_params = {}
    s3object._method = method
    params: dict[str, str | int] = {"Bucket": s3object.bucket, "Key": s3object.key, **extra_params}
    url = s3.generate_presigned_url(method, Params=params, ExpiresIn=3600)
    c = pycurl.Curl()
    c.s3object = s3object  # type: ignore
    c.setopt(pycurl.USERAGENT, S3_USERAGENT_NAME)
    c.setopt(pycurl.CONNECTTIMEOUT, S3_TIMEOUT_CONNECT)
    c.setopt(pycurl.TIMEOUT, S3_TIMEOUT_READ)
    c.setopt(pycurl.FAILONERROR, True)
    c.setopt(pycurl.URL, url)
    c.setopt(pycurl.HEADERFUNCTION, s3object._header_function)
    if headers:
        header_strs = [f"{k}: {v}" for k, v in headers.items()]
        c.setopt(pycurl.HTTPHEADER, header_strs)
    return c


# TODO Don't put random attributes on curl like this??
def c_s3ojb(c: pycurl.Curl) -> S3Object:
    return c.s3object  # type: ignore


def _curl_should_retry(c: pycurl.Curl, errno: int) -> bool:
    if errno in (
        pycurl.E_COULDNT_CONNECT,
        pycurl.E_SEND_ERROR,
        pycurl.E_RECV_ERROR,
        pycurl.E_OPERATION_TIMEDOUT,
        pycurl.E_PARTIAL_FILE,
    ):
        # Retry on network and timeout errors
        return True

    if errno == pycurl.E_HTTP_RETURNED_ERROR:
        s3obj = c_s3ojb(c)
        if s3obj.status_code in _RETRIABLE_HTTP_STATUS_CODES:
            # Retry on 'Request Timeout', 'Too Many Requests' and transient server errors
            return True

        if error_response := getattr(s3obj.error, "response", None):
            if error_response["Error"]["Code"] in _RETRIABLE_S3_ERROR_CODES:
                return True

    return False


def _curl_multi_run(
    objects: Sequence[S3Object], curl_handle_func: Callable[[S3Object], pycurl.Curl], attempt: int = 1
) -> None:
    m = _curlLocal.curlmulti
    curl_handles = []
    retry_objects = []

    try:
        for s3object in objects:
            c = curl_handle_func(s3object)
            m.add_handle(c)
            curl_handles.append(c)

        while True:
            ret, active_handles = m.perform()
            if ret == pycurl.E_CALL_MULTI_PERFORM:
                # More processing required
                continue

            if active_handles:
                # Wait for next event
                m.select(15.0)
            else:
                # All operations complete
                break

        num_q, ok_list, err_list = m.info_read()
        assert num_q == 0

        for c in ok_list:
            s3obj = c_s3ojb(c)
            s3obj.status_code = c.getinfo(pycurl.HTTP_CODE)
        for c, errno, errmsg in err_list:
            s3obj = c_s3ojb(c)
            if errno == pycurl.E_HTTP_RETURNED_ERROR:
                s3obj.status_code = c.getinfo(pycurl.HTTP_CODE)
                response: dict[str, Any] = {}
                response["status_code"] = s3obj.status_code
                response["headers"] = s3obj._response_headers
                if (errfileobj := s3obj._errfileobj) is None:
                    response["body"] = b""
                else:
                    errfileobj.seek(0)
                    response["body"] = errfileobj.read()
                    errfileobj.truncate(0)
                parser = botocore.parsers.RestXMLParser()
                # TODO: botocore safely handles `None` being passed here, but it is
                # probably best to rework this to get the correct `Shape` to match
                # the type hints from boto3-stubs
                parsed_response = parser.parse(response, None)  # type: ignore[arg-type]
                s3obj.error = botocore.exceptions.ClientError(parsed_response, s3obj._method)
            else:
                s3obj.error = pycurl.error(errmsg)

            if attempt < S3_MAX_RETRIES and _curl_should_retry(c, errno):
                s3obj.reset()
                retry_objects.append(s3obj)
    finally:
        for c in curl_handles:
            m.remove_handle(c)
        curl_handles.clear()

    if retry_objects and attempt < S3_MAX_RETRIES:
        # Wait between attempts with truncated exponential backoff with jitter
        exp_backoff = 2 ** (attempt - 1)
        exp_backoff_with_jitter = random.random() * exp_backoff
        retry_delay = min(exp_backoff_with_jitter, _MAX_BACKOFF)

        LOGGER.debug(f"Retrying {len(retry_objects)}/{len(objects)} after {retry_delay} seconds")
        time.sleep(retry_delay)

        _curl_multi_run(retry_objects, curl_handle_func, attempt=attempt + 1)


def head_objects(s3: "S3Client", objects: Sequence[S3Object]) -> None:
    def curl_handle_func(s3object: S3Object) -> pycurl.Curl:
        c = _curl_handle_for_s3(s3, "head_object", s3object)
        c.setopt(pycurl.NOBODY, True)
        return c

    _curl_multi_run(objects, curl_handle_func)


def head_object(s3: "S3Client", s3object: S3Object) -> None:
    head_objects(s3, [s3object])
    if s3object.error is not None:
        raise s3object.error


def set_s3_timeout(
    c: pycurl.Curl,
    s3object: S3Object,
    timeout_seconds_per_kilobyte: float | None,
    timeout_min_seconds: float,
) -> None:
    timeout = timeout_min_seconds
    if s3object.filesize is not None and timeout_seconds_per_kilobyte is not None:
        timeout = max(timeout, s3object.filesize * timeout_seconds_per_kilobyte / 1024)
    c.setopt(pycurl.TIMEOUT, int(timeout))


def get_objects(
    s3: "S3Client",
    objects: Sequence[S3Object],
    timeout_seconds_per_kilobyte: float | None = None,
    timeout_min_seconds: float = S3_TIMEOUT_READ,
    headers: Mapping[str, str] | None = None,
) -> None:
    def curl_handle_func(s3object: S3Object) -> pycurl.Curl:
        c = _curl_handle_for_s3(s3, "get_object", s3object, headers=headers)
        c.setopt(pycurl.WRITEDATA, s3object.fileobj)
        set_s3_timeout(c, s3object, timeout_seconds_per_kilobyte, timeout_min_seconds)
        s3object._errfileobj = s3object.fileobj
        return c

    _curl_multi_run(objects, curl_handle_func)


def get_object(
    s3: "S3Client",
    s3object: S3Object,
    timeout_seconds_per_kilobyte: float | None = None,
    timeout_min_seconds: float = S3_TIMEOUT_READ,
    headers: Mapping[str, str] | None = None,
) -> None:
    get_objects(s3, [s3object], timeout_seconds_per_kilobyte, timeout_min_seconds, headers=headers)
    if s3object.error is not None:
        raise s3object.error


def put_objects(
    s3: "S3Client",
    objects: Sequence[S3Object],
    timeout_seconds_per_kilobyte: float | None = None,
    timeout_min_seconds: float = S3_TIMEOUT_READ,
) -> None:
    def curl_handle_func(s3object: S3Object) -> pycurl.Curl:
        c = _curl_handle_for_s3(s3, "put_object", s3object)
        c.setopt(pycurl.READDATA, s3object.fileobj)
        c.setopt(pycurl.INFILESIZE_LARGE, s3object.filesize)
        c.setopt(pycurl.UPLOAD, 1)
        set_s3_timeout(c, s3object, timeout_seconds_per_kilobyte, timeout_min_seconds)
        s3object._errfileobj = io.BytesIO()
        c.setopt(pycurl.WRITEDATA, s3object._errfileobj)
        return c

    _curl_multi_run(objects, curl_handle_func)


def put_object(
    s3: "S3Client",
    s3object: S3Object,
    timeout_seconds_per_kilobyte: float | None = None,
    timeout_min_seconds: float = S3_TIMEOUT_READ,
) -> None:
    put_objects(s3, [s3object], timeout_seconds_per_kilobyte, timeout_min_seconds)
    if s3object.error is not None:
        raise s3object.error


ParsedResponse = dict[str, str | dict[str, str | int | dict[str, str]]]


def _parse_s3_response(s3: "S3Client", response: BinaryIO, s3object: S3Object, shape_name: str) -> ParsedResponse:
    response_dict: dict[str, int | None | dict[str, str] | bytes] = {}
    response_dict["status_code"] = s3object.status_code
    response_dict["headers"] = s3object.response_headers
    response.seek(0)
    response_dict["body"] = response.read()

    parser = botocore.parsers.RestXMLParser()
    shape = s3.meta.service_model.shape_for(shape_name)
    return cast(ParsedResponse, parser.parse(response_dict, shape))


def start_multipart_upload(s3: "S3Client", s3object: S3Object) -> str:
    response = io.BytesIO()

    def curl_handle_func(_s3object: S3Object) -> pycurl.Curl:
        c = _curl_handle_for_s3(s3, "create_multipart_upload", _s3object)
        c.setopt(pycurl.WRITEDATA, response)
        c.setopt(pycurl.POST, 1)
        return c

    _curl_multi_run([s3object], curl_handle_func)
    if s3object.error is not None:
        raise s3object.error

    parsed_response = _parse_s3_response(s3, response, s3object, "CreateMultipartUploadOutput")
    return parsed_response["UploadId"]  # type: ignore


def upload_parts(s3: "S3Client", s3object: S3Object, parts: Sequence[UploadPart]) -> dict[int, str]:
    s3object_map = {S3Object(s3object.bucket, s3object.key): part for part in parts}

    def curl_handle_func(_s3object: S3Object) -> pycurl.Curl:
        part = s3object_map[_s3object]
        params: dict[str, int | str] = {"UploadId": part.upload_id, "PartNumber": part.number}
        c = _curl_handle_for_s3(s3, "upload_part", _s3object, extra_params=params)
        c.setopt(pycurl.READDATA, part)
        c.setopt(pycurl.UPLOAD, 1)
        c.setopt(pycurl.INFILESIZE_LARGE, len(part))
        c.setopt(pycurl.WRITEDATA, part)
        return c

    _curl_multi_run(list(s3object_map.keys()), curl_handle_func)

    errors: list[Exception] = [_s3object.error for _s3object in s3object_map.keys() if _s3object.error is not None]
    if len(errors) > 0:
        raise errors[0]

    uploaded: dict[int, str] = {}
    for _s3object, part in s3object_map.items():
        response = _parse_s3_response(s3, part.response, _s3object, "UploadPartOutput")
        uploaded[part.number] = response["ResponseMetadata"]["HTTPHeaders"]["etag"]  # type: ignore
    return uploaded


def complete_multipart_upload(
    s3: "S3Client", s3object: S3Object, upload_id: str, parts: Mapping[int, str]
) -> ParsedResponse:
    # Use the boto3 client directly here, rather than a presigned URL. This is
    # necessary because boto3's URL presigning is broken for `complete_multipart_upload`
    # when using s3v4 auth.
    #
    # See https://github.com/boto/boto3/issues/2192
    return cast(
        ParsedResponse,
        s3.complete_multipart_upload(
            Bucket=s3object.bucket,
            Key=s3object.key,
            UploadId=upload_id,
            MultipartUpload={"Parts": [{"ETag": tag, "PartNumber": number} for number, tag in parts.items()]},
        ),
    )


def _list_multipart_parts(s3: "S3Client", s3object: S3Object, upload_id: str) -> ParsedResponse:
    response = io.BytesIO()

    def curl_handle_func(_s3object: S3Object) -> pycurl.Curl:
        params = {"UploadId": upload_id}
        c = _curl_handle_for_s3(s3, "list_parts", _s3object, extra_params=params)
        c.setopt(pycurl.WRITEDATA, response)
        return c

    _curl_multi_run([s3object], curl_handle_func)
    if s3object.error is not None:
        raise s3object.error
    return _parse_s3_response(s3, response, s3object, "ListPartsOutput")


def abort_multipart_upload(s3: "S3Client", s3object: S3Object, upload_id: str) -> None:
    def curl_handle_func(_s3object: S3Object) -> pycurl.Curl:
        params = {"UploadId": upload_id}
        c = _curl_handle_for_s3(s3, "abort_multipart_upload", _s3object, extra_params=params)
        c.setopt(pycurl.CUSTOMREQUEST, "DELETE")
        return c

    parts = _list_multipart_parts(s3, s3object, upload_id)

    # We need to iterate here in case any part uploads slip through in a race
    # against the AbortMultipartUpload call.
    #
    # See https://docs.aws.amazon.com/AmazonS3/latest/API/API_AbortMultipartUpload.html
    while len(parts.get("Parts", [])) > 0:
        _curl_multi_run([s3object], curl_handle_func)
        try:
            parts = _list_multipart_parts(s3, s3object, upload_id)
        except botocore.exceptions.ClientError as e:
            code = e.response.get("Error", {}).get("Code")
            if code == "404":
                # 404 error here means that the multipart upload is properly aborted.
                break
            raise e


def multipart_upload(s3: "S3Client", s3object: S3Object) -> None:
    if s3object.fileobj is None or s3object.filesize is None:
        raise TypeError("S3Object provided to multipart upload didn't contain a file.")

    upload_id = start_multipart_upload(s3, s3object)

    try:
        part_number = 1
        parts: dict[int, str] = {}
        queue: list[UploadPart] = []
        while (part_number - 1) * S3_MULTIPART_PART_SIZE < s3object.filesize:
            part = UploadPart(
                upload_id=upload_id,
                number=part_number,
                file=s3object.fileobj,
                eof=s3object.filesize,
                size=S3_MULTIPART_PART_SIZE,
                offset=(part_number - 1) * S3_MULTIPART_PART_SIZE,
            )
            queue.append(part)

            part_number += 1

            if len(queue) >= S3_MULTIPART_MAX_CONCURRENT_PARTS:
                uploaded = upload_parts(s3, s3object, queue)
                parts.update(uploaded)
                queue = []
        uploaded = upload_parts(s3, s3object, queue)
        parts.update(uploaded)

        complete_multipart_upload(s3, s3object, upload_id, parts)
    except Exception as e:
        abort_multipart_upload(s3, s3object, upload_id)
        raise e


def stream_multipart_upload(s3: "S3Client", s3object: S3Object, chunks: Iterator[bytes]) -> None:
    upload_id = start_multipart_upload(s3, s3object)

    try:
        part_number = 1
        parts: dict[int, str] = {}

        with TemporaryFile() as buffer:
            for chunk in chunks:
                buffer.write(chunk)
                if buffer.tell() < S3_MULTIPART_PART_SIZE:
                    continue
                size = buffer.tell()
                buffer.seek(0)
                part = UploadPart(
                    upload_id=upload_id,
                    number=part_number,
                    file=buffer,
                    eof=size,
                    size=size,
                    offset=0,
                )

                uploaded = upload_parts(s3, s3object, [part])
                parts.update(uploaded)
                part_number += 1
                # Reset the buffer
                buffer.truncate(0)
                buffer.seek(0)

            if buffer.tell() > 0:
                size = buffer.tell()
                buffer.seek(0)
                part = UploadPart(
                    upload_id=upload_id,
                    number=part_number,
                    file=buffer,
                    eof=size,
                    size=size,
                    offset=0,
                )
                uploaded = upload_parts(s3, s3object, [part])
                parts.update(uploaded)

        complete_multipart_upload(s3, s3object, upload_id, parts)
    except Exception as e:
        abort_multipart_upload(s3, s3object, upload_id)
        raise e
