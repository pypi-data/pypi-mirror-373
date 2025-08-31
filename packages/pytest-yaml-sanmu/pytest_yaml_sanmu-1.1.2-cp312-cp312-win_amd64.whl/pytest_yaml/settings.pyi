from _typeshed import Incomplete
from pathlib import Path
from typing import Any

enable_plugin: bool
mark_can_use_vars: bool
global_variable_paths: list[Path]
global_variable_paths_ignore_if_non_existent: bool
global_variable_python_class_name: str
logger: Incomplete

def load_global_variable_by_paths() -> dict[str, Any]: ...
