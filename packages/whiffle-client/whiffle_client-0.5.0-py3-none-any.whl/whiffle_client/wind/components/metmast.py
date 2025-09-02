from dataclasses import dataclass, field


@dataclass
class Metmast:
    name: str = field(default=None)
    longitude: float = field(default=None)
    latitude: float = field(default=None)
