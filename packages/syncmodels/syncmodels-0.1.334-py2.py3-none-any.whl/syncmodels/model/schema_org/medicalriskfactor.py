# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .medicalentity import MedicalEntity


@register_model
class MedicalRiskFactor(MedicalEntity):
    """A risk factor is anything that increases a person s likelihood of developing or contracting a disease medical condition or complication"""

    increasesRiskOf: Optional[
        Union["MedicalEntity", str, List["MedicalEntity"], List[str]]
    ] = Field(
        None, description="The condition complication etc influenced by this factor"
    )


# parent dependences
model_dependence("MedicalRiskFactor", "MedicalEntity")


# attribute dependences
model_dependence(
    "MedicalRiskFactor",
    "MedicalEntity",
)
