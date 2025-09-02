from pathlib import Path
from typing import Union

from whiffle_client.forecast.components.forecast_model import ForecastModel
from whiffle_client.decorators import load_data
from whiffle_client.common.mapping.base import BaseMapping


class ForecastModelEndpoints(BaseMapping):
    """Forecast model endpoint

    Parameters
    ----------
    BaseMapping : Basemapping
        Base mapping
    """

    URL = "/api/v1/forecasts"
    RESOURCE_TYPE = "ForecastModel"

    # Forecast model commands
    @load_data(ForecastModel)
    def add(
        self,
        data: Union[str, dict, Path, ForecastModel] = None,
    ) -> ForecastModel:
        """Add new Forecast Model

        Parameters
        ----------
        data : Union[str, dict, Path, ForecastModel], optional
            Either a path to a yaml, the data itself as a dictionary or a ForecastModel object
            containing the parameters that define the forecast model specs, by default None

        Returns
        -------
        ForecastModel
            Object instance of the forecast  model
        """
        request = self.session.post_request(
            f"{self.session.server_url}{self.URL}", data=data
        )
        return ForecastModel.from_dict(request.json())

    # pylint: disable=arguments-differ
    def get(
        self,
        asset_name: str,
        name: str = "",
        reference_time: str = "",
    ):
        """Get Forecasts

        Parameters
        ----------
        reference_time : str
            The timestamp of the forecast to get
        asset_name : str
            The name of the asset to get the forecast for
        name : str, optional
            Forecast name, by default "name"
        """
        params = {}
        for key, value in [
            ("asset_name", asset_name),
            ("name", name),
            ("reference_time", reference_time),
        ]:
            if value != "":
                params[key] = value

        url = f"{self.session.server_url}{self.URL}"
        request = self.session.get_request(
            url,
            params=params,
        )
        return ForecastModel.from_dict(request.json())

    def get_all(self):
        """Abstract method for get_all

        Raises
        ------
        NotImplementedError
            Not implemented
        """
        raise NotImplementedError

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
