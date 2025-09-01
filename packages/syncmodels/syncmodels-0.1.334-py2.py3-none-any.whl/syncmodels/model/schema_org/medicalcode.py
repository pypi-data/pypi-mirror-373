# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Text


# base imports
from .medicalintangible import MedicalIntangible


@register_model
class MedicalCode(MedicalIntangible):
    """A code for a medical entity"""

    codeValue: Optional[Union[str, List[str]]] = Field(
        None, description="A short textual code that uniquely identifies the value"
    )
    codingSystem: Optional[Union[str, List[str]]] = Field(
        None, description="The coding system e g ICD 10"
    )


# parent dependences
model_dependence("MedicalCode", "MedicalIntangible")


# attribute dependences
model_dependence(
    "MedicalCode",
)
