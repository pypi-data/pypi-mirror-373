# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Number, Text, Date, DateTime, Boolean


# base imports
from .structuredvalue import StructuredValue


@register_model
class PriceSpecification(StructuredValue):
    """A structured value representing a price or price range Typically only the subclasses of this type are used for markup It is recommended to use MonetaryAmount to describe independent amounts of money such as a salary credit card limits etc"""

    eligibleQuantity: Optional[
        Union["QuantitativeValue", str, List["QuantitativeValue"], List[str]]
    ] = Field(
        None,
        description="The interval and unit of measurement of ordering quantities for which the offer or price specification is valid This allows e g specifying that a certain freight charge is valid only for a certain quantity",
    )
    eligibleTransactionVolume: Optional[
        Union["PriceSpecification", str, List["PriceSpecification"], List[str]]
    ] = Field(
        None,
        description="The transaction volume in a monetary unit for which the offer or price specification is valid e g for indicating a minimal purchasing volume to express free shipping above a certain order volume or to limit the acceptance of credit cards to purchases to a certain minimal amount",
    )
    maxPrice: Optional[Union[float, List[float]]] = Field(
        None, description="The highest price if the price is a range"
    )
    membershipPointsEarned: Optional[
        Union[
            "QuantitativeValue",
            float,
            str,
            List["QuantitativeValue"],
            List[float],
            List[str],
        ]
    ] = Field(
        None,
        description="The number of membership points earned by the member If necessary the unitText can be used to express the units the points are issued in E g stars miles etc",
    )
    minPrice: Optional[Union[float, List[float]]] = Field(
        None, description="The lowest price if the price is a range"
    )
    price: Optional[Union[float, List[float]]] = Field(
        None,
        description="The offer price of a product or of a price component when attached to PriceSpecification and its subtypes Usage guidelines Use the priceCurrency property with standard formats ISO 4217 currency format e g USD Ticker symbol for cryptocurrencies e g BTC well known names for Local Exchange Trading Systems LETS and other currency types e g Ithaca HOUR instead of including ambiguous symbols such as in the value Use Unicode FULL STOP U 002E rather than to indicate a decimal point Avoid using these symbols as a readability separator Note that both RDFa and Microdata syntax allow the use of a content attribute for publishing simple machine readable values alongside more human friendly formatting Use values from 0123456789 Unicode DIGIT ZERO U 0030 to DIGIT NINE U 0039 rather than superficially similar Unicode symbols",
    )
    priceCurrency: Optional[Union[str, List[str]]] = Field(
        None,
        description="The currency of the price or a price component when attached to PriceSpecification and its subtypes Use standard formats ISO 4217 currency format e g USD Ticker symbol for cryptocurrencies e g BTC well known names for Local Exchange Trading Systems LETS and other currency types e g Ithaca HOUR",
    )
    validForMemberTier: Optional[
        Union["MemberProgramTier", str, List["MemberProgramTier"], List[str]]
    ] = Field(
        None,
        description="The membership program tier an Offer or a PriceSpecification OfferShippingDetails or MerchantReturnPolicy under an Offer is valid for",
    )
    validFrom: Optional[Union[str, List[str]]] = Field(
        None, description="The date when the item becomes valid"
    )
    validThrough: Optional[Union[str, List[str]]] = Field(
        None,
        description="The date after when the item is not valid For example the end of an offer salary period or a period of opening hours",
    )
    valueAddedTaxIncluded: Optional[Union["bool", List["bool"]]] = Field(
        None,
        description="Specifies whether the applicable value added tax VAT is included in the price specification or not",
    )


# parent dependences
model_dependence("PriceSpecification", "StructuredValue")


# attribute dependences
model_dependence(
    "PriceSpecification",
    "MemberProgramTier",
    "QuantitativeValue",
)
