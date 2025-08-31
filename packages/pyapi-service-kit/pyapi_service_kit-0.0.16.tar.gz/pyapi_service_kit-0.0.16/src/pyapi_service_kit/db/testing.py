import logging
import json
from datetime import datetime
from dateutil.relativedelta import relativedelta

from nats.aio.client import Client as NATS
from nats.aio.msg import Msg
import polars as pl

from ..nats.nats_payload import NatsPayload

LOGGER = logging.getLogger(__name__)


async def simulate_db_update(
    nc: NATS,
    publish_subject: str,
    counter: int,
    initial_time: datetime,
    time_increment: relativedelta,
):
    parts = publish_subject.split(".")
    fqtn = ".".join(parts[-2:])

    ts = initial_time + time_increment * counter

    response = NatsPayload(
        type="json", data={"action": "update", "asof_utc": ts.isoformat()}
    )
    LOGGER.info(
        f"Simulating DB table update[{counter}] for {fqtn} at {response.data['asof_utc']}"
    )

    await nc.publish(publish_subject, response.as_bytes())
    LOGGER.info(f"Published DB table update for {fqtn}")


async def simulate_request_reply_json(msg: Msg) -> NatsPayload:
    request_data = json.loads(msg.data)
    return NatsPayload(type="json", data={"msg": f"Hello '{request_data['data']}'"})


async def simulate_request_reply_ipc(msg: Msg) -> NatsPayload:
    request_data = json.loads(msg.data)

    n = 10000
    data = pl.DataFrame({"a": list(range(n)), "b": [request_data["data"]] * n})

    return NatsPayload(type="ipc", data=data)
