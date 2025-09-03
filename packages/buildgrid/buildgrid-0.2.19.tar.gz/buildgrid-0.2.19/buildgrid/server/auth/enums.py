# Copyright (C) 2023 Bloomberg LP
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

from enum import Enum


class AuthMetadataMethod(Enum):
    # No authorization:
    NONE = "none"
    # Authorize based on client identity headers:
    HEADERS = "headers"
    # JWT based authorization:
    JWT = "jwt"


class AuthMetadataAlgorithm(Enum):
    # No encryption involved:
    UNSPECIFIED = "unspecified"
    # JWT related algorithms:
    JWT_ES256 = "es256"  # ECDSA signature algorithm using SHA-256 hash algorithm
    JWT_ES384 = "es384"  # ECDSA signature algorithm using SHA-384 hash algorithm
    JWT_ES512 = "es512"  # ECDSA signature algorithm using SHA-512 hash algorithm
    JWT_HS256 = "hs256"  # HMAC using SHA-256 hash algorithm
    JWT_HS384 = "hs384"  # HMAC using SHA-384 hash algorithm
    JWT_HS512 = "hs512"  # HMAC using SHA-512 hash algorithm
    JWT_PS256 = "ps256"  # RSASSA-PSS using SHA-256 and MGF1 padding with SHA-256
    JWT_PS384 = "ps384"  # RSASSA-PSS signature using SHA-384 and MGF1 padding with SHA-384
    JWT_PS512 = "ps512"  # RSASSA-PSS signature using SHA-512 and MGF1 padding with SHA-512
    JWT_RS256 = "rs256"  # RSASSA-PKCS1-v1_5 signature algorithm using SHA-256 hash algorithm
    JWT_RS384 = "rs384"  # RSASSA-PKCS1-v1_5 signature algorithm using SHA-384 hash algorithm
    JWT_RS512 = "rs512"  # RSASSA-PKCS1-v1_5 signature algorithm using SHA-512 hash algorithm
