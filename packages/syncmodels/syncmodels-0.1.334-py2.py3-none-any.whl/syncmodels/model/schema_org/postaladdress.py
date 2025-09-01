# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Text


# base imports
from .contactpoint import ContactPoint


@register_model
class PostalAddress(ContactPoint):
    """The mailing address"""

    addressCountry: Optional[Union["Country", str, List["Country"], List[str]]] = Field(
        None,
        description="The country Recommended to be in 2 letter ISO 3166 1 alpha 2 format for example US For backward compatibility a 3 letter ISO 3166 1 alpha 3 country code such as SGP or a full country name such as Singapore can also be used",
    )
    addressLocality: Optional[Union[str, List[str]]] = Field(
        None,
        description="The locality in which the street address is and which is in the region For example Mountain View",
    )
    addressRegion: Optional[Union[str, List[str]]] = Field(
        None,
        description="The region in which the locality is and which is in the country For example California or another appropriate first level Administrative division",
    )
    postOfficeBoxNumber: Optional[Union[int, str, List[int], List[str]]] = Field(
        None, description="The post office box number for PO box addresses"
    )
    postalCode: Optional[Union[str, List[str]]] = Field(
        None, description="The postal code For example 94043"
    )
    streetAddress: Optional[Union[str, List[str]]] = Field(
        None, description="The street address For example 1600 Amphitheatre Pkwy"
    )


# parent dependences
model_dependence("PostalAddress", "ContactPoint")


# attribute dependences
model_dependence(
    "PostalAddress",
    "Country",
)
