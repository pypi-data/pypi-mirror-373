from whiffle_client.io import load_yaml_with_include
from tests.conftest import task_with_yaml_include_path, wind_simulation_task


def test_load_yaml_with_include():
    result = load_yaml_with_include(task_with_yaml_include_path)
    assert isinstance(result["simulations"]["001"]["metmasts"], dict)


def test_load_yaml_with_include_relative_true():
    result = load_yaml_with_include(wind_simulation_task, relative_to_file=True)
    assert isinstance(result["windfarms"]["windfarm_b"], dict)
    assert isinstance(result["windfarms"]["windfarm_c"], dict)
