# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Text, URL


# base imports
from .intangible import Intangible


@register_model
class ServiceChannel(Intangible):
    """A means for accessing a service e g a government office location web site or phone number"""

    availableLanguage: Optional[Union["Language", str, List["Language"], List[str]]] = (
        Field(
            None,
            description="A language someone may use with or at the item service or place Please use one of the language codes from the IETF BCP 47 standard See also inLanguage",
        )
    )
    processingTime: Optional[Union["Duration", str, List["Duration"], List[str]]] = (
        Field(
            None,
            description="Estimated processing time for the service using this channel",
        )
    )
    providesService: Optional[Union["Service", str, List["Service"], List[str]]] = (
        Field(None, description="The service provided by this channel")
    )
    serviceLocation: Optional[Union["Place", str, List["Place"], List[str]]] = Field(
        None,
        description="The location e g civic structure local business etc where a person can go to access the service",
    )
    servicePhone: Optional[
        Union["ContactPoint", str, List["ContactPoint"], List[str]]
    ] = Field(None, description="The phone number to use to access the service")
    servicePostalAddress: Optional[
        Union["PostalAddress", str, List["PostalAddress"], List[str]]
    ] = Field(None, description="The address for accessing the service by mail")
    serviceSmsNumber: Optional[
        Union["ContactPoint", int, str, List["ContactPoint"], List[int], List[str]]
    ] = Field(None, description="The number to access the service by text message")
    serviceUrl: Optional[Union[str, List[str]]] = Field(
        None, description="The website to access the service"
    )


# parent dependences
model_dependence("ServiceChannel", "Intangible")


# attribute dependences
model_dependence(
    "ServiceChannel",
    "ContactPoint",
    "Duration",
    "Language",
    "Place",
    "PostalAddress",
    "Service",
)
