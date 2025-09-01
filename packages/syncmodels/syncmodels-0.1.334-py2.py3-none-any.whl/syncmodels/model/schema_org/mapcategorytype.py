# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .enumeration import Enumeration


@register_model
class MapCategoryType(Enumeration):
    """An enumeration of several kinds of Map"""


# parent dependences
model_dependence("MapCategoryType", "Enumeration")


# attribute dependences
model_dependence(
    "MapCategoryType",
)
