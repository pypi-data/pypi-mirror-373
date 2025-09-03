from __future__ import annotations

import json
from inspect import isclass
from typing import Any

import pydantic
from packaging import version
from pydantic import BaseModel
from typing_extensions import TypeGuard

try:
    from pydantic.v1 import BaseModel as V1BaseModel
except ImportError:
    V1BaseModel = None

is_pydantic_v1 = version.parse(pydantic.__version__).major == 1


def _is_pydantic_v1_basemodel(type_: type) -> TypeGuard[type[BaseModel]]:
    return V1BaseModel is not None and issubclass(type_, V1BaseModel)


def _is_pydantic_v1_basemodel_instance(v: object) -> TypeGuard[BaseModel]:
    return V1BaseModel is not None and isinstance(v, V1BaseModel)


def is_pydantic_basemodel(type_: object) -> TypeGuard[type[BaseModel]]:
    """Check if a type is a Pydantic BaseModel."""
    return isclass(type_) and (issubclass(type_, BaseModel) or _is_pydantic_v1_basemodel(type_))


def is_pydantic_basemodel_instance(v: object) -> TypeGuard[BaseModel]:
    return isinstance(v, BaseModel) or _is_pydantic_v1_basemodel_instance(v)


def get_pydantic_output_structure(model: type[BaseModel]) -> str:
    if is_pydantic_v1 or _is_pydantic_v1_basemodel(model):
        return model.schema_json()
    else:
        return json.dumps(model.model_json_schema())  # pyright: ignore[reportAttributeAccessIssue]


def parse_pydantic_model(model: type[BaseModel], json_str: str) -> BaseModel:
    if is_pydantic_v1 or _is_pydantic_v1_basemodel(model):
        return model.parse_raw(json_str)
    else:
        return model.model_validate_json(json_str)  # pyright: ignore[reportAttributeAccessIssue]


def construct_pydantic_model(model: type[BaseModel], /, **kwargs: Any) -> BaseModel:
    if is_pydantic_v1 or _is_pydantic_v1_basemodel(model):
        return model.construct(**kwargs)
    else:
        return model.model_construct(**kwargs)  # pyright: ignore[reportAttributeAccessIssue]


def get_pydantic_model_dict(model: BaseModel) -> dict[str, Any]:
    if is_pydantic_v1 or _is_pydantic_v1_basemodel_instance(model):
        return model.dict()
    else:
        return model.model_dump()  # pyright: ignore[reportAttributeAccessIssue]


def get_pydantic_model_json(model: BaseModel) -> str:
    if is_pydantic_v1 or _is_pydantic_v1_basemodel_instance(model):
        return model.json()
    else:
        return model.model_dump_json()  # pyright: ignore[reportAttributeAccessIssue]
