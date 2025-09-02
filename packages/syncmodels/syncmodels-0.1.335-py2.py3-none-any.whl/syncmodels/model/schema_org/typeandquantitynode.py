# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Number, Text, URL


# base imports
from .structuredvalue import StructuredValue


@register_model
class TypeAndQuantityNode(StructuredValue):
    """A structured value indicating the quantity unit of measurement and business function of goods included in a bundle offer"""

    amountOfThisGood: Optional[Union[float, List[float]]] = Field(
        None, description="The quantity of the goods included in the offer"
    )
    businessFunction: Optional[
        Union["BusinessFunction", str, List["BusinessFunction"], List[str]]
    ] = Field(
        None,
        description="The business function e g sell lease repair dispose of the offer or component of a bundle TypeAndQuantityNode The default is http purl org goodrelations v1 Sell",
    )
    typeOfGood: Optional[
        Union["Product", "Service", str, List["Product"], List["Service"], List[str]]
    ] = Field(
        None, description="The product that this structured value is referring to"
    )
    unitCode: Optional[Union[str, List[str]]] = Field(
        None,
        description="The unit of measurement given using the UN CEFACT Common Code 3 characters or a URL Other codes than the UN CEFACT Common Code may be used with a prefix followed by a colon",
    )
    unitText: Optional[Union[str, List[str]]] = Field(
        None,
        description="A string or text indicating the unit of measurement Useful if you cannot provide a standard unit code for unitCode",
    )


# parent dependences
model_dependence("TypeAndQuantityNode", "StructuredValue")


# attribute dependences
model_dependence(
    "TypeAndQuantityNode",
    "BusinessFunction",
    "Product",
    "Service",
)
