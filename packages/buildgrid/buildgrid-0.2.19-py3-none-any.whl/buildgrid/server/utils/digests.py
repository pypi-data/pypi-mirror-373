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


from dataclasses import dataclass

from buildgrid._protos.build.bazel.remote.execution.v2.remote_execution_pb2 import Digest, DigestFunction
from buildgrid.server.settings import HASH, HASH_LENGTH


@dataclass(frozen=True)
class HashableDigest:
    hash: str
    size_bytes: int

    def to_digest(self) -> Digest:
        return Digest(hash=self.hash, size_bytes=self.size_bytes)


def get_hash_type() -> "DigestFunction.Value.ValueType":
    """Returns the hash type."""
    hash_name = HASH().name
    if hash_name == "sha256":
        return DigestFunction.SHA256
    return DigestFunction.UNKNOWN


def create_digest(bytes_to_digest: bytes) -> Digest:
    """Computes the :obj:`Digest` of a piece of data.

    The :obj:`Digest` of a data is a function of its hash **and** size.

    Args:
        bytes_to_digest (bytes): byte data to digest.

    Returns:
        :obj:`Digest`: The :obj:`Digest` for the given byte data.
    """
    return Digest(hash=HASH(bytes_to_digest).hexdigest(), size_bytes=len(bytes_to_digest))


def parse_digest(digest_string: str) -> Digest | None:
    """Creates a :obj:`Digest` from a digest string.

    A digest string should alway be: ``{hash}/{size_bytes}``.

    Args:
        digest_string (str): the digest string.

    Returns:
        :obj:`Digest`: The :obj:`Digest` read from the string or None if
            `digest_string` is not a valid digest string.
    """
    digest_hash, digest_size = digest_string.split("/")

    if len(digest_hash) == HASH_LENGTH and digest_size.isdigit():
        return Digest(hash=digest_hash, size_bytes=int(digest_size))

    return None


def validate_digest_data(digest: Digest, data: bytes) -> bool:
    """Validate that the given digest corresponds to the given data."""
    return len(data) == digest.size_bytes and HASH(data).hexdigest() == digest.hash
