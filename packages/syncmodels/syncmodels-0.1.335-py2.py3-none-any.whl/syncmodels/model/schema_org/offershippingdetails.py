# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Boolean, Text, URL


# base imports
from .structuredvalue import StructuredValue


@register_model
class OfferShippingDetails(StructuredValue):
    """OfferShippingDetails represents information about shipping destinations Multiple of these entities can be used to represent different shipping rates for different destinations One entity for Alaska Hawaii A different one for continental US A different one for all France Multiple of these entities can be used to represent different shipping costs and delivery times Two entities that are identical but differ in rate and time E g Cheaper and slower 5 in 5 7 days or Fast and expensive 15 in 1 2 days"""

    deliveryTime: Optional[
        Union["ShippingDeliveryTime", str, List["ShippingDeliveryTime"], List[str]]
    ] = Field(
        None,
        description="The total delay between the receipt of the order and the goods reaching the final customer",
    )
    depth: Optional[
        Union[
            "Distance",
            "QuantitativeValue",
            int,
            str,
            List["Distance"],
            List["QuantitativeValue"],
            List[int],
            List[str],
        ]
    ] = Field(None, description="The depth of the item")
    doesNotShip: Optional[Union["bool", List["bool"]]] = Field(
        None,
        description="Indicates when shipping to a particular shippingDestination is not available",
    )
    height: Optional[
        Union[
            "Distance",
            "QuantitativeValue",
            int,
            str,
            List["Distance"],
            List["QuantitativeValue"],
            List[int],
            List[str],
        ]
    ] = Field(None, description="The height of the item")
    shippingDestination: Optional[
        Union["DefinedRegion", str, List["DefinedRegion"], List[str]]
    ] = Field(
        None,
        description="indicates possibly multiple shipping destinations These can be defined in several ways e g postalCode ranges",
    )
    shippingLabel: Optional[Union[str, List[str]]] = Field(
        None,
        description="Label to match an OfferShippingDetails with a ShippingRateSettings within the context of a shippingSettingsLink cross reference",
    )
    shippingOrigin: Optional[
        Union["DefinedRegion", str, List["DefinedRegion"], List[str]]
    ] = Field(
        None,
        description="Indicates the origin of a shipment i e where it should be coming from",
    )
    shippingRate: Optional[
        Union["MonetaryAmount", str, List["MonetaryAmount"], List[str]]
    ] = Field(
        None,
        description="The shipping rate is the cost of shipping to the specified destination Typically the maxValue and currency values of the MonetaryAmount are most appropriate",
    )
    shippingSettingsLink: Optional[Union[str, List[str]]] = Field(
        None,
        description="Link to a page containing ShippingRateSettings and DeliveryTimeSettings details",
    )
    transitTimeLabel: Optional[Union[str, List[str]]] = Field(
        None,
        description="Label to match an OfferShippingDetails with a DeliveryTimeSettings within the context of a shippingSettingsLink cross reference",
    )
    validForMemberTier: Optional[
        Union["MemberProgramTier", str, List["MemberProgramTier"], List[str]]
    ] = Field(
        None,
        description="The membership program tier an Offer or a PriceSpecification OfferShippingDetails or MerchantReturnPolicy under an Offer is valid for",
    )
    weight: Optional[
        Union["QuantitativeValue", str, List["QuantitativeValue"], List[str]]
    ] = Field(None, description="The weight of the product or person")
    width: Optional[
        Union[
            "Distance",
            "QuantitativeValue",
            int,
            str,
            List["Distance"],
            List["QuantitativeValue"],
            List[int],
            List[str],
        ]
    ] = Field(None, description="The width of the item")


# parent dependences
model_dependence("OfferShippingDetails", "StructuredValue")


# attribute dependences
model_dependence(
    "OfferShippingDetails",
    "DefinedRegion",
    "Distance",
    "MemberProgramTier",
    "MonetaryAmount",
    "QuantitativeValue",
    "ShippingDeliveryTime",
)
