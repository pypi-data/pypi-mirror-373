# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Text


# base imports
from .place import Place


@register_model
class CivicStructure(Place):
    """A public structure such as a town hall or concert hall"""

    openingHours: Optional[Union[str, List[str]]] = Field(
        None,
        description="The general opening hours for a business Opening hours can be specified as a weekly time range starting with days then times per day Multiple days can be listed with commas separating each day Day or time ranges are specified using a hyphen Days are specified using the following two letter combinations Mo Tu We Th Fr Sa Su Times are specified using 24 00 format For example 3pm is specified as 15 00 10am as 10 00 Here is an example time itemprop openingHours datetime Tu Th 16 00 20 00 Tuesdays and Thursdays 4 8pm time If a business is open 7 days a week then it can be specified as time itemprop openingHours datetime Mo Su Monday through Sunday all day time",
    )


# parent dependences
model_dependence("CivicStructure", "Place")


# attribute dependences
model_dependence(
    "CivicStructure",
)
