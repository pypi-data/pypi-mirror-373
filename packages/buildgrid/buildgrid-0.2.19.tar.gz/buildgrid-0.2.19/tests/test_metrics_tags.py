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


import pytest

from buildgrid.server.metrics_tags import tag_blob_age, tag_blob_size


@pytest.mark.parametrize(
    "size, expected_tag",
    [(0, "0_TO_2000"), (10001, "10000_TO_100000"), (2000000001, "2000000000_AND_ABOVE")],
)
def test_tag_blob_size(size, expected_tag):
    assert tag_blob_size(size) == expected_tag


@pytest.mark.parametrize(
    "age, expected_tag",
    [(0, "0_TO_60"), (172800001, "2880_TO_10080"), (2592000001, "43200_AND_ABOVE")],
)
def test_tag_blob_age(age, expected_tag):
    assert tag_blob_age(age) == expected_tag
