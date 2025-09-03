from __future__ import annotations

import enum
import os
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Final


@dataclass
class Server:
    host: str
    port: int
    ae: str


class ActionType(enum.IntEnum):
    DELETE = 1


def get_servers() -> dict[str, Server]:
    servers: dict[str, Server] = {}

    with Path(os.environ['SERVERS_TOML']).open('rb') as f:
        data = tomllib.load(f)

    for k, v in data['server'].items():
        servers[k] = Server(v['host'], int(v['port']), v['ae'])

    return servers


TIMEOUT: Final[int] = 15 * 60  # Timeout 15 min
