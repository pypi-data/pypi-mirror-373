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


import pytest

from buildgrid._protos.build.bazel.remote.execution.v2 import remote_execution_pb2
from buildgrid._protos.build.buildgrid.identity_pb2 import ClientIdentity
from buildgrid._protos.build.buildgrid.scheduling_pb2 import SchedulingMetadata
from buildgrid.server.auth.manager import set_context_client_identity
from buildgrid.server.metadata import extract_client_identity, extract_request_metadata, extract_scheduling_metadata
from buildgrid.server.settings import REQUEST_METADATA_HEADER_NAME, SCHEDULING_METADATA_HEADER_NAME


def generate_metadata():
    request_metadata = remote_execution_pb2.RequestMetadata()
    request_metadata.tool_details.tool_name = "tool-name"
    request_metadata.tool_details.tool_version = "1.0"

    request_metadata.action_id = "920ea86d6a445df893d0a39815e8856254392ce40e5957f167af8f16485916fb"
    request_metadata.tool_invocation_id = "cec14b04-075e-4f47-9c24-c5e6ac7f9827"
    request_metadata.correlated_invocations_id = "9f962383-25f6-43b3-886d-56d761ac524e"

    from collections import namedtuple

    metadata_entry = namedtuple("metadata_entry", ("key", "value"))

    return [metadata_entry(REQUEST_METADATA_HEADER_NAME, request_metadata.SerializeToString())]


def test_extract_request_metadata():
    metadata = extract_request_metadata(generate_metadata())

    assert metadata.tool_details.tool_name == "tool-name"
    assert metadata.tool_details.tool_version == "1.0"
    assert metadata.action_id == "920ea86d6a445df893d0a39815e8856254392ce40e5957f167af8f16485916fb"
    assert metadata.tool_invocation_id == "cec14b04-075e-4f47-9c24-c5e6ac7f9827"
    assert metadata.correlated_invocations_id == "9f962383-25f6-43b3-886d-56d761ac524e"


def test_extract_request_metadata_with_no_metadata():
    metadata = extract_request_metadata(())
    assert metadata == remote_execution_pb2.RequestMetadata()


def test_extract_client_identity():
    mock_invocation_metadata = [
        ("x-request-workflow", "workflow"),
        ("x-request-actor", "tool"),
        ("x-request-subject", "user"),
    ]

    client_id = extract_client_identity("instance", mock_invocation_metadata)

    assert client_id.instance == "instance"
    assert client_id.workflow == "workflow"
    assert client_id.actor == "tool"
    assert client_id.subject == "user"


def test_extract_client_identity_empty():
    mock_invocation_metadata = []

    client_id = extract_client_identity("instance", mock_invocation_metadata)

    assert client_id is None


def test_extract_client_identity_with_ctx_var():
    mock_invocation_metadata = [
        ("x-request-workflow", "workflow"),
        ("x-request-actor", "tool"),
        ("x-request-subject", "user"),
    ]

    client_id = extract_client_identity("instance", mock_invocation_metadata)

    assert client_id.instance == "instance"
    assert client_id.workflow == "workflow"
    assert client_id.actor == "tool"
    assert client_id.subject == "user"

    set_context_client_identity(
        ClientIdentity(
            workflow="buildgrid",
            actor="janedoe",
            subject="johndoe",
        )
    )

    client_id = extract_client_identity("instance", mock_invocation_metadata)
    assert client_id.instance == "instance"
    assert client_id.workflow == "buildgrid"
    assert client_id.actor == "janedoe"
    assert client_id.subject == "johndoe"


def test_extract_scheduling_metadata():
    """Test extracting scheduling metadata with a simple locality hint."""
    # Create test scheduling metadata
    scheduling_metadata = SchedulingMetadata()
    scheduling_metadata.locality_hint = "hint"

    # Create mock metadata entry (using tuple access pattern like other functions)
    metadata_entries = [(SCHEDULING_METADATA_HEADER_NAME, scheduling_metadata.SerializeToString())]

    # Extract and verify
    extracted_metadata = extract_scheduling_metadata(metadata_entries)
    assert extracted_metadata.locality_hint == "hint"


def test_extract_scheduling_metadata_empty():
    """Test extracting scheduling metadata with no metadata present."""
    metadata_entries = []

    extracted_metadata = extract_scheduling_metadata(metadata_entries)
    assert extracted_metadata.locality_hint == ""  # Default protobuf string value


@pytest.mark.parametrize(
    "locality_hint",
    [
        "a",
        "b",
        "c",
        "zone-1",
        "datacenter-2",
    ],
)
def test_extract_scheduling_metadata_with_locality_hint(locality_hint):
    """Test extracting scheduling metadata with various locality hint values."""
    scheduling_metadata = SchedulingMetadata()
    scheduling_metadata.locality_hint = locality_hint

    metadata_entries = [(SCHEDULING_METADATA_HEADER_NAME, scheduling_metadata.SerializeToString())]

    extracted_metadata = extract_scheduling_metadata(metadata_entries)
    assert extracted_metadata.locality_hint == locality_hint


def test_extract_scheduling_metadata_malformed_data():
    """Test extracting scheduling metadata with malformed protobuf data."""
    # Create metadata entry with invalid protobuf data
    metadata_entries = [(SCHEDULING_METADATA_HEADER_NAME, b"invalid_protobuf_data")]

    # Should return empty SchedulingMetadata on parsing error
    extracted_metadata = extract_scheduling_metadata(metadata_entries)
    assert extracted_metadata.locality_hint == ""


def test_extract_scheduling_metadata_wrong_header():
    """Test extracting scheduling metadata when wrong header is present."""
    scheduling_metadata = SchedulingMetadata()
    scheduling_metadata.locality_hint = "should-not-be-found"

    # Use wrong header name
    metadata_entries = [("wrong-header-name", scheduling_metadata.SerializeToString())]

    extracted_metadata = extract_scheduling_metadata(metadata_entries)
    assert extracted_metadata.locality_hint == ""


def test_extract_scheduling_metadata_empty_binary_data():
    """Test extracting scheduling metadata with empty binary data."""
    # Empty binary data should parse as empty SchedulingMetadata
    metadata_entries = [(SCHEDULING_METADATA_HEADER_NAME, b"")]

    extracted_metadata = extract_scheduling_metadata(metadata_entries)
    assert extracted_metadata.locality_hint == ""
