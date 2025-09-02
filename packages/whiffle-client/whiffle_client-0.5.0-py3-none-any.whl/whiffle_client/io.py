from pathlib import Path
from typing import Union

import yaml
import yaml_include

from whiffle_client.loaders.csv import csv_loader_constructor

CHUNK_SIZE = 1024 * 1024


def stream_download_write_chunks_url(filename, url, session):
    """Download files in streaming fashion

    This method avoids memory issues when downloading large files

    Parameters
    ----------
    filename : str
        String of file to use to dump data
    url : str
        Url to download from
    session
        request session to use to perform download
    """
    with session.get_request(url, stream=True) as res:
        stream_download_write_chunks(filename=filename, res=res)


def stream_download_write_chunks(filename, res):
    """Download files in streaming fashion

    This method avoids memory issues when downloading large files

    Parameters
    ----------
    filename : str
        String of file to use to dump data
    res : requests.Response
        Requests response object with data to download
    """
    with open(filename, "wb") as file:
        file_size = float(res.headers.get("Content-Length", "nan"))
        downloaded = 0
        for chunk in res.iter_content(chunk_size=CHUNK_SIZE):
            if chunk:
                file.write(chunk)
                downloaded += len(chunk)
                print(
                    "Downloaded {:>5.1%}\r".format(downloaded / file_size),
                    end="",
                    flush=True,
                )


def download_write_chunks(filename, res):
    file = open(filename, "wb")
    file_size = float(res.headers["Content-Length"])
    downloaded = 0
    for chunk in res.iter_content(chunk_size=CHUNK_SIZE):
        if chunk:
            file.write(chunk)
            downloaded += len(chunk)
            print(
                "Downloaded {:>5.1%}\r".format(downloaded / file_size),
                end="",
                flush=True,
            )
    file.close()


def load_yaml_with_include(
    filename: Union[Path, str], relative_to_file: bool = False
) -> dict:
    """Load yaml file with yaml and csv includes.

    Parameters
    ----------
    filename : Path | str
        Yaml file to load.
    relative_to_file : bool, optional
        Whether the path should be relative to the yaml file to load.
        If set to False, the path will be relative to the current working
        directory.

    Returns
    -------
    dict
        Yaml file content as python dictionary.
    """
    base_dir = None
    if relative_to_file:
        base_dir = Path(filename).resolve().parents[0]
    yaml.add_constructor("!include", yaml_include.Constructor(base_dir=base_dir))
    yaml.add_constructor("!include-csv", csv_loader_constructor(base_dir=base_dir))
    with open(filename) as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
    del yaml.FullLoader.yaml_constructors["!include"]
    del yaml.FullLoader.yaml_constructors["!include-csv"]
    return data
