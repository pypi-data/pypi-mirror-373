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

import os
import re
from typing import Literal

import yaml
from pydantic import BaseModel, Field


class Acl(BaseModel):
    actor: str | None = Field(default=None)
    requests: list[str] | None = Field(default=None)
    subject: str | None = Field(default=None)
    workflow: str | None = Field(default=None)

    def is_authorized(
        self,
        request_name: str,
        actor: str | None = None,
        subject: str | None = None,
        workflow: str | None = None,
    ) -> bool:
        if self.actor is not None and not re.match(self.actor, actor or ""):
            return False

        if self.subject is not None and not re.match(self.subject, subject or ""):
            return False

        if self.workflow is not None and not re.match(self.workflow, workflow or ""):
            return False

        if self.requests is not None and request_name not in self.requests:
            return False

        return True


class InstanceAuthorizationConfig(BaseModel):
    allow: Literal["all"] | list[Acl]

    def is_authorized(
        self,
        request_name: str,
        actor: str | None = None,
        subject: str | None = None,
        workflow: str | None = None,
    ) -> bool:
        if self.allow == "all":
            return True

        return any(acl.is_authorized(request_name, actor, subject, workflow) for acl in self.allow)


def parse_auth_config(path: str | bytes | os.PathLike[str]) -> dict[str, InstanceAuthorizationConfig]:
    with open(path) as config_file:
        config = yaml.safe_load(config_file)
    return {
        instance_name: InstanceAuthorizationConfig(**instance_config)
        for instance_name, instance_config in config.items()
    }
