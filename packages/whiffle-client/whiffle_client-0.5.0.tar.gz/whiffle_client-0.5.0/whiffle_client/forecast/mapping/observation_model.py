import datetime
from pathlib import Path
from typing import Union

from whiffle_client.forecast.components.observation_model import ObservationModel
from whiffle_client.decorators import load_data
from whiffle_client.common.mapping.base import BaseMapping


class ObservationModelEndpoints(BaseMapping):
    """Observation model endpoint

    Parameters
    ----------
    BaseMapping : Basemapping
        Base mapping
    """

    URL = "/api/v1/observations"
    RESOURCE_TYPE = "ObservationModel"

    # Observation models commands
    @load_data(ObservationModel)
    def add(
        self,
        data: Union[str, dict, Path, ObservationModel] = None,
    ) -> ObservationModel:
        """Add new Observation Model

        Parameters
        ----------
        data : Union[str, dict, Path, ObservationModel], optional
            Either a path to a yaml, the data itself as a dictionary or a ObservationModel object
            containing the parameters that define the observation model specs, by default None

        Returns
        -------
        ObservationModel
            Object instance of the observation model
        """
        request = self.session.post_request(
            f"{self.session.server_url}{self.URL}", data=data
        )
        return ObservationModel.from_dict(request.json())

    def get(self):
        """Get method for observation

        Raises
        ------
        NotImplementedError
            Not implemented; use get_all method
        """
        raise NotImplementedError(
            "Get method for observations not implemented; use get_all method."
        )

    # pylint: disable=arguments-differ
    def get_all(
        self,
        asset_name: str,
        quantity: str,
        time_after: datetime.datetime,
        time_before: datetime.datetime,
    ) -> list[ObservationModel]:
        """Get a list of all the Observation Models available to the user in predefined period

        Returns
        -------
        list[ObservationModel]
            List of ObservationModel object instances
        """
        observations = []
        data = self.session.get_request(
            f"{self.session.server_url}{self.URL}",
            params={
                "asset_name": asset_name,
                "quantity": quantity,
                "time_after": time_after.isoformat(),
                "time_before": time_before.isoformat(),
            },
        ).json()
        observations.extend(
            ObservationModel.from_dict(observation_model)
            for observation_model in data.get("results", [])
        )

        while isinstance(data.get("next"), str):
            data = self.session.get_request(data["next"]).json()
            observations.extend(
                ObservationModel.from_dict(observation_model)
                for observation_model in data.get("results", [])
            )
        return observations

    def edit(self):
        """Abstract method for edit

        Raises
        ------
        NotImplementedError
            Not implemented
        """
        raise NotImplementedError

    def delete(self):
        """Abstract method for delete

        Raises
        ------
        NotImplementedError
            Not implemented
        """
        raise NotImplementedError

    def download(self):
        """Abstract method for download

        Raises
        ------
        NotImplementedError
            Not implemented
        """
        raise NotImplementedError
