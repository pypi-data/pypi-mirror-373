# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .medicalcondition import MedicalCondition


@register_model
class MedicalSignOrSymptom(MedicalCondition):
    """Any feature associated or not with a medical condition In medicine a symptom is generally subjective while a sign is objective"""

    possibleTreatment: Optional[
        Union["MedicalTherapy", str, List["MedicalTherapy"], List[str]]
    ] = Field(
        None,
        description="A possible treatment to address this condition sign or symptom",
    )


# parent dependences
model_dependence("MedicalSignOrSymptom", "MedicalCondition")


# attribute dependences
model_dependence(
    "MedicalSignOrSymptom",
    "MedicalTherapy",
)
