import json
from datetime import datetime

from dataclasses import dataclass
from typing import Any, Dict, Literal, Optional

from polars_hist_db.utils import to_ipc_b64

EncodableType = Literal["json", "ipc", "epoch_ms", "error"]


def _encode_data(type: EncodableType, data: Any) -> str | int | bytes:
    encodable_result: str | int | bytes
    if type == "ipc":
        encodable_result = to_ipc_b64(data, "zlib").decode()
    elif type == "epoch_ms":
        if isinstance(data, datetime):
            encodable_result = int(data.timestamp() * 1000)
        else:
            assert isinstance(data, int), (
                "Data must be a integer object (milliseconds since epoch)"
            )
            encodable_result = data
    else:
        # its a json-encodable object
        encodable_result = data

    return encodable_result


@dataclass
class NatsPayload:
    type: EncodableType
    data: Any
    extra: Optional[Any] = None

    def as_bytes(self) -> bytes:
        encodable_result = _encode_data(self.type, self.data)

        payload: Dict[str, Any] = {
            "data": encodable_result,
            "type": self.type,
        }

        if self.extra:
            payload["extra"] = self.extra

        json_result = json.dumps(payload)
        result = json_result.encode("utf-8")
        return result

    def __str__(self) -> str:
        match self.type:
            case "json":
                return f"Response(type={self.type}, len={len(self.data)})"
            case "ipc":
                return f"Response(type={self.type}, rowcount={len(self.data)})"
            case "epoch_ms":
                return f"Response(type={self.type}, timestamp={self.data})"
            case "error":
                return f"Response(type={self.type}, error={self.data})"
            case _:
                return f"Response(type={self.type})"
