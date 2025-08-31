import logging
from typing import Any, Mapping

from nats.js.client import JetStreamContext


LOGGER = logging.getLogger(__name__)


async def _try_delete_key_value_bucket(js: JetStreamContext, bucket_name: str):
    try:
        await js.delete_key_value(bucket_name)
        return True
    except Exception:
        return False


async def create_nats_key_value_bucket(js: JetStreamContext, config: Mapping[str, Any]):
    for kv_bucket_name, kv_config in config.items():
        try:
            if kv_config.get("recreate_if_exists", False):
                await _try_delete_key_value_bucket(js, kv_bucket_name)

            await js.create_key_value(bucket=kv_bucket_name, **kv_config["options"])
            LOGGER.info(f"KV bucket {kv_bucket_name} created")
        except Exception as e:
            LOGGER.error(f"Error creating KV bucket {kv_bucket_name}: {e}")
            raise
