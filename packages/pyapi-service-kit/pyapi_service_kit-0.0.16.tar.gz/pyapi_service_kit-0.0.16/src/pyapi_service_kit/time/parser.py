from datetime import datetime
from dateutil.parser import isoparse
import pytz


def parse_zoned_iso(s: str) -> datetime:
    if "[" in s and s.endswith("]"):
        base, zone = s.split("[")
        zone = zone.strip("]")
    else:
        base = s
        zone = None

    dt = isoparse(base)
    if zone:
        try:
            tz = pytz.timezone(zone)
            dt = dt.astimezone(tz)
        except Exception:
            # Fallback: use the parsed offset
            pass
    return dt


def parse_granularity(granularity: str) -> int:
    granularity = granularity.lower().strip()

    if granularity.endswith("s"):
        seconds = float(granularity[:-1])
        return int(seconds * 1000)
    elif granularity.endswith("m"):
        minutes = float(granularity[:-1])
        return int(minutes * 60 * 1000)
    elif granularity.endswith("h"):
        hours = float(granularity[:-1])
        return int(hours * 60 * 60 * 1000)
    elif granularity.endswith("d"):
        days = float(granularity[:-1])
        return int(days * 24 * 60 * 60 * 1000)
    else:
        raise ValueError(
            f"Invalid granularity format: {granularity}. Use format like '20s', '1m', '5h', '1d'"
        )
