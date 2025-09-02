from pathlib import Path
from typing import Union

from whiffle_client.forecast.components.asset_model import AssetModel
from whiffle_client.decorators import load_data
from whiffle_client.common.mapping.base import BaseMapping


class AssetEndpoints(BaseMapping):
    """Asset model endpoint

    Parameters
    ----------
    BaseMapping : Basemapping
        Base mapping
    """

    URL = "/api/v1/assets"
    RESOURCE_TYPE = "Asset"

    # pylint: disable=arguments-differ
    @load_data(AssetModel)
    def add(
        self,
        data: Union[str, dict, Path, AssetModel] = None,
    ) -> AssetModel:
        """Add new Asset

        Parameters
        ----------
        data : Union[str, dict, Path, AssetModel], optional
            Either a path to a yaml, the data itself as a dictionary or a AssetModel object
            containing the parameters that define the Asset, by default None

        Returns
        -------
        AssetModel
            Object instance of the wind simulation
        """
        asset = self.session.post_request(
            f"{self.session.server_url}{self.URL}", data=data
        )
        return AssetModel.from_dict(asset.json())

    def get(self, asset_name: str) -> AssetModel:
        """Get a Asset

        Parameters
        ----------
        asset_name : str
            Name of the asset

        Returns
        -------
        AssetModel
            Requested AssetModel
        """
        return AssetModel.from_dict(
            self.session.get_request(
                f"{self.session.server_url}{self.URL}/{asset_name}",
            ).json()
        )

    # pylint: disable=arguments-differ
    def get_all(self) -> list[AssetModel]:
        """Get a list of all Assets available to the user

        Returns
        -------
        list[AssetModel]
            List of AssetModels object instances
        """
        assets = []
        request = self.session.get_request(f"{self.session.server_url}{self.URL}")
        data = request.json()
        assets.extend(AssetModel.from_dict(asset) for asset in data.get("results", []))
        while isinstance(data.get("next"), str):
            data = self.session.get_request(data["next"]).json()
            assets.extend(
                AssetModel.from_dict(asset) for asset in data.get("results", [])
            )
        return assets

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
