from .file import YamlItem as YamlItem
from _pytest.fixtures import FixtureRequest as FixtureRequest

def pytest_yaml_run_step(item: YamlItem, request: FixtureRequest): ...
