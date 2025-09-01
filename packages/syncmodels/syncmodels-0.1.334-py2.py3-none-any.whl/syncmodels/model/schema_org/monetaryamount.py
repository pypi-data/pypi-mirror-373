# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Text, Number, Date, DateTime, Boolean


# base imports
from .structuredvalue import StructuredValue


@register_model
class MonetaryAmount(StructuredValue):
    """A monetary value or range This type can be used to describe an amount of money such as 50 USD or a range as in describing a bank account being suitable for a balance between Â 1 000 and Â 1 000 000 GBP or the value of a salary etc It is recommended to use PriceSpecification Types to describe the price of an Offer Invoice etc"""

    currency: Optional[Union[str, List[str]]] = Field(
        None,
        description="The currency in which the monetary amount is expressed Use standard formats ISO 4217 currency format e g USD Ticker symbol for cryptocurrencies e g BTC well known names for Local Exchange Trading Systems LETS and other currency types e g Ithaca HOUR",
    )
    maxValue: Optional[Union[float, List[float]]] = Field(
        None, description="The upper value of some characteristic or property"
    )
    minValue: Optional[Union[float, List[float]]] = Field(
        None, description="The lower value of some characteristic or property"
    )
    validFrom: Optional[Union[str, List[str]]] = Field(
        None, description="The date when the item becomes valid"
    )
    validThrough: Optional[Union[str, List[str]]] = Field(
        None,
        description="The date after when the item is not valid For example the end of an offer salary period or a period of opening hours",
    )
    value: Optional[
        Union[
            "StructuredValue",
            "bool",
            float,
            str,
            List["StructuredValue"],
            List["bool"],
            List[float],
            List[str],
        ]
    ] = Field(
        None,
        description="The value of a QuantitativeValue including Observation or property value node For QuantitativeValue and MonetaryAmount the recommended type for values is Number For PropertyValue it can be Text Number Boolean or StructuredValue Use values from 0123456789 Unicode DIGIT ZERO U 0030 to DIGIT NINE U 0039 rather than superficially similar Unicode symbols Use Unicode FULL STOP U 002E rather than to indicate a decimal point Avoid using these symbols as a readability separator",
    )


# parent dependences
model_dependence("MonetaryAmount", "StructuredValue")


# attribute dependences
model_dependence(
    "MonetaryAmount",
    "StructuredValue",
)
