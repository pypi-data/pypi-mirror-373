# Whiffle client

This client allows running atmospheric large-eddy simulations (LES) with Whiffle's GPU-resident model <https://whiffle.nl/>.

## Getting started

### Install client

`whiffle-client` can be installed with `pip` as follows:

`pip install whiffle-client` or `pip install "whiffle-client[analysis]"` to include data-analysis packages.


### Configure credentials 

The client requires an access token, which you can configure with the command line interface by executing:

`whiffle config login`

This will open interactive browser portal where user/password log in can be done. From there, token will be automatically stored on local configuration for further usage.

NOTE: configuration will be stored on user config directory.
> Unix  systems `~/.config/whiffle/whiffle_config.yaml`

> macOS systems `~/Library/Application Support/whiffle/whiffle_config.yaml`

> Windows systems `%USERPROFILE%\AppData\Local\whiffle\whiffle_config.yaml`

current configuration (including token) can be listed with:

`whiffle config list`


## Run a task with Whiffle Wind API client

The process to run a simulation using Whiffle Wind client is as simple as:
- Instantiate the client
- Add some turbine model specs (if necessary)
- Define the wind simulation parameters
- Submit wind simulation and check progress
- Download results

> 💡: All this steps are compatible with Whiffle Wind user interface https://whiffle.cloud and moving back and forth from the client to the UI is possible in every step.

### Instantiate the client

To launch a simulation first a client object needs to be instantiated.

```python
from whiffle_client.wind import WindSimulationClient

client = WindSimulationClient()
```

### Add turbine model specs
Afterwards some turbine model specs can be uploaded to the application using the corresponding client methods.

Adding the specifications for the turbine model in a YAML file, for example `./inputs/my_turbine_model.yaml`.
```yaml
"name": "my_turbine_model_1",
"hub_height": 100 ,
"rotor_diameter": 120  ,
"rated_power": 5000000 ,
"reference_density": 1.225,
"reference_turbulence_intensity": 0.08,
"reference_windspeed": [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],
"thrust_coefficient": [2.5, 1.77, 1.41, 1.2, 1.1, 0.98, 0.94, 0.9, 0.85, 0.63, 0.47],
"power": [40500, 177700, 403900, 737600, 1187200, 1771100, 2518600, 3448400, 4562500, 5000000, 5000000],
"public": True
```

To send the turbine model specifications to Whiffle Wind, simply call `add_turbine_model` as shown. This only needs to be done once per turbine model, and thereafter, the turbine model will be readily available for any future simulations.
```python
turbine_model_object = client.add_turbine_model(data="./inputs/my_turbine_model.yaml")
```

Here data can be either a YAML with the proper attributes, a python dictionary with the values or a turbine model object (as it would be returned when calling `client.get_turbine_model(turbine_model_id=123)` for instance). All options are valid as long as they contain the information shown before.


> 💡: More information regarding turbine model specs can be found in [whiffle wind docs](https://docs.whiffle.cloud/).

### Define wind simulation

To set up a simulation, start by defining the simulation details in a YAML file. For example, you can create a file named configuration.yaml similar to the example below:

```yaml
type: WindSimulationTask

name: "MySimulation 1st week of Jan 2023"
reference_code: "Test simulations"

dates: 
  start: "2023-01-01"
  end: "2023-01-07"

simulation_type: "time_series"

windfarms:
  windfarm_a: !include ./windfarm_A.yaml
  windfarm_b:
    name: [turbine_1B, turbine_2B, turbine_3B, turbine_4B]
    location: [[4.25, 51.92], [4.21, 52.035], [4.31, 51.952], [4.22, 52.014]]  
    turbine_model_name: my_turbine_model_1  # Ideally <turbine_mode_id: the_proper_id>
    thrust: True
    include_in_les: True
  windfarm_c: !include-csv ./windfarm_C.csv

metmasts:
  name: [metA, metB, metC]
  location: [[4.05, 52], [4.1, 52.05], [4.15, 52.15]]  
metmasts_heights: [20, 40, 60, 80, 100, 2500, 3000] # unlimited

wind_resource_grid_heights: [100]
fields_heights: [120]
```

> 🔎: Note Whiffle's convention for locations/coordinates is [longitude, latitude].

The main configuration file can import additional resources such as YAML files (see 'windfarm_b' in example above) or CSV files (see 'windfarm_c' in example above). Below are examples illustrating how these imported YAML and CSV files can be defined.:

```yaml
name: [turbine_1A, turbine_2A, turbine_3A]
location: [[4.205, 52], [4.21, 52.015], [4.215, 52.011]]  
turbine_model_name: my_turbine_model_1
thrust: True
include_in_les: True
```

and

```csv
name,lon,lat,type
tur C1,4.2321,52.0321,my_turbine_model_1
turC2,4.23211,52.03211,my_turbine_model_1
turC3,4.232111,52.032111,my_turbine_model_1
```

To send a configuration to Whiffle Wind, utilize the following command:
```python
my_simulation = client.add_wind_simulation_task(data="./inputs/configuration.yaml")
```

This action won't initiate the simulation immediately; rather, it validates the configuration and saves it within Whiffle Wind.

Note how again, data can be a str to a file as in the example, a python Path object to a YAML or a WindSimulationTask object (the _my_simulation_ instance in the previous command)

An example of a dictionary containing the data would be:
```python
data = {
    "name": "MySimulation 1st week of Jan 2023",
    "reference_code": "Test simulations",
    "dates": {"start": "2023-01-01", "end": "2023-01-07"},
    "simulation_type": "time_series",
    "windfarms": {
        "windfarm_one": {
            "name": ["turbine_1A", "turbine_2A", "turbine_3A", "turbine_4A"],
            "location": [[4.25, 51.92], [4.21, 52.035], [4.31, 51.952], [4.22, 52.014]],
            "turbine_model_name": "nrel5mw",
            "thrust": True,
            "include_in_les": True,
        },
        "windfarm_two": {
            "name": ["turbine_1B", "turbine_2B", "turbine_3B", "turbine_4B"],
            "location": [
                [4.325, 52.592],
                [4.321, 52.535],
                [4.331, 52.5952],
                [4.322, 52.54],
            ],
            "turbine_model_name": "nrel5mw",
            "thrust": True,
            "include_in_les": False,
        },
    },
    "metmasts": {
        "name": ["metA", "metB", "metC"],
        "location": [[4.05, 52], [4.01, 52.05], [4.015, 52.015]],
    },
    "metmasts_heights": [20, 40, 60, 80, 100, 250, 500, 1000, 2000, 2500, 3000],
    "wind_resource_grid_heights": [80, 100, 120],
    "fields_heights": [120],
}
```

To check the defined simulation one can use the following command:
```python
print(client.get_wind_simulation_task(my_simulation.id))
```


> ℹ️: Among other attributes, the price of the drafted simulation is exposed.

> ℹ️: Also note how `simulation_type` is exposed. This selector allows to either run a _time\_series_ simulation or a _statistics_ one. More info found on whiffle wind documentation regarding [setting up](https://docs.whiffle.cloud/getting-started/running-a-simulation) a simulation and it's different [outputs](https://docs.whiffle.cloud/outputs).

### Starting the wind simulation task

Your simulation is now configured and ready to be launched. Starting it requires just one command.
```python
client.submit_wind_simulation_task(my_simulation.id)
```

> ⚠️: By submiting a wind simulation one accepts the terms and conditions of the service as well as being obliged to pay the price of such simulation.

Checking the progress can be done by getting the task from the client as in:

```python
print(client.get_wind_simulation_task(my_simulation.id))
```

### Downloading the results

Once the status of the wind simulation is completed, results can be dowloaded with the python client.

> 💡: Additionally, results can be explored on Whiffle's user interface https://whiffle.cloud where plots and visualizations of the data are provided as well as an easy to use interface to download the results too.

Using the python client the tabular data (csv's) and the wrg can be downloaded using:

```python
# Download csv + wrg data
client.download_wind_simulation_task(my_simulation.id)
```
This will download a zip with all the data that can be unpack with python with the following lines:
```python
import zipfile
with zipfile.ZipFile(f"{my_simulation.reference_number}.zip", 'r') as zip_ref:
    zip_ref.extractall(".")
```

The fields data can be dowloaded as follows:
```python
# Download fields data
client.download_wind_simulation_task(
    wind_simulation_task_id=my_simulation.id,
    file="fields",
)
```

### Additional examples


More information and examples on how to use the Whiffle Wind API python client in the public repo [whiffle-client-example](https://gitlab.com/whiffle-public/whiffle-client-example).

Please don't hesitate to contact <support@whiffle.nl> for any doubts regarding whiffle's python client.


## Run a task with Whiffle AspForge API client

You can create a new task using the aspforge client by executing,

`whiffle task run <path_to_the_task_specification.[json|yaml]>`

The client polls the progress of the task until it has finished. The task will run in the background if you abort the client.
You can list the most recent tasks by executing,

`whiffle task list`

For new users we recommend starting with the Whiffle Wind API.

If you need an access token or you have any questions, please reach out to <support@whiffle.nl>.



## Command-line interface for Whiffle AspForge API client

### List the configuration

`whiffle config list`

### Change the token in the configuration

`whiffle config edit user.token <your_token>`


### Run a task

`whiffle task run <path_to_the_task_specification.[json|yaml]>`


### List tasks

`whiffle task list <number of tasks>`

### Download a task

`whiffle task download <task_id>`

### Attach a task

You can monitor the progress of a task and it will be automatically downloaded once the task has been successfully completed. 

`whiffle task attach <task_id>`

### Cancel a task

A task on a non-finished status can be cancelled with the following command: 

`whiffle task cancel <task_id>`

## Task description file formats

Allowed file formats are JSON and YAML. The YAML format supports includes through [pyyaml-include](https://github.com/tanbro/pyyaml-include).

Here is an example of a YAML file with include:

The task.yaml file describes the task and includes the metmasts value from another file
``` 
metmasts: !include example_yaml_include_metmasts.yaml
```

and the example_yaml_include_metmasts.yaml file specifies the metmasts:
```
example_metmast_collection:
  id:
  - metmast0
  - metmast1
  lat:
  - 52.1
  - 52.2
  lon:
  - 3.1
  - 3.2
  z:
  - 10
  - 100
```
