# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import PropertyValue, DefinedTerm, Text


# base imports
from .enumeration import Enumeration


@register_model
class QualitativeValue(Enumeration):
    """A predefined value for a product characteristic e g the power cord plug type US or the garment sizes S M L and XL"""

    additionalProperty: Optional[Union[str, List[str]]] = Field(
        None,
        description="A property value pair representing an additional characteristic of the entity e g a product feature or another characteristic for which there is no matching property in schema org Note Publishers should be aware that applications designed to use specific schema org properties e g https schema org width https schema org color https schema org gtin13 will typically expect such data to be provided using those properties rather than using the generic property value mechanism",
    )
    equal: Optional[
        Union["QualitativeValue", str, List["QualitativeValue"], List[str]]
    ] = Field(
        None,
        description="This ordering relation for qualitative values indicates that the subject is equal to the object",
    )
    greater: Optional[
        Union["QualitativeValue", str, List["QualitativeValue"], List[str]]
    ] = Field(
        None,
        description="This ordering relation for qualitative values indicates that the subject is greater than the object",
    )
    greaterOrEqual: Optional[
        Union["QualitativeValue", str, List["QualitativeValue"], List[str]]
    ] = Field(
        None,
        description="This ordering relation for qualitative values indicates that the subject is greater than or equal to the object",
    )
    lesser: Optional[
        Union["QualitativeValue", str, List["QualitativeValue"], List[str]]
    ] = Field(
        None,
        description="This ordering relation for qualitative values indicates that the subject is lesser than the object",
    )
    lesserOrEqual: Optional[
        Union["QualitativeValue", str, List["QualitativeValue"], List[str]]
    ] = Field(
        None,
        description="This ordering relation for qualitative values indicates that the subject is lesser than or equal to the object",
    )
    nonEqual: Optional[
        Union["QualitativeValue", str, List["QualitativeValue"], List[str]]
    ] = Field(
        None,
        description="This ordering relation for qualitative values indicates that the subject is not equal to the object",
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
model_dependence("QualitativeValue", "Enumeration")


# attribute dependences
model_dependence(
    "QualitativeValue",
    "Enumeration",
    "MeasurementTypeEnumeration",
    "QuantitativeValue",
    "StructuredValue",
)
