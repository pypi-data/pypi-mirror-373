from dataclasses import dataclass, field

from whiffle_client.wind.components.turbine import Turbine


@dataclass
class Windfarm:
    name: str = field(default=None)
    turbines: list[Turbine] = field(default=None)
    include_in_les: bool = field(default=True)
    thrust: bool = field(default=True)
    turbine_model_id: str = field(default=None)
    turbine_model_name: str = field(default=None)

    def __post_init__(self):
        are_all_turbine_dict = all([isinstance(t, dict) for t in self.turbines])
        if are_all_turbine_dict:
            self.turbines = [Turbine(**t) for t in self.turbines]
        are_all_turbine_turbine_obj = all(
            [isinstance(t, Turbine) for t in self.turbines]
        )
        if not are_all_turbine_turbine_obj:
            raise ValueError("All turbines must be of type Turbine or dict")
