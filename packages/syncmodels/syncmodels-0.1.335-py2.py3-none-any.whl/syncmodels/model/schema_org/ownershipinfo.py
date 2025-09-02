# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import DateTime


# base imports
from .structuredvalue import StructuredValue


@register_model
class OwnershipInfo(StructuredValue):
    """A structured value providing information about when a certain organization or person owned a certain product"""

    acquiredFrom: Optional[
        Union[
            "Organization",
            "Person",
            str,
            List["Organization"],
            List["Person"],
            List[str],
        ]
    ] = Field(
        None,
        description="The organization or person from which the product was acquired",
    )
    ownedFrom: Optional[Union[str, List[str]]] = Field(
        None, description="The date and time of obtaining the product"
    )
    ownedThrough: Optional[Union[str, List[str]]] = Field(
        None, description="The date and time of giving up ownership on the product"
    )
    typeOfGood: Optional[
        Union["Product", "Service", str, List["Product"], List["Service"], List[str]]
    ] = Field(
        None, description="The product that this structured value is referring to"
    )


# parent dependences
model_dependence("OwnershipInfo", "StructuredValue")


# attribute dependences
model_dependence(
    "OwnershipInfo",
    "Organization",
    "Person",
    "Product",
    "Service",
)
