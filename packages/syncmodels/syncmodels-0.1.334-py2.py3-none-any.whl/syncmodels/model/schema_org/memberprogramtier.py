# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Text, Number


# base imports
from .intangible import Intangible


@register_model
class MemberProgramTier(Intangible):
    """A MemberProgramTier specifies a tier under a loyalty member program for example gold"""

    hasTierBenefit: Optional[
        Union["TierBenefitEnumeration", str, List["TierBenefitEnumeration"], List[str]]
    ] = Field(
        None, description="A member benefit for a particular tier of a loyalty program"
    )
    hasTierRequirement: Optional[
        Union[
            "CreditCard",
            "MonetaryAmount",
            "UnitPriceSpecification",
            str,
            List["CreditCard"],
            List["MonetaryAmount"],
            List["UnitPriceSpecification"],
            List[str],
        ]
    ] = Field(
        None,
        description="A requirement for a user to join a membership tier for example a CreditCard if the tier requires sign up for a credit card A UnitPriceSpecification if the user is required to pay a periodic fee or a MonetaryAmount if the user needs to spend a minimum amount to join the tier If a tier is free to join then this property does not need to be specified",
    )
    isTierOf: Optional[
        Union["MemberProgram", str, List["MemberProgram"], List[str]]
    ] = Field(
        None,
        description="The member program this tier is a part of Inverse property hasTiers",
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


# parent dependences
model_dependence("MemberProgramTier", "Intangible")


# attribute dependences
model_dependence(
    "MemberProgramTier",
    "CreditCard",
    "MemberProgram",
    "MonetaryAmount",
    "QuantitativeValue",
    "TierBenefitEnumeration",
    "UnitPriceSpecification",
)
