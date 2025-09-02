from dataclasses import dataclass, field
from whiffle_client.common.components.base import BaseComponent


@dataclass
class TurbineModelSpecs(BaseComponent):
    name: str = field(default=None)
    hub_height: float = field(default=None)
    rotor_diameter: float = field(default=None)
    rated_power: float = field(default=None)
    reference_density: float = field(default=None)
    reference_turbulence_intensity: float = field(default=None)
    reference_windspeed: list[float] = field(default=None)
    thrust_coefficient: list[float] = field(default=None)
    power: list[float] = field(default=None)
    public: bool = field(default_factory=bool)
