from pathlib import Path
from typing import Union

from whiffle_client.wind.components.turbine_model_specs import TurbineModelSpecs
from whiffle_client.decorators import load_data
from whiffle_client.common.mapping.base import BaseMapping


class TurbineModelSpecsEndpoints(BaseMapping):

    URL = "/api/v1/turbine-models"
    RESOURCE_TYPE = "TurbineModelSpecs"

    # Turbine models commands
    @load_data(TurbineModelSpecs)
    def add(
        self,
        data: Union[str, dict, Path, TurbineModelSpecs] = None,
    ) -> TurbineModelSpecs:
        """Add new Turbine Model

        Parameters
        ----------
        data : Union[str, dict, Path, TurbineModelSpecs], optional
            Either a path to a yaml, the data itself as a dictionary or a TurbineModelSpecs object
            containing the parameters that define the turbine model specs, by default None

        Returns
        -------
        TurbineModelSpecs
            Object instance of the turbine model
        """
        request = self.session.post_request(
            f"{self.session.server_url}{self.URL}", data=data
        )
        return TurbineModelSpecs.from_dict(request.json())

    @load_data(TurbineModelSpecs)
    def edit(
        self,
        turbine_model_id: str,
        data: Union[str, dict, Path, TurbineModelSpecs] = None,
    ) -> TurbineModelSpecs:
        """Edit existing Turbine Model

        Parameters
        ----------
        turbine_model_id : str
            Id of the turbine model
        data : Union[str, dict, Path, TurbineModelSpecs], optional
            Either a path to a yaml, the data itself as a dictionary or a TurbineModelSpecs object
            containing the parameters that define the turbine model specs, by default None

        Returns
        -------
        TurbineModelSpecs
            Object instance of the turbine model
        """
        request = self.session.put_request(
            f"{self.session.server_url}{self.URL}/{turbine_model_id}",
            data=data,
        )
        return TurbineModelSpecs.from_dict(request.json())

    def get_all(self) -> list[TurbineModelSpecs]:
        """Get a list of all the Turbine Models available to the user

        Returns
        -------
        list[TurbineModelSpecs]
            List of TurbineModelSpecs object instances
        """
        request = self.session.get_request(f"{self.session.server_url}{self.URL}")
        return [
            TurbineModelSpecs.from_dict(turbine_model_specs)
            for turbine_model_specs in request.json()
        ]

    def get(
        self,
        turbine_model_id: str = None,
        turbine_model_name: str = None,
    ) -> Union[TurbineModelSpecs, list[TurbineModelSpecs]]:
        """Get a Turbine Model

        Parameters
        ----------
        turbine_model_id : int, optional
            Id of the turbine model, by default None
        turbine_model_name : str, optional
            Turbine model name, by default None

        Returns
        -------
        Union[TurbineModelSpecs, list[TurbineModelSpecs]]
            Uniquely identidied TurbineModelSpecs object instance or list of TurbineModelSpecs

        Raises
        ------
        ValueError
            Raises error if either `turbine_model_id` or `turbine_model_name` are not provided
        """
        if turbine_model_id:
            return TurbineModelSpecs.from_dict(
                self.session.get_request(
                    f"{self.session.server_url}{self.URL}/{turbine_model_id}"
                ).json()
            )
        elif turbine_model_name:
            print(
                "WARN: Accessing turbine model specs by name. Using an `id` is recommended as name does not ensure uniqueness."
            )
            all_turbines = self.get_all()
            for turbine in all_turbines:
                if turbine.name == turbine_model_name:
                    return turbine
            else:
                raise ValueError(
                    f"Turbine with turbine_model_name: <{turbine_model_name}> not found"
                )
        else:
            raise ValueError(
                "Please provide either valid turbine_model_id or turbine_model_name"
            )

    def delete(
        self,
        turbine_model_id: str,
    ) -> TurbineModelSpecs:
        """Delete a Turbine Model

        Parameters
        ----------
        turbine_model_id : str
            Id of the turbine model

        Returns
        -------
        TurbineModelSpecs
            TurbineModelSpecs object instance of deleted turbine model
        """
        return TurbineModelSpecs.from_dict(
            self.session.delete_request(
                f"{self.session.server_url}{self.URL}/{turbine_model_id}"
            ).json()
        )

    def download(self):
        """Not implemented"""
        return super().download()
