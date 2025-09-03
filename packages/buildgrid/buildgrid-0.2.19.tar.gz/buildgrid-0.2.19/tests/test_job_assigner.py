# Copyright (C) 2022 Bloomberg LP
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
import json

from buildgrid._protos.google.devtools.remoteworkers.v1test2.bots_pb2 import BotSession
from buildgrid._protos.google.devtools.remoteworkers.v1test2.worker_pb2 import Device, Worker
from buildgrid.server.scheduler import DynamicPropertySet
from buildgrid.server.scheduler.properties import hash_from_dict


def session_for_props(props):
    properties = []
    for key, values in props.items():
        if isinstance(values, str):
            values = [values]
        for value in values:
            properties.append(Device.Property(key=key, value=value))

    return BotSession(worker=Worker(devices=[Device(properties=properties)]))


def session_hashes(props, session):
    return list(map(hash_from_dict, props.worker_properties(session)))


def test_get_partial_capabilities_hashes() -> None:
    empty_props = DynamicPropertySet(
        unique_property_keys=set(),
        match_property_keys=set(),
        wildcard_property_keys=set(),
    )
    capabilities = session_hashes(empty_props, BotSession())
    assert sorted(capabilities) == [hashlib.sha1(json.dumps({}, sort_keys=True).encode()).hexdigest()]

    expected_partial_capabilities = [
        {},
        {"OSFamily": ["Linux"]},
        {"ISA": ["x86-32"]},
        {"ISA": ["x86-64"]},
        {"OSFamily": ["Linux"], "ISA": ["x86-32"]},
        {"OSFamily": ["Linux"], "ISA": ["x86-64"]},
        {"ISA": ["x86-32", "x86-64"]},
        {"OSFamily": ["Linux"], "ISA": ["x86-32", "x86-64"]},
    ]
    expected_partial_capabilities_hashes = sorted(
        list(
            map(
                lambda cap: hashlib.sha1(json.dumps(cap, sort_keys=True).encode()).hexdigest(),
                expected_partial_capabilities,
            )
        )
    )
    props = DynamicPropertySet(
        unique_property_keys=set(),
        match_property_keys={"OSFamily", "ISA"},
        wildcard_property_keys=set(),
    )

    capabilities = session_hashes(props, session_for_props({"OSFamily": "Linux", "ISA": {"x86-32", "x86-64"}}))
    assert sorted(capabilities) == expected_partial_capabilities_hashes

    # Should be the same if the string is passed in as a singleton set
    capabilities = session_hashes(props, session_for_props({"OSFamily": {"Linux"}, "ISA": {"x86-32", "x86-64"}}))
    assert sorted(capabilities) == expected_partial_capabilities_hashes

    # Changing the order of the ISA values should produce the same hashes
    capabilities = session_hashes(props, session_for_props({"OSFamily": "Linux", "ISA": {"x86-64", "x86-32"}}))
    assert sorted(capabilities) == expected_partial_capabilities_hashes
