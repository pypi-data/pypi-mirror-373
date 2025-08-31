import logging
from typing import List

from nats.js.client import JetStreamContext

from .config import StreamConfig


LOGGER = logging.getLogger(__name__)


async def try_delete_stream(js: JetStreamContext, stream_name: str):
    try:
        await js.delete_stream(stream_name)
        return True
    except Exception:
        return False


async def create_jetstream_streams(js: JetStreamContext, config: List[StreamConfig]):
    for stream_config in config:
        await _create_jetstream_stream(js, stream_config)


async def _create_jetstream_stream(js: JetStreamContext, config: StreamConfig):
    try:
        if config.recreate_if_exists:
            await try_delete_stream(js, config.name)

        await js.add_stream(name=config.name, **config.options)
        LOGGER.info(f"JetStream stream {config.name} created")
    except Exception as e:
        LOGGER.error(f"Error creating JetStream stream {config.name}: {e}")
        raise
