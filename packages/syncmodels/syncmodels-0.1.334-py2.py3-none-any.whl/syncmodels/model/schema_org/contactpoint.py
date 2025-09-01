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
class ContactPoint(StructuredValue):
    """A contact point for example a Customer Complaints department"""

    areaServed: Optional[
        Union[
            "AdministrativeArea",
            "GeoShape",
            "Place",
            str,
            List["AdministrativeArea"],
            List["GeoShape"],
            List["Place"],
            List[str],
        ]
    ] = Field(
        None,
        description="The geographic area where a service or offered item is provided Supersedes serviceArea",
    )
    availableLanguage: Optional[Union["Language", str, List["Language"], List[str]]] = (
        Field(
            None,
            description="A language someone may use with or at the item service or place Please use one of the language codes from the IETF BCP 47 standard See also inLanguage",
        )
    )
    contactOption: Optional[
        Union["ContactPointOption", str, List["ContactPointOption"], List[str]]
    ] = Field(
        None,
        description="An option available on this contact point e g a toll free number or support for hearing impaired callers",
    )
    contactType: Optional[Union[str, List[str]]] = Field(
        None,
        description="A person or organization can have different contact points for different purposes For example a sales contact point a PR contact point and so on This property is used to specify the kind of contact point",
    )
    email: Optional[Union[str, List[str]]] = Field(None, description="Email address")
    faxNumber: Optional[Union[int, str, List[int], List[str]]] = Field(
        None, description="The fax number"
    )
    hoursAvailable: Optional[
        Union[
            "OpeningHoursSpecification",
            str,
            List["OpeningHoursSpecification"],
            List[str],
        ]
    ] = Field(
        None, description="The hours during which this service or contact is available"
    )
    productSupported: Optional[Union["Product", str, List["Product"], List[str]]] = (
        Field(
            None,
            description="The product or service this support contact point is related to such as product support for a particular product line This can be a specific product or product line e g iPhone or a general category of products or services e g smartphones",
        )
    )
    telephone: Optional[Union[str, List[str]]] = Field(
        None, description="The telephone number"
    )


# parent dependences
model_dependence("ContactPoint", "StructuredValue")


# attribute dependences
model_dependence(
    "ContactPoint",
    "AdministrativeArea",
    "ContactPointOption",
    "GeoShape",
    "Language",
    "OpeningHoursSpecification",
    "Place",
    "Product",
)
