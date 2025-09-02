# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Number, Text, Integer


# base imports
from .offer import Offer


@register_model
class AggregateOffer(Offer):
    """When a single product is associated with multiple offers for example the same pair of shoes is offered by different merchants then AggregateOffer can be used Note AggregateOffers are normally expected to associate multiple offers that all share the same defined businessFunction value or default to http purl org goodrelations v1 Sell if businessFunction is not explicitly defined"""

    highPrice: Optional[Union[float, str, List[float], List[str]]] = Field(
        None,
        description="The highest price of all offers available Usage guidelines Use values from 0123456789 Unicode DIGIT ZERO U 0030 to DIGIT NINE U 0039 rather than superficially similar Unicode symbols Use Unicode FULL STOP U 002E rather than to indicate a decimal point Avoid using these symbols as a readability separator",
    )
    lowPrice: Optional[Union[float, str, List[float], List[str]]] = Field(
        None,
        description="The lowest price of all offers available Usage guidelines Use values from 0123456789 Unicode DIGIT ZERO U 0030 to DIGIT NINE U 0039 rather than superficially similar Unicode symbols Use Unicode FULL STOP U 002E rather than to indicate a decimal point Avoid using these symbols as a readability separator",
    )
    offerCount: Optional[Union[int, List[int]]] = Field(
        None, description="The number of offers for the product"
    )
    offers: Optional[
        Union["Demand", "Offer", str, List["Demand"], List["Offer"], List[str]]
    ] = Field(
        None,
        description="An offer to provide this item for example an offer to sell a product rent the DVD of a movie perform a service or give away tickets to an event Use businessFunction to indicate the kind of transaction offered i e sell lease etc This property can also be used to describe a Demand While this property is listed as expected on a number of common types it can be used in others In that case using a second type such as Product or a subtype of Product can clarify the nature of the offer Inverse property itemOffered",
    )


# parent dependences
model_dependence("AggregateOffer", "Offer")


# attribute dependences
model_dependence(
    "AggregateOffer",
    "Demand",
    "Offer",
)
