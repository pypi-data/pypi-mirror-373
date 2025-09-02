from datetime import datetime

import click
import yaml

from whiffle_client import Client
from whiffle_client.forecast import WhiffleForecastClient


@click.group()
@click.version_option(prog_name="whiffle-client")
def whiffle():
    pass


@whiffle.group()
def wind():
    """Wind api commands"""
    ...


@whiffle.group()
def task():
    """Task commands"""
    pass


@whiffle.group()
def config():
    """Edit config"""
    pass


@task.command()
@click.argument("number_of_tasks", default=10)
def list(number_of_tasks):
    """List tasks"""

    number_of_tasks = int(number_of_tasks)
    client = Client()
    tasks = client.get_tasks()
    click.echo(
        "{:33}{:11}{:16} {:16} progress".format(
            "task id", "status", "start time", "finish time"
        )
    )
    for task in tasks[-number_of_tasks:]:
        finished = task["finished"]
        if finished == None:
            task["finished"] = ""
        click.echo(
            "{task_id:33}{task_status:11}{received:17.16}{finished:17.16}{processed_steps}/{total_steps}".format(
                **task
            )
        )


@task.command()
@click.argument("file_path")
def run(file_path) -> str:
    """Run task type given a set of parameters.

    \b
    Parameters
    ----------
    file_path : str
        Path to (json|yaml) file containing parameters

    \b
    Returns
    -------
    str
        Name of the launched task
    """
    click.echo(f"run task with params: file_path={file_path}")
    client = Client()
    return client.process(file_path)


@config.command()
def login() -> str:
    """Log in into Whiffle's portal"""
    # Retrieve token from Whiffle's portal
    client = Client()
    client.get_token()
    click.echo(f"Token properly updated")


@config.command()
@click.argument("key")
@click.argument("value")
def edit(key, value) -> str:
    """Edit Whiffle configuration file

    \b
    Parameters
    ----------
    key : str
        Dot separated key value (e.g.: user.token)
    value : str
        Value to fill the configuration key with
    """
    client = Client()
    config_key = key.split(".")
    config = client.get_config()

    sub_config = config
    for sub_key in config_key[:-1]:
        if sub_key in sub_config:
            sub_config = sub_config[sub_key]
        else:
            raise KeyError(f"Key {sub_key} does not exist")
    try:
        if config_key[-1] not in sub_config:
            raise KeyError
        sub_config[config_key[-1]] = value
    except KeyError:
        raise KeyError(f"Key {config_key[-1]} does not exist")

    client.set_config(config=config)
    click.echo(f"{key} changed to {value}")


@config.command()
def list():
    """List configuration values"""

    client = Client()
    config = client.get_config()

    click.echo("Current configuration:\n-----\n")
    click.echo(yaml.safe_dump(config))
    click.echo("-----")


@task.command()
@click.argument("task_id")
def download(task_id):
    """Download task

    \b
    Parameters
    ----------
    task_id : str
    """
    click.echo(f"downloading task output {task_id}")
    client = Client()
    client.download(task_id)


@task.command()
@click.argument("task_id")
def attach(task_id):
    """attach task"""
    click.echo(f"attaching to the task {task_id}")
    client = Client()
    client.communicate(task_id)


@task.command()
@click.argument("task_id")
def cancel(task_id):
    """cancel task"""
    click.echo(f"cancelling task {task_id}")
    client = Client()
    client.cancel(task_id)


# Whiffle wind API commands


# Forecast group
@whiffle.group()
def forecast():
    """Forecast commands"""
    # pylint: disable=unnecessary-pass
    pass


@forecast.command()
@click.argument("number_of_assets", default=10)
def list_assets(number_of_assets):
    """List assets

    \b
    Parameters
    ----------
    number of assets : int
        Number of assets you want to see, by default 10

    \b
    Returns
    -------
    dict
        Table format of listed assets"""

    number_of_assets = int(number_of_assets)
    client = WhiffleForecastClient()
    assets = client.get_all_asset_model()
    name = "name"
    location = "location"
    click.echo(f"{name:33}{location:11}")
    for asset in assets[-number_of_assets:]:
        name = asset.name
        location = asset.location["coordinates"]
        click.echo(f"{name:33}{location}")


@forecast.command()
@click.argument("file_path")
def add_asset(file_path) -> str:
    """Add asset given a set of parameters.

    \b
    Parameters
    ----------
    file_path : str
        Path to (json|yaml) file containing parameters

    \b
    Returns
    -------
    dict
        JSON of added assets
    """
    click.echo(f"Add asset with params: file_path={file_path}")
    client = WhiffleForecastClient()
    return client.add_asset_model(**{"data": file_path})


@forecast.command()
@click.argument("asset_name")
def get_asset(asset_name):
    """Get asset

    \b
    Parameters
    ----------
    asset_name : str
        The name of the asset

    \b
    Returns
    -------
    dict
        JSON of asset"""

    client = WhiffleForecastClient()
    asset = client.get_asset_model(asset_name)
    name = "name"
    location = "location"
    click.echo(f"{name:33}{location:11}")
    name = asset.name
    location = asset.location["coordinates"]
    click.echo(f"{name:33}{location}")


@forecast.command()
@click.argument("asset_name")
@click.argument("quantity")
@click.argument("time_after")
@click.argument("time_before")
def list_observations(asset_name, quantity, time_before, time_after):
    """List observations

    \b
    Parameters
    ----------
    asset_name : str
        The name of the asset
    quantity : str
        The quantity of the observation, choose from: "PRODUCTION" "PRODUCTION_RAW"
        "SETPOINT_PLANNED", "CURTAILMENT_PLANNED", "REDISPATCH_PLANNED", "AVAILABILITY_PLANNED",
        "SETPOINT_REALIZED", "CURTAILMENT_REALIZED", "REDISPATCH_REALIZED", "AVAILABILITY_REALIZED",
        "WIND_SPEED", "WIND_DIRECTION", "TEMPERATURE" and "TOTAL_INPLANE_IRRADIANCE"
    time_after : str
        The time after which observations need to be listed
    time_before : str
        The time before which observations need to be listed

    \b
    Returns
    -------
    dict
        Table format of the observations"""
    time_after = datetime.fromisoformat(time_after)
    time_before = datetime.fromisoformat(time_before)
    client = WhiffleForecastClient()
    observations = client.get_all_observation_model(
        asset_name=asset_name,
        quantity=quantity.upper(),
        time_before=time_before,
        time_after=time_after,
    )

    click.echo(f"{'time':24}{'asset_name':24}{'quantity':24}{'value':10}")
    for observation in observations:
        asset_name = observation.asset_name
        quantity = observation.quantity
        time = observation.time
        value = observation.value
        click.echo(f"{time:24}{asset_name:24}{quantity:24}{value:10}")


@forecast.command()
@click.argument("file_path")
def add_observation(file_path) -> str:
    """Add observation(s) given a set of parameters.

    \b
    Parameters
    ----------
    file_path : str
        Path to (json|yaml) file containing parameters

    \b
    Returns
    -------
    dict
        JSON of the added observations
    """
    click.echo(f"Add observation with params: file_path={file_path}")
    client = WhiffleForecastClient()
    return client.add_observation_model(**{"data": file_path})


@forecast.command()
@click.argument("asset_name")
@click.argument("name", default="")
@click.argument("reference_time", default="")
def get_forecast(name, asset_name, reference_time):
    """Get forecast

    \b
    Parameters
    ----------
    asset_name : str
        The name of the asset
    name : str
        The name of the forecast (by default: blender)
    reference_time : str (isoformat)
        The reference time of the forecast (by default a get will be done on the latest forecast)

    \b
    Returns
    -------
    dict
        Table format of the forecast"""
    if reference_time not in ("latest", ""):
        reference_time = datetime.fromisoformat(reference_time).isoformat()
    client = WhiffleForecastClient()
    forecast_model = client.get_forecast_model(
        name=name, asset_name=asset_name, reference_time=reference_time
    )

    click.echo(
        f"Forecast: {forecast_model.name} with reference_time {forecast_model.reference_time} for asset "
        f"{forecast_model.asset_name}, results:"
    )
    click.echo(f"{'time':24}{'quantity':24}{'value':10}")
    for forecaststep in forecast_model.steps:
        quantity = forecaststep["quantity"]
        time = forecaststep["time"]
        value = forecaststep["value"]
        click.echo(f"{time:24}{quantity:24}{value:10}")


@forecast.command()
@click.argument("file_path")
def add_forecast(file_path) -> str:
    """Add forcast given a set of parameters.

    \b
    Parameters
    ----------
    file_path : str
        Path to (json|yaml) file containing parameters

    \b
    Returns
    -------
    dict
        JSON of the added forecast
    """
    click.echo(f"Add forecast with params: file_path={file_path}")
    client = WhiffleForecastClient()
    return client.add_forecast_model(**{"data": file_path})
