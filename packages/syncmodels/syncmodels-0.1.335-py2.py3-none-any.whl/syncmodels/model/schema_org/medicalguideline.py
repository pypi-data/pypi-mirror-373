# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Text, Date


# base imports
from .medicalentity import MedicalEntity


@register_model
class MedicalGuideline(MedicalEntity):
    """Any recommendation made by a standard society e g ACC AHA or consensus statement that denotes how to diagnose and treat a particular condition Note this type should be used to tag the actual guideline recommendation if the guideline recommendation occurs in a larger scholarly article use MedicalScholarlyArticle to tag the overall article not this type Note also the organization making the recommendation should be captured in the recognizingAuthority base property of MedicalEntity"""

    evidenceLevel: Optional[
        Union["MedicalEvidenceLevel", str, List["MedicalEvidenceLevel"], List[str]]
    ] = Field(
        None,
        description="Strength of evidence of the data used to formulate the guideline enumerated",
    )
    evidenceOrigin: Optional[Union[str, List[str]]] = Field(
        None,
        description="Source of the data used to formulate the guidance e g RCT consensus opinion etc",
    )
    guidelineDate: Optional[Union[str, List[str]]] = Field(
        None, description="Date on which this guideline s recommendation was made"
    )
    guidelineSubject: Optional[
        Union["MedicalEntity", str, List["MedicalEntity"], List[str]]
    ] = Field(
        None,
        description="The medical conditions treatments etc that are the subject of the guideline",
    )


# parent dependences
model_dependence("MedicalGuideline", "MedicalEntity")


# attribute dependences
model_dependence(
    "MedicalGuideline",
    "MedicalEntity",
    "MedicalEvidenceLevel",
)
