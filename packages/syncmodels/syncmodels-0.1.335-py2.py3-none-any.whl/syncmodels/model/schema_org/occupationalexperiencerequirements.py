# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Number


# base imports
from .intangible import Intangible


@register_model
class OccupationalExperienceRequirements(Intangible):
    """Indicates employment related experience requirements e g monthsOfExperience"""

    monthsOfExperience: Optional[Union[float, List[float]]] = Field(
        None,
        description="Indicates the minimal number of months of experience required for a position",
    )


# parent dependences
model_dependence("OccupationalExperienceRequirements", "Intangible")


# attribute dependences
model_dependence(
    "OccupationalExperienceRequirements",
)
