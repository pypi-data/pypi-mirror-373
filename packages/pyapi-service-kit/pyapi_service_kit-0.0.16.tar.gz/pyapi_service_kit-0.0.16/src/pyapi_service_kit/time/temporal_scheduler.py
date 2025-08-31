import logging
import pytz
from datetime import datetime
from typing import Dict, Any, Callable, List, Awaitable, Optional
import asyncio
from .parser import parse_granularity

LOGGER = logging.getLogger(__name__)


class TemporalScheduler:
    _borg: Dict[str, Any] = {}

    # for auto-complete
    now_epoch_ms: int
    subscribers: List[Dict[str, Any]]

    def __init__(self):
        self.__dict__ = self._borg
        if "subscribers" not in self._borg:
            self._borg["subscribers"] = []

    def get_datetime(self) -> datetime:
        return datetime.fromtimestamp(self.now_epoch_ms / 1000, tz=pytz.timezone("UTC"))

    def get_epoch_ms(self) -> int:
        return self.now_epoch_ms

    def update_from_epoch_ms(self, epoch_ms: int):
        self.now_epoch_ms = epoch_ms
        asyncio.create_task(self._check_subscribers(epoch_ms))

    def update_from_datetime(self, dt: datetime):
        self.update_from_epoch_ms(int(dt.timestamp() * 1000))

    def subscribe(
        self,
        subscription_id: str,
        cb: Callable[[int], Awaitable[None]],
        granularity: str,
    ):
        tick_ms = parse_granularity(granularity)

        # force tick on initial subscription
        next_tick = 0

        subscriber = {
            "subscription_id": subscription_id,
            "cb": cb,
            "granularity_ms": tick_ms,
            "next_tick": next_tick,
        }

        self.subscribers.append(subscriber)

    def unsubscribe(self, subscription_id: str):
        self.subscribers = [
            s for s in self.subscribers if s["subscription_id"] != subscription_id
        ]

    def _calc_next_trigger_time(self, current_ms: int, granularity_ms: int) -> int:
        ticks_passed = current_ms // granularity_ms
        next_tick = (ticks_passed + 1) * granularity_ms
        return next_tick

    async def _check_subscribers(self, current_time: Optional[int]):
        if current_time is None:
            return

        for subscriber in self.subscribers[
            :
        ]:  # Copy list to avoid modification during iteration
            if current_time >= subscriber["next_tick"]:
                try:
                    await subscriber["cb"](current_time)
                except Exception as e:
                    LOGGER.error(f"Error calling subscriber callback: {e}")

                # update next tick time
                subscriber["next_tick"] = self._calc_next_trigger_time(
                    current_time, subscriber["granularity_ms"]
                )

    def get_subscriber_count(self) -> int:
        return len(self.subscribers)

    def clear_subscribers(self):
        self.subscribers.clear()
