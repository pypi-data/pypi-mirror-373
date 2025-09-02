import datetime
from dataclasses import dataclass, field

from whiffle_client.common.components.base import BaseComponent


# pylint: disable=duplicate-code
@dataclass
class ObservationModel(BaseComponent):
    """Observation model"""

    time: datetime.datetime = field(default=None)
    quantity: str = field(default=None)
    value: float = field(default=None)
    asset_name: int = field(default=None)
