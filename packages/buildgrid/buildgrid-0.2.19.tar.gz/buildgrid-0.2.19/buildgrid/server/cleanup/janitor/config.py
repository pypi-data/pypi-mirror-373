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


import os
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field

from buildgrid.server.app.settings.config import populate_monitoring_config
from buildgrid.server.app.settings.parser import load_sql_connection, string_definitions
from buildgrid.server.monitoring import set_monitoring_bus
from buildgrid.server.sql.provider import SqlProvider


class S3Config(BaseModel):
    access_key: str
    bucket_regex: str
    endpoint: str
    path_prefix: str
    hash_prefix_size: int = Field(default=0)
    secret_key: str
    sleep_interval: int | None = Field(default=None)
    max_batch_size: int = Field(default=1000)
    batch_sleep_interval: float | None = Field(default=None)


class SQLStorageConfig(BaseModel):
    sql: SqlProvider
    sql_ro: SqlProvider
    sleep_interval: int | None = Field(default=None)
    batch_size: int
    batch_sleep_interval: float | None = Field(default=None)

    model_config = ConfigDict(arbitrary_types_allowed=True)


class RedisConfig(BaseModel):
    db: int | None = Field(default=None)
    dns_srv_record: str | None = Field(default=None)
    index_prefix: str
    key_batch_size: int
    password: str | None = Field(default=None)
    host: str | None = Field(default=None)
    port: int | None = Field(default=None)
    sentinel_master_name: str | None = Field(default=None)


class JanitorConfig(BaseModel):
    redis: RedisConfig | None = Field(default=None)
    sleep_interval: int | None = Field(default=None)
    s3: S3Config | None = Field(default=None)
    sql_storage_config: SQLStorageConfig | None = Field(default=None)
    sql_connection_string: str | None = Field(default=None)


def parse_janitor_config(path: str | bytes | os.PathLike[str]) -> JanitorConfig:
    class Loader(yaml.SafeLoader):
        def string_loader(self, node: yaml.MappingNode) -> Any:
            return string_definitions[node.tag](node.value)

    for kind in string_definitions:
        Loader.add_constructor(kind, Loader.string_loader)

    with open(path) as config_file:
        config = yaml.load(config_file, Loader=Loader)
    if "sql_storage_config" in config:
        config["sql_storage_config"]["sql"] = load_sql_connection(**config["sql_storage_config"]["sql"])
        config["sql_storage_config"]["sql_ro"] = load_sql_connection(**config["sql_storage_config"]["sql_ro"])
    if "monitoring" in config:
        monitoring_config = populate_monitoring_config(config["monitoring"])
        if monitoring_config is not None:
            set_monitoring_bus(monitoring_config)
    return JanitorConfig(**config)
