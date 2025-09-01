# from __future__ import annotations

from pydantic import BaseModel, Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


@register_model
class DataType(BaseModel):
    """The basic data types such as Integers Strings etc"""


# parent dependences


# attribute dependences
model_dependence(
    "DataType",
)
