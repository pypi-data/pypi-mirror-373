from dataclasses import dataclass, field


@dataclass
class Geometry:
    coordinates: list[list[list[float]]] = field(default=None)
    type: str = field(default="Polygon")


@dataclass
class Domain:
    geometry: Geometry = field(default_factory=dict)
    properties: dict = field(default_factory=dict)
    type: str = field(default="Feature")
