# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .medicalintangible import MedicalIntangible


@register_model
class DrugLegalStatus(MedicalIntangible):
    """The legal availability status of a medical drug"""

    applicableLocation: Optional[
        Union["AdministrativeArea", str, List["AdministrativeArea"], List[str]]
    ] = Field(None, description="The location in which the status applies")


# parent dependences
model_dependence("DrugLegalStatus", "MedicalIntangible")


# attribute dependences
model_dependence(
    "DrugLegalStatus",
    "AdministrativeArea",
)
