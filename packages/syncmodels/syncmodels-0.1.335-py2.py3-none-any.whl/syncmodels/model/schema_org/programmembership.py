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
class ProgramMembership(Intangible):
    """Used to describe membership in a loyalty programs e g StarAliance traveler clubs e g AAA purchase clubs Safeway Club etc"""

    hostingOrganization: Optional[
        Union["Organization", str, List["Organization"], List[str]]
    ] = Field(
        None,
        description="The Organization airline travelers club retailer etc the membership is made with or which offers the MemberProgram",
    )
    member: Optional[
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
        description="A member of an Organization or a ProgramMembership Organizations can be members of organizations ProgramMembership is typically for individuals Supersedes members musicGroupMember Inverse property memberOf",
    )
    membershipNumber: Optional[Union[int, str, List[int], List[str]]] = Field(
        None, description="A unique identifier for the membership"
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
    program: Optional[Union["MemberProgram", str, List["MemberProgram"], List[str]]] = (
        Field(None, description="The MemberProgram associated with a ProgramMembership")
    )
    programName: Optional[Union[str, List[str]]] = Field(
        None,
        description="The program providing the membership It is preferable to use program instead",
    )


# parent dependences
model_dependence("ProgramMembership", "Intangible")


# attribute dependences
model_dependence(
    "ProgramMembership",
    "MemberProgram",
    "Organization",
    "Person",
    "QuantitativeValue",
)
