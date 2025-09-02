from dataclasses import asdict, dataclass, field

from whiffle_client.common.components.base import BaseComponent
from whiffle_client.wind.components.dates import Dates
from whiffle_client.wind.components.domain import Domain
from whiffle_client.wind.components.metmast import Metmast
from whiffle_client.wind.components.turbine import Turbine
from whiffle_client.wind.components.windfarm import Windfarm


@dataclass
class WindSimulationTask(BaseComponent):
    # Metadata attributes
    reference_code: str = field(default=None)
    name: str = field(default=None)

    # Time attributes
    dates: Dates = field(default=None)
    simulation_type: str = field(default="time_series")

    # Domain/object/geolocated elements attributes
    windfarms: list[Windfarm] = field(default_factory=list)
    metmasts: list[Metmast] = field(default_factory=list)
    metmasts_heights: list[float] = field(default_factory=list)
    additional_area: Domain = field(default=None)

    # Output attributes
    wind_resource_grid_heights: list[float] = field(default_factory=list)
    fields_heights: list[float] = field(default_factory=list)

    def __post_init__(self):
        if isinstance(self.metmasts, list):
            self.metmasts = [
                Metmast(
                    name=metmast["name"],
                    longitude=metmast["longitude"],
                    latitude=metmast["latitude"],
                )
                for metmast in self.metmasts
            ]
        elif isinstance(self.metmasts, dict):
            self.metmasts = [
                Metmast(name=name, latitude=latitude, longitude=longitude)
                for name, (longitude, latitude) in zip(
                    self.metmasts["name"], self.metmasts["location"]
                )
            ]

        if isinstance(self.windfarms, list):
            self.windfarms = [Windfarm(**windfarm) for windfarm in self.windfarms]
        elif isinstance(self.windfarms, dict):
            self.windfarms = [
                Windfarm(
                    name=windfarm_name,
                    include_in_les=windfarm["include_in_les"],
                    thrust=windfarm["thrust"],
                    turbine_model_id=windfarm.get("turbine_model_id", None),
                    turbine_model_name=windfarm.get("turbine_model_name", None),
                    turbines=[
                        Turbine(
                            name=name,
                            longitude=longitude,
                            latitude=latitude,
                        )
                        for name, (longitude, latitude) in zip(
                            windfarm["name"], windfarm["location"]
                        )
                    ],
                )
                for windfarm_name, windfarm in self.windfarms.items()
            ]

    def _get_api_params(self):
        params = asdict(self)

        if self.metmasts:
            params["metmasts"] = [
                {
                    "name": metmast.name,
                    "longitude": metmast.longitude,
                    "latitude": metmast.latitude,
                }
                for metmast in self.metmasts
            ]

        if self.windfarms:
            params["windfarms"] = [
                {
                    "name": windfarm.name,
                    "include_in_les": windfarm.include_in_les,
                    "thrust": windfarm.thrust,
                    "turbine_model_name": windfarm.turbine_model_name,
                    "turbines": [
                        {
                            "name": turbine.name,
                            "longitude": turbine.longitude,
                            "latitude": turbine.latitude,
                        }
                        for turbine in windfarm.turbines
                    ],
                }
                for windfarm in self.windfarms
            ]

        return params
