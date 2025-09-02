#!/usr/bin/env python3

from whiffle_client.base_client import BaseClient
from whiffle_client.forecast.mapping import (
    AssetEndpoints,
    ForecastModelEndpoints,
    ObservationModelEndpoints,
)


# pylint: disable=too-many-instance-attributes
# pylint: disable=too-few-public-methods
class WhiffleForecastClient:
    """
    Client to connect to the Whiffle Forecast API
    """

    # NOTE: https://refactoring.guru/design-patterns/facade
    def __init__(self, access_token=None, url=None, session=None):
        self.session = BaseClient(access_token, url, session)

        # Map the asset simulation model endpoints
        self.asset_model = AssetEndpoints(self.session)
        self._map_asset_model_specs_methods()

        # Map the observation model specs endpoints
        self.observation_model = ObservationModelEndpoints(self.session)
        self._map_observation_model_specs_methods()

        # Map the forecast model specs endpoints
        self.forecast_model = ForecastModelEndpoints(self.session)
        self._map_forecast_model_specs_methods()

    def __repr__(self) -> str:
        return self.session.__repr__()

    def _map_asset_model_specs_methods(self):
        self.add_asset_model = self.asset_model.add
        self.get_all_asset_model = self.asset_model.get_all
        self.get_asset_model = self.asset_model.get

    def _map_observation_model_specs_methods(self):
        self.add_observation_model = self.observation_model.add
        self.get_all_observation_model = self.observation_model.get_all

    def _map_forecast_model_specs_methods(self):
        self.add_forecast_model = self.forecast_model.add
        self.get_forecast_model = self.forecast_model.get
