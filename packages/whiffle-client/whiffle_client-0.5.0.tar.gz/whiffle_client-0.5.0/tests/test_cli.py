import subprocess

import yaml
from click.testing import CliRunner

from tests.conftest import mock_new_task_response, default_task_path
from whiffle_client import Client
from whiffle_client.entrypoints import whiffle

runner = CliRunner()


class TestCli:
    def test_list_config(self):
        config = Client().get_config()
        res = runner.invoke(whiffle, ["config", "list"])
        assert yaml.safe_dump(config) in res.output

    def test_edit_config(self):
        token = "test_token"
        res = runner.invoke(whiffle, ["config", "edit", "user.access_token", token])
        assert token in res.output
        res = runner.invoke(whiffle, ["config", "list"])
        assert token in res.output

    def test_run_task(self, mocker):
        mock_new_task_response(mocker)
        mock = mocker.patch("whiffle_client.Client.process")
        runner.invoke(whiffle, ["task", "run", default_task_path])
        mock.assert_called_once()

    def test_task_list(self, mocker):
        mock_new_task_response(mocker)
        mock = mocker.patch("whiffle_client.Client.get_tasks")
        runner.invoke(whiffle, ["task", "list"])
        mock.assert_called_once()

    def test_download_task(self, mocker):
        mock_new_task_response(mocker)
        mock = mocker.patch("whiffle_client.Client.download")
        res = runner.invoke(whiffle, ["task", "download", "123"])
        assert not "Error" in res.output, res.output
        mock.assert_called_once()

    def test_attach_task(self, mocker):
        mock_new_task_response(mocker)
        mock = mocker.patch("whiffle_client.Client.communicate")
        runner.invoke(whiffle, ["task", "attach", "123"])
        mock.assert_called_once()

    def test_cancel_task(self, mocker):
        mock_new_task_response(mocker)
        mock = mocker.patch("whiffle_client.Client.cancel")
        res = runner.invoke(whiffle, ["task", "cancel", "123"])
        assert not "Error" in res.output, res.output
        mock.assert_called_once()

    def test_version(self):
        git_version = subprocess.check_output(["git", "describe"]).decode()
        res = runner.invoke(whiffle, ["--version"])
        # res.output = "whiffle-client, version 0.2.9.post1+git.adbca4e1.dirty"
        cli_version = ".".join(res.output.split(" version ")[-1].split(".")[:3])

        print(res.output, cli_version, res.output.split(" ")[2][:5])
        print(git_version, git_version.split("-")[0], git_version[:5])

        assert cli_version.strip() == git_version.split("-")[0].strip()
