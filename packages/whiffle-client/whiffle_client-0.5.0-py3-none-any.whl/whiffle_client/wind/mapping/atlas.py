import os

from whiffle_client.common.mapping.base import BaseMapping
from whiffle_client.io import stream_download_write_chunks


VALID_FORMATS = ["nc", "csv"]


class AtlasEndpoints(BaseMapping):
    URL = "/api/v1/atlas"

    def download_point(
        self,
        longitude: float,
        latitude: float,
        format: str = "nc",
        dataset: str = "meso",
        output_name: str = None,
        output_dir: str = None,
    ):
        """Download atlas data

        Parameters
        ----------
        longitude : float
            Longitude location of data to download
        latitude : float
            Latitude location of data to download
        format : str, optional
            Format in which the data will be downloaded
        dataset : str, optional
            Requested dataset for data download
        output_name : str, optional
            Output file name to use if provided, else use same name as remote file, by default None
        output_dir : str, optional
            Output directory path, by default None

        Raises
        ------
        ValueError
            Raises error if file format is not in the valid file formats
        """

        if format not in VALID_FORMATS:
            raise ValueError(
                f"Atlas download request has to be one of the valid formats: {VALID_FORMATS}"
            )

        download_url = f"{self.session.server_url}{self.URL}/time-series.{format}?latitude={latitude}&longitude={longitude}"
        download_response = self.session.get_request(download_url, stream=True)

        # NOTE: If provided, use given name, else take same name as response filename or return default
        local_filename = (
            output_name
            or download_response.headers.get(
                "Content-Disposition", f"filename=atlas_data.{format}"
            ).split("filename=")[1]
        )
        output_dir = output_dir or os.getcwd()

        print(
            f"Fetch atlas:{dataset} data at location "
            f"longitude:{longitude} latitude:{latitude} and "
            f"store it at: `{output_dir}/{local_filename}`"
        )
        stream_download_write_chunks(
            f"{output_dir}/{local_filename}", download_response
        )

    download = download_point
