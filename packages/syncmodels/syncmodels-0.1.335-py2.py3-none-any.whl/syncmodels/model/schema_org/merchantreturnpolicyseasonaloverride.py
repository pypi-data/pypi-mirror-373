# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Date, DateTime, Integer, Number


# base imports
from .intangible import Intangible


@register_model
class MerchantReturnPolicySeasonalOverride(Intangible):
    """A seasonal override of a return policy for example used for holidays"""

    endDate: Optional[Union[str, List[str]]] = Field(
        None, description="The end date and time of the item in ISO 8601 date format"
    )
    merchantReturnDays: Optional[Union[int, str, List[int], List[str]]] = Field(
        None,
        description="Specifies either a fixed return date or the number of days from the delivery date that a product can be returned Used when the returnPolicyCategory property is specified as MerchantReturnFiniteReturnWindow Supersedes productReturnDays",
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
    returnShippingFeesAmount: Optional[
        Union["MonetaryAmount", str, List["MonetaryAmount"], List[str]]
    ] = Field(
        None,
        description="Amount of shipping costs for product returns for any reason Applicable when property returnFees equals ReturnShippingFees",
    )
    startDate: Optional[Union[str, List[str]]] = Field(
        None, description="The start date and time of the item in ISO 8601 date format"
    )


# parent dependences
model_dependence("MerchantReturnPolicySeasonalOverride", "Intangible")


# attribute dependences
model_dependence(
    "MerchantReturnPolicySeasonalOverride",
    "MerchantReturnEnumeration",
    "MonetaryAmount",
    "RefundTypeEnumeration",
    "ReturnFeesEnumeration",
    "ReturnMethodEnumeration",
)
