# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .medicalsignorsymptom import MedicalSignOrSymptom


@register_model
class MedicalSign(MedicalSignOrSymptom):
    """Any physical manifestation of a person s medical condition discoverable by objective diagnostic tests or physical examination"""

    identifyingExam: Optional[
        Union["PhysicalExam", str, List["PhysicalExam"], List[str]]
    ] = Field(None, description="A physical examination that can identify this sign")
    identifyingTest: Optional[
        Union["MedicalTest", str, List["MedicalTest"], List[str]]
    ] = Field(None, description="A diagnostic test that can identify this sign")


# parent dependences
model_dependence("MedicalSign", "MedicalSignOrSymptom")


# attribute dependences
model_dependence(
    "MedicalSign",
    "MedicalTest",
    "PhysicalExam",
)
