import yaml

from tests.conftest import (
    mock_new_task_response,
    get_default_task,
    default_task_path,
    task_with_yaml_include_path,
)
from whiffle_client import Client


class TestAPI:
    def test_init_client_with_default_params(self):
        client = Client()
        config = client.get_config()
        assert client.server_url == config["whiffle"]["url"]
        assert config["user"]["access_token"] in client.session.headers["Authorization"]

    def test_init_client_with_given_params(self):
        token = "test_token"
        url = "https://test_url.com"
        client = Client(token, url)

        assert client.server_url == url
        assert token in client.session.headers["Authorization"]

    def test_new_task_from_dict(self, mocker):
        task = get_default_task()
        client = Client()
        mock_new_task_response(mocker)
        task_id = client.new_task(task)
        assert type(task_id) == str

    def test_new_task_from_json(self, mocker):
        client = Client()
        mock_new_task_response(mocker)
        task_id = client.new_task(default_task_path)
        assert type(task_id) == str

    def test_new_task_from_yaml(self, mocker, tmp_path):
        task = get_default_task()
        path = f"{tmp_path}/task.yaml"
        with open(path, "w") as f:
            yaml.safe_dump(task, f)
        client = Client()
        mock_new_task_response(mocker)
        task_id = client.new_task(path)
        assert type(task_id) == str

    def test_new_task_from_yaml_with_include(self, mocker, tmp_path):
        task = get_default_task()
        client = Client()
        mock_new_task_response(mocker)
        task_id = client.new_task(task_with_yaml_include_path)
        assert type(task_id) == str

    def test_new_task_with_warnings(self, mocker, capsys):
        warnings = {"version": "incorrect version"}

        task = get_default_task()
        client = Client()
        mock_new_task_response(mocker, warnings)
        client.new_task(task)
        captured = capsys.readouterr()
        assert "incorrect version" in captured.out
