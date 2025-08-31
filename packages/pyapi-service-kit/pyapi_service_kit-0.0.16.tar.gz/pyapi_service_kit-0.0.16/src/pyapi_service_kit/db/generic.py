import json
import logging
from typing import Awaitable, Callable

from polars import DataFrame
from polars_hist_db.core import TimeHint
from sqlalchemy.engine import Connection

from nats.aio.msg import Msg

from ..nats.nats_payload import NatsPayload
from ..time.parser import parse_zoned_iso

LOGGER = logging.getLogger(__name__)

QueryFn = Callable[[Connection, TimeHint], Awaitable[DataFrame]]


async def run_query_asof(
    msg: Msg,
    query_fn: QueryFn,
    connection: Connection,
) -> NatsPayload:
    try:
        payload = json.loads(msg.data)
        asof_utc = parse_zoned_iso(payload["data"]["asof_utc"])
        LOGGER.info(f"Running query for {msg.subject} asof {asof_utc.isoformat()}")
        time_hint = TimeHint(mode="asof", asof_utc=asof_utc)
        return await _run_query_with_time_hint(time_hint, query_fn, connection)
    except Exception as e:
        return NatsPayload(type="error", data=str(e))


async def run_query_simple(
    msg: Msg,
    query_fn: QueryFn,
    connection: Connection,
) -> NatsPayload:
    LOGGER.info(f"Running query for {msg.subject}")

    time_hint = TimeHint(mode="none")
    return await _run_query_with_time_hint(time_hint, query_fn, connection)


async def _run_query_with_time_hint(
    time_hint: TimeHint,
    query_fn: QueryFn,
    connection: Connection,
) -> NatsPayload:
    df = await query_fn(connection, time_hint)
    return NatsPayload(type="ipc", data=df)
