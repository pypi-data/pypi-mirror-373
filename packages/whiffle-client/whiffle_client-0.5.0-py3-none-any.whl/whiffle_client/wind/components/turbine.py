from dataclasses import dataclass, field


@dataclass
class Turbine:
    name: str = field(default=None)
    longitude: float = field(default=None)
    latitude: float = field(default=None)
