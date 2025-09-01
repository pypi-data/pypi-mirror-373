# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import DateTime, Time


# base imports
from .intangible import Intangible


@register_model
class Trip(Intangible):
    """A trip or journey An itinerary of visits to one or more places"""

    arrivalTime: Optional[Union[str, List[str]]] = Field(
        None, description="The expected arrival time"
    )
    departureTime: Optional[Union[str, List[str]]] = Field(
        None, description="The expected departure time"
    )
    itinerary: Optional[
        Union["ItemList", "Place", str, List["ItemList"], List["Place"], List[str]]
    ] = Field(
        None,
        description="Destination s Place that make up a trip For a trip where destination order is important use ItemList to specify that order see examples",
    )
    offers: Optional[
        Union["Demand", "Offer", str, List["Demand"], List["Offer"], List[str]]
    ] = Field(
        None,
        description="An offer to provide this item for example an offer to sell a product rent the DVD of a movie perform a service or give away tickets to an event Use businessFunction to indicate the kind of transaction offered i e sell lease etc This property can also be used to describe a Demand While this property is listed as expected on a number of common types it can be used in others In that case using a second type such as Product or a subtype of Product can clarify the nature of the offer Inverse property itemOffered",
    )
    partOfTrip: Optional[Union["Trip", str, List["Trip"], List[str]]] = Field(
        None,
        description="Identifies that this Trip is a subTrip of another Trip For example Day 1 Day 2 etc of a multi day trip Inverse property subTrip",
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
    subTrip: Optional[Union["Trip", str, List["Trip"], List[str]]] = Field(
        None,
        description="Identifies a Trip that is a subTrip of this Trip For example Day 1 Day 2 etc of a multi day trip Inverse property partOfTrip",
    )
    tripOrigin: Optional[Union["Place", str, List["Place"], List[str]]] = Field(
        None,
        description="The location of origin of the trip prior to any destination s",
    )


# parent dependences
model_dependence("Trip", "Intangible")


# attribute dependences
model_dependence(
    "Trip",
    "Demand",
    "ItemList",
    "Offer",
    "Organization",
    "Person",
    "Place",
)
