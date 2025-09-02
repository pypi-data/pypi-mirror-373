# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Text, Number


# base imports
from .medicalintangible import MedicalIntangible


@register_model
class DrugStrength(MedicalIntangible):
    """A specific strength in which a medical drug is available in a specific country"""

    activeIngredient: Optional[Union[str, List[str]]] = Field(
        None,
        description="An active ingredient typically chemical compounds and or biologic substances",
    )
    availableIn: Optional[
        Union["AdministrativeArea", str, List["AdministrativeArea"], List[str]]
    ] = Field(None, description="The location in which the strength is available")
    maximumIntake: Optional[
        Union["MaximumDoseSchedule", str, List["MaximumDoseSchedule"], List[str]]
    ] = Field(
        None,
        description="Recommended intake of this supplement for a given population as defined by a specific recommending authority",
    )
    strengthUnit: Optional[Union[str, List[str]]] = Field(
        None, description="The units of an active ingredient s strength e g mg"
    )
    strengthValue: Optional[Union[float, List[float]]] = Field(
        None, description="The value of an active ingredient s strength e g 325"
    )


# parent dependences
model_dependence("DrugStrength", "MedicalIntangible")


# attribute dependences
model_dependence(
    "DrugStrength",
    "AdministrativeArea",
    "MaximumDoseSchedule",
)
