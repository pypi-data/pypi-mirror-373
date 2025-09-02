# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import (
    PropertyValue,
    Text,
    Boolean,
    Date,
    DateTime,
    Integer,
    URL,
    Number,
)


# base imports
from .intangible import Intangible


@register_model
class MerchantReturnPolicy(Intangible):
    """A MerchantReturnPolicy provides information about product return policies associated with an Organization Product or Offer"""

    additionalProperty: Optional[Union[str, List[str]]] = Field(
        None,
        description="A property value pair representing an additional characteristic of the entity e g a product feature or another characteristic for which there is no matching property in schema org Note Publishers should be aware that applications designed to use specific schema org properties e g https schema org width https schema org color https schema org gtin13 will typically expect such data to be provided using those properties rather than using the generic property value mechanism",
    )
    applicableCountry: Optional[Union["Country", str, List["Country"], List[str]]] = (
        Field(
            None,
            description="A country where a particular merchant return policy applies to for example the two letter ISO 3166 1 alpha 2 country code",
        )
    )
    customerRemorseReturnFees: Optional[
        Union["ReturnFeesEnumeration", str, List["ReturnFeesEnumeration"], List[str]]
    ] = Field(
        None,
        description="The type of return fees if the product is returned due to customer remorse",
    )
    customerRemorseReturnLabelSource: Optional[
        Union[
            "ReturnLabelSourceEnumeration",
            str,
            List["ReturnLabelSourceEnumeration"],
            List[str],
        ]
    ] = Field(
        None,
        description="The method from an enumeration by which the customer obtains a return shipping label for a product returned due to customer remorse",
    )
    customerRemorseReturnShippingFeesAmount: Optional[
        Union["MonetaryAmount", str, List["MonetaryAmount"], List[str]]
    ] = Field(
        None,
        description="The amount of shipping costs if a product is returned due to customer remorse Applicable when property customerRemorseReturnFees equals ReturnShippingFees",
    )
    inStoreReturnsOffered: Optional[Union["bool", List["bool"]]] = Field(
        None,
        description="Are in store returns offered For more advanced return methods use the returnMethod property",
    )
    itemCondition: Optional[
        Union["OfferItemCondition", str, List["OfferItemCondition"], List[str]]
    ] = Field(
        None,
        description="A predefined value from OfferItemCondition specifying the condition of the product or service or the products or services included in the offer Also used for product return policies to specify the condition of products accepted for returns",
    )
    itemDefectReturnFees: Optional[
        Union["ReturnFeesEnumeration", str, List["ReturnFeesEnumeration"], List[str]]
    ] = Field(
        None, description="The type of return fees for returns of defect products"
    )
    itemDefectReturnLabelSource: Optional[
        Union[
            "ReturnLabelSourceEnumeration",
            str,
            List["ReturnLabelSourceEnumeration"],
            List[str],
        ]
    ] = Field(
        None,
        description="The method from an enumeration by which the customer obtains a return shipping label for a defect product",
    )
    itemDefectReturnShippingFeesAmount: Optional[
        Union["MonetaryAmount", str, List["MonetaryAmount"], List[str]]
    ] = Field(
        None,
        description="Amount of shipping costs for defect product returns Applicable when property itemDefectReturnFees equals ReturnShippingFees",
    )
    merchantReturnDays: Optional[Union[int, str, List[int], List[str]]] = Field(
        None,
        description="Specifies either a fixed return date or the number of days from the delivery date that a product can be returned Used when the returnPolicyCategory property is specified as MerchantReturnFiniteReturnWindow Supersedes productReturnDays",
    )
    merchantReturnLink: Optional[Union[str, List[str]]] = Field(
        None,
        description="Specifies a Web page or service by URL for product returns Supersedes productReturnLink",
    )
    refundType: Optional[
        Union["RefundTypeEnumeration", str, List["RefundTypeEnumeration"], List[str]]
    ] = Field(None, description="A refund type from an enumerated list")
    restockingFee: Optional[
        Union[
            "MonetaryAmount", float, str, List["MonetaryAmount"], List[float], List[str]
        ]
    ] = Field(
        None,
        description="Use MonetaryAmount to specify a fixed restocking fee for product returns or use Number to specify a percentage of the product price paid by the customer",
    )
    returnFees: Optional[
        Union["ReturnFeesEnumeration", str, List["ReturnFeesEnumeration"], List[str]]
    ] = Field(
        None,
        description="The type of return fees for purchased products for any return reason",
    )
    returnLabelSource: Optional[
        Union[
            "ReturnLabelSourceEnumeration",
            str,
            List["ReturnLabelSourceEnumeration"],
            List[str],
        ]
    ] = Field(
        None,
        description="The method from an enumeration by which the customer obtains a return shipping label for a product returned for any reason",
    )
    returnMethod: Optional[
        Union[
            "ReturnMethodEnumeration", str, List["ReturnMethodEnumeration"], List[str]
        ]
    ] = Field(
        None,
        description="The type of return method offered specified from an enumeration",
    )
    returnPolicyCategory: Optional[
        Union[
            "MerchantReturnEnumeration",
            str,
            List["MerchantReturnEnumeration"],
            List[str],
        ]
    ] = Field(
        None, description="Specifies an applicable return policy from an enumeration"
    )
    returnPolicyCountry: Optional[Union["Country", str, List["Country"], List[str]]] = (
        Field(
            None,
            description="The country where the product has to be sent to for returns for example Ireland using the name property of Country You can also provide the two letter ISO 3166 1 alpha 2 country code Note that this can be different from the country where the product was originally shipped from or sent to",
        )
    )
    returnPolicySeasonalOverride: Optional[
        Union[
            "MerchantReturnPolicySeasonalOverride",
            str,
            List["MerchantReturnPolicySeasonalOverride"],
            List[str],
        ]
    ] = Field(None, description="Seasonal override of a return policy")
    returnShippingFeesAmount: Optional[
        Union["MonetaryAmount", str, List["MonetaryAmount"], List[str]]
    ] = Field(
        None,
        description="Amount of shipping costs for product returns for any reason Applicable when property returnFees equals ReturnShippingFees",
    )
    validForMemberTier: Optional[
        Union["MemberProgramTier", str, List["MemberProgramTier"], List[str]]
    ] = Field(
        None,
        description="The membership program tier an Offer or a PriceSpecification OfferShippingDetails or MerchantReturnPolicy under an Offer is valid for",
    )


# parent dependences
model_dependence("MerchantReturnPolicy", "Intangible")


# attribute dependences
model_dependence(
    "MerchantReturnPolicy",
    "Country",
    "MemberProgramTier",
    "MerchantReturnEnumeration",
    "MerchantReturnPolicySeasonalOverride",
    "MonetaryAmount",
    "OfferItemCondition",
    "RefundTypeEnumeration",
    "ReturnFeesEnumeration",
    "ReturnLabelSourceEnumeration",
    "ReturnMethodEnumeration",
)
