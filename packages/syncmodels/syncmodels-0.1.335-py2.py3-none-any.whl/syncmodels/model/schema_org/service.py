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
class Service(Intangible):
    """A service provided by an organization e g delivery service print services etc"""

    aggregateRating: Optional[
        Union["AggregateRating", str, List["AggregateRating"], List[str]]
    ] = Field(
        None,
        description="The overall rating based on a collection of reviews or ratings of the item",
    )
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
    audience: Optional[Union["Audience", str, List["Audience"], List[str]]] = Field(
        None,
        description="An intended audience i e a group for whom something was created Supersedes serviceAudience",
    )
    availableChannel: Optional[
        Union["ServiceChannel", str, List["ServiceChannel"], List[str]]
    ] = Field(
        None,
        description="A means of accessing the service e g a phone bank a web site a location etc",
    )
    award: Optional[Union[str, List[str]]] = Field(
        None, description="An award won by or for this item Supersedes awards"
    )
    brand: Optional[
        Union[
            "Brand", "Organization", str, List["Brand"], List["Organization"], List[str]
        ]
    ] = Field(
        None,
        description="The brand s associated with a product or service or the brand s maintained by an organization or business person",
    )
    broker: Optional[
        Union[
            "Organization",
            "Person",
            str,
            List["Organization"],
            List["Person"],
            List[str],
        ]
    ] = Field(
        None,
        description="An entity that arranges for an exchange between a buyer and a seller In most cases a broker never acquires or releases ownership of a product or service involved in an exchange If it is not clear whether an entity is a broker seller or buyer the latter two terms are preferred Supersedes bookingAgent",
    )
    category: Optional[
        Union[
            "CategoryCode",
            "PhysicalActivityCategory",
            "Thing",
            str,
            List["CategoryCode"],
            List["PhysicalActivityCategory"],
            List["Thing"],
            List[str],
        ]
    ] = Field(
        None,
        description="A category for the item Greater signs or slashes can be used to informally indicate a category hierarchy",
    )
    hasCertification: Optional[
        Union["Certification", str, List["Certification"], List[str]]
    ] = Field(
        None,
        description="Certification information about a product organization service place or person",
    )
    hasOfferCatalog: Optional[
        Union["OfferCatalog", str, List["OfferCatalog"], List[str]]
    ] = Field(
        None,
        description="Indicates an OfferCatalog listing for this Organization Person or Service",
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
    isRelatedTo: Optional[
        Union["Product", "Service", str, List["Product"], List["Service"], List[str]]
    ] = Field(
        None,
        description="A pointer to another somehow related product or multiple products",
    )
    isSimilarTo: Optional[
        Union["Product", "Service", str, List["Product"], List["Service"], List[str]]
    ] = Field(
        None,
        description="A pointer to another functionally similar product or multiple products",
    )
    logo: Optional[Union["ImageObject", str, List["ImageObject"], List[str]]] = Field(
        None, description="An associated logo"
    )
    offers: Optional[
        Union["Demand", "Offer", str, List["Demand"], List["Offer"], List[str]]
    ] = Field(
        None,
        description="An offer to provide this item for example an offer to sell a product rent the DVD of a movie perform a service or give away tickets to an event Use businessFunction to indicate the kind of transaction offered i e sell lease etc This property can also be used to describe a Demand While this property is listed as expected on a number of common types it can be used in others In that case using a second type such as Product or a subtype of Product can clarify the nature of the offer Inverse property itemOffered",
    )
    provider: Optional[
        Union[
            "Organization",
            "Person",
            str,
            List["Organization"],
            List["Person"],
            List[str],
        ]
    ] = Field(
        None,
        description="The service provider service operator or service performer the goods producer Another party a seller may offer those services or goods on behalf of the provider A provider may also serve as the seller Supersedes carrier",
    )
    providerMobility: Optional[Union[str, List[str]]] = Field(
        None,
        description="Indicates the mobility of a provided service e g static dynamic",
    )
    review: Optional[Union["Review", str, List["Review"], List[str]]] = Field(
        None, description="A review of the item Supersedes reviews"
    )
    serviceOutput: Optional[Union["Thing", str, List["Thing"], List[str]]] = Field(
        None,
        description="The tangible thing generated by the service e g a passport permit etc Supersedes produces",
    )
    serviceType: Optional[
        Union["GovernmentBenefitsType", str, List["GovernmentBenefitsType"], List[str]]
    ] = Field(
        None,
        description="The type of service being offered e g veterans benefits emergency relief etc",
    )
    slogan: Optional[Union[str, List[str]]] = Field(
        None, description="A slogan or motto associated with the item"
    )
    termsOfService: Optional[Union[str, List[str]]] = Field(
        None, description="Human readable terms of service documentation"
    )


# parent dependences
model_dependence("Service", "Intangible")


# attribute dependences
model_dependence(
    "Service",
    "AdministrativeArea",
    "AggregateRating",
    "Audience",
    "Brand",
    "CategoryCode",
    "Certification",
    "Demand",
    "GeoShape",
    "GovernmentBenefitsType",
    "ImageObject",
    "Offer",
    "OfferCatalog",
    "OpeningHoursSpecification",
    "Organization",
    "Person",
    "PhysicalActivityCategory",
    "Place",
    "Product",
    "Review",
    "ServiceChannel",
    "Thing",
)
