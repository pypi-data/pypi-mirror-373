# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .datatype import DataType


@register_model
class Text(DataType):
    """Data type Text"""


# parent dependences
model_dependence("Text", "DataType")


# attribute dependences
model_dependence(
    "Text",
)
