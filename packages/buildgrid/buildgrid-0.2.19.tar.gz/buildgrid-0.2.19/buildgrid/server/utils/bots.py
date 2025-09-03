# Copyright (C) 2025 Bloomberg LP
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

from typing import Any

from buildgrid._protos.google.devtools.remoteworkers.v1test2.bots_pb2 import BotSession
from buildgrid.server.context import current_instance

BOT_CAPACITY_KEY = "capacity"


def get_bot_capacity(bot_session: BotSession) -> int:
    """Return the maximum capacity of the given ``BotSession``.

    Defaults to 1 if no capacity is specified.
    """
    if bot_session.worker.configs:
        for config in bot_session.worker.configs:
            if config.key == BOT_CAPACITY_KEY:
                return int(config.value)

    # If we got here, the bot didn't specify a capacity, so we assume
    # it only supports a single lease.
    return 1


def bot_log_tags(bot_session: BotSession) -> dict[str, Any]:
    """Return the dictionary of common log tags for a BotSession."""
    return {
        "instance_name": current_instance(),
        "request.bot_name": bot_session.name,
        "request.bot_id": bot_session.bot_id,
        "request.bot_status": bot_session.status,
        "request.leases": {lease.id: lease.state for lease in bot_session.leases},
        "request.capacity": get_bot_capacity(bot_session),
    }
