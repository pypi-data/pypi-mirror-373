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
class Substance(MedicalEntity):
    """Any matter of defined composition that has discrete existence whose origin may be biological mineral or chemical"""

    activeIngredient: Optional[Union[str, List[str]]] = Field(
        None,
        description="An active ingredient typically chemical compounds and or biologic substances",
    )
    maximumIntake: Optional[
        Union["MaximumDoseSchedule", str, List["MaximumDoseSchedule"], List[str]]
    ] = Field(
        None,
        description="Recommended intake of this supplement for a given population as defined by a specific recommending authority",
    )


# parent dependences
model_dependence("Substance", "MedicalEntity")


# attribute dependences
model_dependence(
    "Substance",
    "MaximumDoseSchedule",
)
