# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Text


# base imports
from .structuredvalue import StructuredValue


@register_model
class DefinedRegion(StructuredValue):
    """A DefinedRegion is a geographic area defined by potentially arbitrary rather than political administrative or natural geographical criteria Properties are provided for defining a region by reference to sets of postal codes Examples a delivery destination when shopping Region where regional pricing is configured Requirement 1 Country US States NY CA Requirement 2 Country US PostalCode Set 94000 94585 97000 97999 13000 13599 12345 12345 78945 78945 Region state canton prefecture autonomous community"""

    addressCountry: Optional[Union["Country", str, List["Country"], List[str]]] = Field(
        None,
        description="The country Recommended to be in 2 letter ISO 3166 1 alpha 2 format for example US For backward compatibility a 3 letter ISO 3166 1 alpha 3 country code such as SGP or a full country name such as Singapore can also be used",
    )
    addressRegion: Optional[Union[str, List[str]]] = Field(
        None,
        description="The region in which the locality is and which is in the country For example California or another appropriate first level Administrative division",
    )
    postalCode: Optional[Union[str, List[str]]] = Field(
        None, description="The postal code For example 94043"
    )
    postalCodePrefix: Optional[Union[str, List[str]]] = Field(
        None,
        description="A defined range of postal codes indicated by a common textual prefix Used for non numeric systems such as UK",
    )
    postalCodeRange: Optional[
        Union[
            "PostalCodeRangeSpecification",
            str,
            List["PostalCodeRangeSpecification"],
            List[str],
        ]
    ] = Field(None, description="A defined range of postal codes")


# parent dependences
model_dependence("DefinedRegion", "StructuredValue")


# attribute dependences
model_dependence(
    "DefinedRegion",
    "Country",
    "PostalCodeRangeSpecification",
)
