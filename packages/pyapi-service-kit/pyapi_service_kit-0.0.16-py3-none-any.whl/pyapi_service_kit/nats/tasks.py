import asyncio
from datetime import datetime, timedelta
import logging
from typing import Any, Callable, Awaitable
import pytz

from nats.aio.client import Client as NATS

from .nats_payload import NatsPayload

LOGGER = logging.getLogger(__name__)


async def check_health_task(nc: NATS, _subject: str, counter: int):
    if not nc.is_connected:
        LOGGER.warning("NATS connection lost, attempting to reconnect...")
    else:
        if counter % 10 == 0:
            LOGGER.info("NATS connection healthy")


async def subscribe_task(
    nc, listen_subject: str, cb: Callable[..., Awaitable[NatsPayload]]
):
    async def subscription_wrapper():
        try:
            await nc.subscribe(listen_subject, cb=cb)
            # Keep the task running until cancelled
            while True:
                await asyncio.sleep(3600)  # Sleep for a long time
        except Exception as e:
            LOGGER.error(f"Error in subscription {listen_subject}: {e}")
            raise

    LOGGER.info(f"[NATS Task] Subscribing to {listen_subject}")
    return await subscription_wrapper()


async def request_reply_task(
    nc: NATS, api_subject: str, cb: Callable[..., Awaitable[Any]]
):
    async def request_response_wrapper():
        try:
            LOGGER.info(f"Subscribing to {api_subject}")
            sub = await nc.subscribe(api_subject)
            async for msg in sub.messages:
                msg.headers = msg.headers or dict()
                msg.headers["received_ts"] = datetime.now(
                    pytz.timezone("UTC")
                ).isoformat()
                response = await cb(msg)
                msg.headers["processed_ts"] = datetime.now(
                    pytz.timezone("UTC")
                ).isoformat()
                await msg.respond(response.as_bytes())

        except Exception as e:
            LOGGER.error(f"Error in request_reply task {api_subject}: {e}")
            raise

    LOGGER.info(f"[NATS Task] Request-reply from {api_subject}")
    return await request_response_wrapper()


async def periodic_publisher_task(
    nc: NATS,
    publish_subject: str,
    timeout: timedelta,
    cb: Callable[..., Awaitable[NatsPayload]],
    *args: Any,
    **kwargs: Any,
):
    async def periodic_wrapper():
        counter = 0
        while True:
            try:
                await cb(nc, publish_subject, counter, *args, **kwargs)
                counter += 1
            except Exception as e:
                LOGGER.error(f"Error in periodic task {cb.__name__}: {e}")
            await asyncio.sleep(timeout.total_seconds())

    LOGGER.info(f"[NATS Task] Periodic publisher to {publish_subject}")
    return await periodic_wrapper()


async def triggered_js_publish_task(
    nc: NATS,
    listen_subject: str,
    publish_subject: str,
    cb: Callable[..., Awaitable[NatsPayload]],
):
    js = nc.jetstream()

    async def message_handler(msg):
        try:
            result = await cb(msg)
            # Publish to JetStream instead of regular NATS
            await js.publish(publish_subject, result.as_bytes())
            LOGGER.info(f"Published message to JetStream stream {publish_subject}")
        except Exception as e:
            LOGGER.error(f"Error handling message on {listen_subject}", exc_info=e)

    LOGGER.info(
        f"[NATS Task] Setup trigger for {listen_subject}, js_publish to {publish_subject}"
    )
    return await subscribe_task(nc, listen_subject, message_handler)


async def triggered_kv_put_task(
    nc: NATS,
    listen_subject: str,
    kv_bucket: str,
    key: str,
    cb: Callable[..., Awaitable[NatsPayload]],
):
    js = nc.jetstream()

    async def message_handler(msg):
        try:
            result = await cb(msg)
            kv = await js.key_value(kv_bucket)
            await kv.put(key, result.as_bytes())
            LOGGER.info(f"Updated key-value {kv_bucket}[{key}] {str(result)}")
        except Exception as e:
            LOGGER.error(f"Error handling message on {listen_subject}", exc_info=e)

    LOGGER.info(f"[NATS Task] Setup trigger for {listen_subject}, kv_put to {kv_bucket}[{key}]")
    return await subscribe_task(nc, listen_subject, message_handler)


async def once_kv_put_task(
    nc: NATS,
    kv_bucket: str,
    key: str,
    cb: Callable[..., Awaitable[NatsPayload]],
):
    js = nc.jetstream()

    async def once_task():
        try:
            result = await cb()
            kv = await js.key_value(kv_bucket)
            await kv.put(key, result.as_bytes())
            LOGGER.info(f"Updated key-value {kv_bucket}[{key}]")
        except Exception as e:
            LOGGER.error(f"Error handling message on {kv_bucket}[{key}]", exc_info=e)

    LOGGER.info(f"[NATS Task] Setup one-time kv_put to {kv_bucket}[{key}]")
    return await once_task()
