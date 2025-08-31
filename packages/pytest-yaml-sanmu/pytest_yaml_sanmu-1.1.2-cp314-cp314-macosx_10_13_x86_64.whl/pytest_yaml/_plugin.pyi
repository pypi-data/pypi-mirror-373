import pytest
from .file import YamlItem as YamlItem
from _typeshed import Incomplete
from abc import ABCMeta, abstractmethod
from pytest import FixtureRequest as FixtureRequest

class YamlPlugin(metaclass=ABCMeta):
    config: Incomplete
    def __init__(self, config: pytest.Config) -> None: ...
    @abstractmethod
    def pytest_yaml_run_step(self, item: YamlItem, request: FixtureRequest): ...

class PrintYamlPlugin(YamlPlugin):
    def is_chinese_locale(self): ...
    def pytest_yaml_run_step(self, item: YamlItem, request: FixtureRequest): ...

class AllureYamlPlugin(YamlPlugin):
    meta_column_name: str
    def __init__(self, *args, **kwargs) -> None: ...
    def pytest_yaml_run_step(self, item: YamlItem, request: FixtureRequest): ...
