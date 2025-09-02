# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .creativework import CreativeWork


@register_model
class Map(CreativeWork):
    """A map"""

    mapType: Optional[
        Union["MapCategoryType", str, List["MapCategoryType"], List[str]]
    ] = Field(
        None,
        description="Indicates the kind of Map from the MapCategoryType Enumeration",
    )


# parent dependences
model_dependence("Map", "CreativeWork")


# attribute dependences
model_dependence(
    "Map",
    "MapCategoryType",
)
