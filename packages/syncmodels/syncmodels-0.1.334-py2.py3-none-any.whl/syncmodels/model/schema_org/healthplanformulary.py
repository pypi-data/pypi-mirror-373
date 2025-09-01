# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Boolean, Text


# base imports
from .intangible import Intangible


@register_model
class HealthPlanFormulary(Intangible):
    """For a given health insurance plan the specification for costs and coverage of prescription drugs"""

    healthPlanCostSharing: Optional[Union["bool", List["bool"]]] = Field(
        None,
        description="The costs to the patient for services under this network or formulary",
    )
    healthPlanDrugTier: Optional[Union[str, List[str]]] = Field(
        None,
        description="The tier s of drugs offered by this formulary or insurance plan",
    )
    offersPrescriptionByMail: Optional[Union["bool", List["bool"]]] = Field(
        None, description="Whether prescriptions can be delivered by mail"
    )


# parent dependences
model_dependence("HealthPlanFormulary", "Intangible")


# attribute dependences
model_dependence(
    "HealthPlanFormulary",
)
