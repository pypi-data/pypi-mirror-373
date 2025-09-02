# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Number, Text, URL


# base imports
from .pricespecification import PriceSpecification


@register_model
class UnitPriceSpecification(PriceSpecification):
    """The price asked for a given offer by the respective organization or person"""

    billingDuration: Optional[
        Union[
            "Duration",
            "QuantitativeValue",
            float,
            str,
            List["Duration"],
            List["QuantitativeValue"],
            List[float],
            List[str],
        ]
    ] = Field(
        None,
        description="Specifies for how long this price or price component will be billed Can be used for example to model the contractual duration of a subscription or payment plan Type can be either a Duration or a Number in which case the unit of measurement for example month is specified by the unitCode property",
    )
    billingIncrement: Optional[Union[float, List[float]]] = Field(
        None,
        description="This property specifies the minimal quantity and rounding increment that will be the basis for the billing The unit of measurement is specified by the unitCode property",
    )
    billingStart: Optional[Union[float, List[float]]] = Field(
        None,
        description="Specifies after how much time this price or price component becomes valid and billing starts Can be used for example to model a price increase after the first year of a subscription The unit of measurement is specified by the unitCode property",
    )
    priceComponentType: Optional[
        Union[
            "PriceComponentTypeEnumeration",
            str,
            List["PriceComponentTypeEnumeration"],
            List[str],
        ]
    ] = Field(
        None,
        description="Identifies a price component for example a line item on an invoice part of the total price for an offer",
    )
    priceType: Optional[
        Union["PriceTypeEnumeration", str, List["PriceTypeEnumeration"], List[str]]
    ] = Field(
        None,
        description="Defines the type of a price specified for an offered product for example a list price a temporary sale price or a manufacturer suggested retail price If multiple prices are specified for an offer the priceType property can be used to identify the type of each such specified price The value of priceType can be specified as a value from enumeration PriceTypeEnumeration or as a free form text string for price types that are not already predefined in PriceTypeEnumeration",
    )
    referenceQuantity: Optional[
        Union["QuantitativeValue", str, List["QuantitativeValue"], List[str]]
    ] = Field(
        None,
        description="The reference quantity for which a certain price applies e g 1 EUR per 4 kWh of electricity This property is a replacement for unitOfMeasurement for the advanced cases where the price does not relate to a standard unit",
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
model_dependence("UnitPriceSpecification", "PriceSpecification")


# attribute dependences
model_dependence(
    "UnitPriceSpecification",
    "Duration",
    "PriceComponentTypeEnumeration",
    "PriceTypeEnumeration",
    "QuantitativeValue",
)
