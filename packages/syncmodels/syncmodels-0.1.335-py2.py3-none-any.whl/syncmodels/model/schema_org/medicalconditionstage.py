# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Number, Text


# base imports
from .medicalintangible import MedicalIntangible


@register_model
class MedicalConditionStage(MedicalIntangible):
    """A stage of a medical condition such as Stage IIIa"""

    stageAsNumber: Optional[Union[float, int, List[float], List[int]]] = Field(
        None, description="The stage represented as a number e g 3"
    )
    subStageSuffix: Optional[Union[str, List[str]]] = Field(
        None, description="The substage e g a for Stage IIIa"
    )


# parent dependences
model_dependence("MedicalConditionStage", "MedicalIntangible")


# attribute dependences
model_dependence(
    "MedicalConditionStage",
)
