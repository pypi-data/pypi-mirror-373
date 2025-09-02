import os
import secrets
import time
import urllib
import webbrowser
from pathlib import Path
from time import sleep

import pkg_resources
import platformdirs
import requests
import yaml
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from whiffle_client.auth import (
    AUTH_STATE,
    ServerThread,
    auth0_url_encode,
    generate_challenge,
)
from whiffle_client.decorators import request_ok, with_token


class BaseClient:
    """
    Base class client to connect to Whiffle APIs
    """

    # API variables
    ENDPOINTS_URL: str = ""

    CONFIG_FILE_NAME = "whiffle_config.yaml"
    CONFIG_PACKAGE_FILE_LOCATION = pkg_resources.resource_filename(
        "whiffle_client", f"resources/{CONFIG_FILE_NAME}"
    )  # package resource path
    CONFIG_USER_FILE_LOCATION = (
        f"{platformdirs.user_config_dir('whiffle')}/{CONFIG_FILE_NAME}"
    )

    # Type method
    def __init__(self, access_token=None, url=None, session=None):
        """
        Initialize the client.

        Authentication order:
        1. `access_token` passed when creating class.
        2. token in CONFIG_FILE_PATH_LOCATION (JSON format)

        Parameters
        ----------
        access_token : str, optional
            Token for client session auth
        url : str, optional
            Url pointing to API
        """

        config = self.get_config()
        if access_token is None:
            access_token = config["user"]["access_token"]
        access_token_validator = config["user"].get("token_validator", None)
        if url is None:
            url = config["whiffle"]["url"]
        self.server_url = url

        if session is None:
            # More docs: https://urllib3.readthedocs.io/en/latest/reference/urllib3.util.html#urllib3.util.Retry
            status_forcelist = (500, 502, 503, 504)
            retry = Retry(
                total=5,  # Total number of retries to allow
                backoff_factor=0.1,  # Incremental time between retry requests
                status_forcelist=status_forcelist,  # A set of integer HTTP status codes that will force a retry on
            )
            adapter = HTTPAdapter(max_retries=retry)
            session = requests.Session()
            session.mount("http://", adapter)
            session.mount("https://", adapter)
        self.session = session

        self.session.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
            "Authorization-type": (
                "Integration" if access_token_validator == "zitadel" else None
            ),
        }

    def __repr__(self) -> str:
        return f"Whiffle wind client connected to url: {self.server_url}"

    def update_token_config(self, token):
        config = self.get_config()
        config["user"]["access_token"] = token["access_token"]
        config["user"]["refresh_token"] = token["refresh_token"]
        config["user"]["token_validator"] = token["token_validator"]
        config["user"]["expires_in"] = token["expires_in"]
        config["user"]["obtained_at"] = int(time.time())
        self.set_config(config=config)

    def get_token(self):
        config = self.get_config()
        IDP_BASE_URL = config["whiffle"]["idp_base_url"]
        CLIENT_ID = config["whiffle"]["client_id"]
        REDIRECT_URI = config["whiffle"]["redirect_uri"]

        verifier = auth0_url_encode(secrets.token_bytes(32))
        challenge = generate_challenge(verifier)
        base_url = IDP_BASE_URL + "/authorize?"
        url_parameters = {
            "client_id": CLIENT_ID,
            "redirect_uri": REDIRECT_URI,
            "scope": "profile openid email urn:zitadel:iam:user:resourceowner offline_access",
            "response_type": "code",
            "response_mode": "query",
            "code_challenge_method": "S256",
            "code_challenge": challenge.replace("=", ""),
            "state": auth0_url_encode(secrets.token_bytes(32)),
        }
        # Open the browser window to the login url
        webbrowser.open_new(base_url + urllib.parse.urlencode(url_parameters))
        server = ServerThread()
        # Start the server
        server.start()
        print(f"Waiting for log in callback")
        print(
            f"If no browser opens, please visit: {base_url}{urllib.parse.urlencode(url_parameters)}"
        )

        # Poll until the callback has been invoked or timeout
        waited = 2
        sleep(2)  # Usually in two seconds token has been refreshed
        while not AUTH_STATE["received_callback"] and waited < 60:
            sleep(1)
            waited += 1
            print(
                f"Waiting for callback for {waited} seconds, status {AUTH_STATE['received_callback']}",
                end="\r",
                flush=True,
            )
        if not AUTH_STATE["received_callback"]:
            raise RuntimeError("Timeout waiting for log in callback")
        server.shutdown()

        # received_state and error_message are global variable from auth_app callback
        if url_parameters["state"] != AUTH_STATE["received_state"]:
            raise RuntimeError(
                "Error: session replay or similar attack in progress. Please log out of all connections."
            )
        if AUTH_STATE["error_message"]:
            raise RuntimeError(
                "An error occurred: {}".format(AUTH_STATE["error_message"])
            )
        # Exchange the code for a token
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        body = {
            "grant_type": "authorization_code",
            "code": AUTH_STATE["code"],  # global variable from auth_app callback
            "redirect_uri": REDIRECT_URI,
            "client_id": CLIENT_ID,
            "code_verifier": verifier,
        }
        token_request = requests.post(
            IDP_BASE_URL + "token", headers=headers, data=body
        )
        if token_request.status_code != 200:
            raise RuntimeError(
                f"Error: failed to exchange code for token {token_request.status_code}"
            )

        token_request = token_request.json()
        token_request["token_validator"] = "zitadel"
        self.update_token_config(token_request)

    def refresh_token(self):
        config = self.get_config()
        IDP_BASE_URL = config["whiffle"]["idp_base_url"]
        CLIENT_ID = config["whiffle"]["client_id"]

        if "refresh_token" not in config["user"]:
            raise RuntimeError("No refresh token available, must log in again.")

        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "refresh_token",
            "refresh_token": config["user"]["refresh_token"],
            "client_id": CLIENT_ID,
        }
        token_refresh_response = requests.post(
            IDP_BASE_URL + "token", headers=headers, data=data
        )

        if token_refresh_response.status_code != 200:
            raise RuntimeError(
                f"Failed to refresh token: {token_refresh_response.status_code} {token_refresh_response.text}"
            )

        token_refresh_response = token_refresh_response.json()
        token_refresh_response["token_validator"] = "zitadel"
        self.update_token_config(token_refresh_response)

    def get_valid_access_token(self):
        """Return a valid access token, refreshing if needed."""
        config = self.get_config()
        if not config["user"]["access_token"]:
            self.get_token()
            config = self.get_config()

        if (
            time.time()
            > config["user"]["obtained_at"] + config["user"]["expires_in"] - 30
        ):
            self.refresh_token()
            config = self.get_config()

        return config["user"]["access_token"]

    def merge_configurations(self, base_config: dict, update_config: dict) -> dict:
        for key, value in update_config.items():
            if key not in base_config:
                base_config[key] = value
            elif isinstance(value, dict) and isinstance(base_config.get(key), dict):
                self.merge_configurations(base_config[key], value)

        return base_config

    def get_config(self) -> dict:
        """Gathers client configuration from local and updates with resources one.

        Returns
        -------
        dict
            Dictionary containing the configuration.

        Raises
        ------
        FileNotFoundError
            Raises error if no configuration found
        """
        with open(self.CONFIG_PACKAGE_FILE_LOCATION) as file_object:
            config = yaml.safe_load(file_object)

        # Merge default config with user config if present
        user_config = {}
        if Path(self.CONFIG_USER_FILE_LOCATION).exists():
            with open(self.CONFIG_USER_FILE_LOCATION) as file_object:
                user_config = yaml.safe_load(file_object)

        return self.merge_configurations(user_config, config)

    def set_config(self, config):
        config_file_path = self.CONFIG_USER_FILE_LOCATION
        os.makedirs(os.path.dirname(config_file_path), exist_ok=True)
        with open(config_file_path, "w") as file_object:
            yaml.safe_dump(config, file_object)

    @request_ok
    @with_token
    def get_request(self, url, **kwargs):
        return self.session.get(url, **kwargs)

    @request_ok
    @with_token
    def post_request(self, url, data=None, files=None):
        if files:
            return self.session.post(url, data=data, files=files)

        return self.session.post(url, json=data)

    @request_ok
    @with_token
    def put_request(self, url, data=None, files=None):
        if files:
            return self.session.put(url, data=data, files=files)

        return self.session.put(url, json=data)

    @request_ok
    @with_token
    def delete_request(self, url):
        return self.session.delete(url)
