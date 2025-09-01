# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Text


# base imports
from .medicalentity import MedicalEntity


@register_model
class MedicalTest(MedicalEntity):
    """Any medical test typically performed for diagnostic purposes"""

    affectedBy: Optional[Union["Drug", str, List["Drug"], List[str]]] = Field(
        None, description="Drugs that affect the test s results"
    )
    normalRange: Optional[
        Union["MedicalEnumeration", str, List["MedicalEnumeration"], List[str]]
    ] = Field(
        None,
        description="Range of acceptable values for a typical patient when applicable",
    )
    signDetected: Optional[
        Union["MedicalSign", str, List["MedicalSign"], List[str]]
    ] = Field(None, description="A sign detected by the test")
    usedToDiagnose: Optional[
        Union["MedicalCondition", str, List["MedicalCondition"], List[str]]
    ] = Field(None, description="A condition the test is used to diagnose")
    usesDevice: Optional[
        Union["MedicalDevice", str, List["MedicalDevice"], List[str]]
    ] = Field(None, description="Device used to perform the test")


# parent dependences
model_dependence("MedicalTest", "MedicalEntity")


# attribute dependences
model_dependence(
    "MedicalTest",
    "Drug",
    "MedicalCondition",
    "MedicalDevice",
    "MedicalEnumeration",
    "MedicalSign",
)
