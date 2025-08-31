import pytest
import yaml
from . import settings as settings
from .fixtures import getfixtureinfo as getfixtureinfo
from .models import Case as Case
from .templates import item_locals as item_locals, render as render
from _pytest.config import Config as Config
from _pytest.fixtures import FuncFixtureInfo as FuncFixtureInfo
from _pytest.main import Session as Session
from _pytest.python import CallSpec2 as CallSpec2, FunctionDefinition, Metafunc
from _typeshed import Incomplete
from collections.abc import Generator
from typing import Any, Mapping
from yamlinclude import YamlIncludeConstructor

logger: Incomplete

class MySafeLoader(yaml.SafeLoader): ...
class MyYamlInclude(YamlIncludeConstructor): ...

class YamlFile(pytest.Module):
    obj: Incomplete
    def __init__(self, *args, **kwargs) -> None: ...
    def collect(self) -> Generator[Incomplete, Incomplete]: ...

class YamlItem(pytest.Function):
    yaml_data: Case
    max_step_no: int
    current_step_no: int
    current_step: dict
    usefixtures: dict
    callspec: Incomplete
    originalname: Incomplete
    fixturenames: Incomplete
    def __init__(self, name: str, parent, config: Config | None = None, callspec: CallSpec2 | None = None, callobj=..., keywords: Mapping[str, Any] | None = None, session: Session | None = None, fixtureinfo: FuncFixtureInfo | None = None, originalname: str | None = None, case: Case | None = None, own_markers: list | None = None, is_definition: bool = False) -> None: ...
    @property
    def cls(self): ...
    @property
    def is_first_step(self): ...
    @property
    def is_last_step(self): ...
    @property
    def location(self): ...
    @classmethod
    def from_parent(cls, parent, case: Case, **kw): ...
    def runtest(self) -> None: ...
    def repr_failure(self, excinfo): ...

class YamlItemDefinition(FunctionDefinition, YamlItem): ...
class YamlMetafunc(Metafunc): ...
