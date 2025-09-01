# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Number, Text


# base imports
from .listitem import ListItem


@register_model
class HowToItem(ListItem):
    """An item used as either a tool or supply when performing the instructions for how to achieve a result"""

    requiredQuantity: Optional[
        Union[
            "QuantitativeValue",
            float,
            str,
            List["QuantitativeValue"],
            List[float],
            List[str],
        ]
    ] = Field(None, description="The required quantity of the item s")


# parent dependences
model_dependence("HowToItem", "ListItem")


# attribute dependences
model_dependence(
    "HowToItem",
    "QuantitativeValue",
)
