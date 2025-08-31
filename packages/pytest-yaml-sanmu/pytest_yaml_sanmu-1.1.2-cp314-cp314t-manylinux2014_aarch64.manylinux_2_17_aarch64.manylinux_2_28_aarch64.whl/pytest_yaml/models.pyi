from pydantic import BaseModel

class Case(BaseModel):
    name: str
    vars: dict | None
    steps: list[dict]
    mark: list[str | dict]
    @classmethod
    def from_case_dict(cls, case_dict: dict): ...
    @classmethod
    def to_yaml(cls, obj) -> str: ...
    @classmethod
    def from_yaml(cls, yaml_str: str): ...
