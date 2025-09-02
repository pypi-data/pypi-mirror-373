# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import PropertyValue, Number, Text, URL, Boolean, DefinedTerm


# base imports
from .structuredvalue import StructuredValue


@register_model
class QuantitativeValue(StructuredValue):
    """A point value or interval for product characteristics and other purposes"""

    additionalProperty: Optional[Union[str, List[str]]] = Field(
        None,
        description="A property value pair representing an additional characteristic of the entity e g a product feature or another characteristic for which there is no matching property in schema org Note Publishers should be aware that applications designed to use specific schema org properties e g https schema org width https schema org color https schema org gtin13 will typically expect such data to be provided using those properties rather than using the generic property value mechanism",
    )
    maxValue: Optional[Union[float, List[float]]] = Field(
        None, description="The upper value of some characteristic or property"
    )
    minValue: Optional[Union[float, List[float]]] = Field(
        None, description="The lower value of some characteristic or property"
    )
    unitCode: Optional[Union[str, List[str]]] = Field(
        None,
        description="The unit of measurement given using the UN CEFACT Common Code 3 characters or a URL Other codes than the UN CEFACT Common Code may be used with a prefix followed by a colon",
    )
    unitText: Optional[Union[str, List[str]]] = Field(
        None,
        description="A string or text indicating the unit of measurement Useful if you cannot provide a standard unit code for unitCode",
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
    valueReference: Optional[
        Union[
            "Enumeration",
            "MeasurementTypeEnumeration",
            "QualitativeValue",
            "QuantitativeValue",
            "StructuredValue",
            str,
            List["Enumeration"],
            List["MeasurementTypeEnumeration"],
            List["QualitativeValue"],
            List["QuantitativeValue"],
            List["StructuredValue"],
            List[str],
        ]
    ] = Field(
        None,
        description="A secondary value that provides additional information on the original value e g a reference temperature or a type of measurement",
    )


# parent dependences
model_dependence("QuantitativeValue", "StructuredValue")


# attribute dependences
model_dependence(
    "QuantitativeValue",
    "Enumeration",
    "MeasurementTypeEnumeration",
    "QualitativeValue",
    "StructuredValue",
)
