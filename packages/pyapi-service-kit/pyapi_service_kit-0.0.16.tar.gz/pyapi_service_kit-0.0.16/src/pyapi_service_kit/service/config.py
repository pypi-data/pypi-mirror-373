from dataclasses import dataclass
from typing import Optional

from pyapi_service_kit.service.guid import validate_guid


@dataclass
class ServiceConfig:
    instance_id: str
    time_service_subject: Optional[str] = None

    def __post_init__(self):
        self.instance_id = validate_guid(self.instance_id)
