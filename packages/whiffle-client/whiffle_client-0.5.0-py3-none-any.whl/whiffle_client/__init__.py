from whiffle_client.client import Client, CONFIG_FILE_PATH_LOCATIONS
from importlib.metadata import version

__version__ = version("whiffle_client")

__all__ = [Client, CONFIG_FILE_PATH_LOCATIONS]
