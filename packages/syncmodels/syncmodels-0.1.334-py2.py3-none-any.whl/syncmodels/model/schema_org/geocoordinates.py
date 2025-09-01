# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Text, Number


# base imports
from .structuredvalue import StructuredValue


@register_model
class GeoCoordinates(StructuredValue):
    """The geographic coordinates of a place or event"""

    address: Optional[Union["PostalAddress", str, List["PostalAddress"], List[str]]] = (
        Field(None, description="Physical address of the item")
    )
    addressCountry: Optional[Union["Country", str, List["Country"], List[str]]] = Field(
        None,
        description="The country Recommended to be in 2 letter ISO 3166 1 alpha 2 format for example US For backward compatibility a 3 letter ISO 3166 1 alpha 3 country code such as SGP or a full country name such as Singapore can also be used",
    )
    elevation: Optional[Union[float, str, List[float], List[str]]] = Field(
        None,
        description="The elevation of a location WGS 84 Values may be of the form NUMBER UNIT_OF_MEASUREMENT e g 1 000 m 3 200 ft while numbers alone should be assumed to be a value in meters",
    )
    latitude: Optional[Union[float, str, List[float], List[str]]] = Field(
        None, description="The latitude of a location For example 37 42242 WGS 84"
    )
    longitude: Optional[Union[float, str, List[float], List[str]]] = Field(
        None, description="The longitude of a location For example 122 08585 WGS 84"
    )
    postalCode: Optional[Union[str, List[str]]] = Field(
        None, description="The postal code For example 94043"
    )


# parent dependences
model_dependence("GeoCoordinates", "StructuredValue")


# attribute dependences
model_dependence(
    "GeoCoordinates",
    "Country",
    "PostalAddress",
)
