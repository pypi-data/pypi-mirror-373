import asyncio
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from nats.aio.client import Client as NATS
from nats.js.client import JetStreamContext
from .core import make_nats_client


@dataclass
class StreamConfig:
    name: str
    options: Dict[str, Any]
    recreate_if_exists: bool = False


@dataclass
class NatsConfig:
    servers: List[str]
    options: Dict[str, Any]
    streams: List[StreamConfig]

    # Cached connection and JetStream context
    _lock: asyncio.Lock = asyncio.Lock()
    _nc: Optional[NATS] = None
    _js: Optional[JetStreamContext] = None

    async def get_connection(self) -> tuple[NATS, JetStreamContext]:
        async with self._lock:
            if self._nc is None or (
                self._nc.is_closed and not self._nc.is_reconnecting
            ):
                self._nc, self._js = await make_nats_client(
                    servers=self.servers,
                    options=self.options,
                )

        assert self._nc is not None
        assert self._js is not None
        return self._nc, self._js

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NatsConfig":
        return cls(
            streams=[
                StreamConfig(**stream)
                for stream in data.get("streams", [])
                if isinstance(stream, dict)
            ],
            options=data.get("options", {}),
            servers=data.get("servers", []),
        )
