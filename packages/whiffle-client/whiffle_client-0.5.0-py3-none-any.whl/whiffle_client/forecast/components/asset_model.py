from dataclasses import dataclass, field

from whiffle_client.common.components.base import BaseComponent


@dataclass
class AssetModel(BaseComponent):
    """Asset model"""

    # Metadata attributes
    name: str = field(default=None)
    location: dict[str, list[float]] = field(default=None)
    properties: list = field(default_factory=list)
