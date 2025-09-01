# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Text


# base imports
from .creativework import CreativeWork


@register_model
class HowTo(CreativeWork):
    """Instructions that explain how to achieve a result by performing a sequence of steps"""

    estimatedCost: Optional[
        Union["MonetaryAmount", str, List["MonetaryAmount"], List[str]]
    ] = Field(
        None,
        description="The estimated cost of the supply or supplies consumed when performing instructions",
    )
    performTime: Optional[Union["Duration", str, List["Duration"], List[str]]] = Field(
        None,
        description="The length of time it takes to perform instructions or a direction not including time to prepare the supplies in ISO 8601 duration format",
    )
    prepTime: Optional[Union["Duration", str, List["Duration"], List[str]]] = Field(
        None,
        description="The length of time it takes to prepare the items to be used in instructions or a direction in ISO 8601 duration format",
    )
    step: Optional[
        Union[
            "CreativeWork",
            "HowToSection",
            "HowToStep",
            str,
            List["CreativeWork"],
            List["HowToSection"],
            List["HowToStep"],
            List[str],
        ]
    ] = Field(
        None,
        description="A single step item as HowToStep text document video etc or a HowToSection Supersedes steps",
    )
    supply: Optional[Union["HowToSupply", str, List["HowToSupply"], List[str]]] = Field(
        None,
        description="A sub property of instrument A supply consumed when performing instructions or a direction",
    )
    tool: Optional[Union["HowToTool", str, List["HowToTool"], List[str]]] = Field(
        None,
        description="A sub property of instrument An object used but not consumed when performing instructions or a direction",
    )
    totalTime: Optional[Union["Duration", str, List["Duration"], List[str]]] = Field(
        None,
        description="The total time required to perform instructions or a direction including time to prepare the supplies in ISO 8601 duration format",
    )
    yield_: Optional[
        Union["QuantitativeValue", str, List["QuantitativeValue"], List[str]]
    ] = Field(
        None,
        alias="yield",
        description="The quantity that results by performing instructions For example a paper airplane 10 personalized candles",
    )


# parent dependences
model_dependence("HowTo", "CreativeWork")


# attribute dependences
model_dependence(
    "HowTo",
    "CreativeWork",
    "Duration",
    "HowToSection",
    "HowToStep",
    "HowToSupply",
    "HowToTool",
    "MonetaryAmount",
    "QuantitativeValue",
)
