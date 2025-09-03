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


import typing

import boto3
import botocore

if typing.TYPE_CHECKING:
    from mypy_boto3_s3.client import S3Client

from buildgrid.server.cleanup.janitor.config import S3Config


def get_s3_client(config: S3Config) -> "S3Client":
    try:
        return boto3.client(
            "s3",
            endpoint_url=config.endpoint,
            aws_access_key_id=config.access_key,
            aws_secret_access_key=config.secret_key,
        )
    except Exception as e:
        raise ValueError("Failed to create an S3 client, check the S3 configuration options.") from e


def check_bucket_versioning(s3_client: "S3Client", bucket: str) -> bool:
    try:
        response = s3_client.get_bucket_versioning(Bucket=bucket)
        return bool(response.get("Status"))
    except botocore.exceptions.ClientError:
        return False
