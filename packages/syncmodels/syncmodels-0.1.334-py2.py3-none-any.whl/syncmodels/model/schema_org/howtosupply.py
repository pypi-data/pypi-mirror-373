# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Text


# base imports
from .howtoitem import HowToItem


@register_model
class HowToSupply(HowToItem):
    """A supply consumed when performing the instructions for how to achieve a result"""

    estimatedCost: Optional[
        Union["MonetaryAmount", str, List["MonetaryAmount"], List[str]]
    ] = Field(
        None,
        description="The estimated cost of the supply or supplies consumed when performing instructions",
    )


# parent dependences
model_dependence("HowToSupply", "HowToItem")


# attribute dependences
model_dependence(
    "HowToSupply",
    "MonetaryAmount",
)
