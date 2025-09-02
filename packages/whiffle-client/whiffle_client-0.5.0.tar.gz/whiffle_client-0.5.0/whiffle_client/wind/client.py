#!/usr/bin/env python3

from whiffle_client.base_client import BaseClient
from whiffle_client.wind.mapping.atlas import AtlasEndpoints
from whiffle_client.wind.mapping.turbine_model_specs import TurbineModelSpecsEndpoints
from whiffle_client.wind.mapping.wind_simulation_tasks import (
    WindSimulationTaskEndpoints,
)


class WindSimulationClient:
    """
    Client to connect to the Whiffle Wind API
    """

    # NOTE: https://refactoring.guru/design-patterns/facade
    def __init__(self, access_token=None, url=None, session=None):
        self.session = BaseClient(access_token, url, session)

        # Map the turbine model specs endpoints
        self.turbine_model = TurbineModelSpecsEndpoints(self.session)
        self._map_turbine_model_specs_methods()

        # Map the wind simulation model endpoints
        self.wind_simulation_task = WindSimulationTaskEndpoints(self.session)
        self._map_wind_simulation_model_methods()

        # Map the atlas endpoints
        self.atlas = AtlasEndpoints(self.session)
        self._map_atlas_methods()

    def __repr__(self) -> str:
        return self.session.__repr__()

    def _map_turbine_model_specs_methods(self):
        self.add_turbine_model = self.turbine_model.add
        self.edit_turbine_model = self.turbine_model.edit
        self.get_all_turbine_models = self.turbine_model.get_all
        self.get_turbine_model = self.turbine_model.get
        self.delete_turbine_model = self.turbine_model.delete

    def _map_wind_simulation_model_methods(self):
        self.add_wind_simulation_task = self.wind_simulation_task.add
        self.edit_wind_simulation_task = self.wind_simulation_task.edit
        self.get_all_wind_simulation_tasks = self.wind_simulation_task.get_all
        self.get_wind_simulation_task = self.wind_simulation_task.get
        self.delete_wind_simulation_task = self.wind_simulation_task.delete
        self.download_wind_simulation_task = self.wind_simulation_task.download
        self.submit_wind_simulation_task = self.wind_simulation_task.submit

    def _map_atlas_methods(self):
        self.download_atlas_location = self.atlas.download_point
