from dataclasses import dataclass, field


@dataclass
class Geometries:
    les_domain: dict = field(default=None)
    meso_domain: dict = field(default=None)
    suggested_les_domain: dict = field(default=None)
