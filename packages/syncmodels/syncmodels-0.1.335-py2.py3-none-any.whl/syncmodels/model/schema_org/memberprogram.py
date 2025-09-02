# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .intangible import Intangible


@register_model
class MemberProgram(Intangible):
    """A MemberProgram defines a loyalty or membership program that provides its members with certain benefits for example better pricing free shipping or returns or the ability to earn loyalty points Member programs may have multiple tiers for example silver and gold members each with different benefits"""

    hasTiers: Optional[
        Union["MemberProgramTier", str, List["MemberProgramTier"], List[str]]
    ] = Field(
        None, description="The tiers of a member program Inverse property isTierOf"
    )
    hostingOrganization: Optional[
        Union["Organization", str, List["Organization"], List[str]]
    ] = Field(
        None,
        description="The Organization airline travelers club retailer etc the membership is made with or which offers the MemberProgram",
    )


# parent dependences
model_dependence("MemberProgram", "Intangible")


# attribute dependences
model_dependence(
    "MemberProgram",
    "MemberProgramTier",
    "Organization",
)
