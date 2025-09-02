# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Text, Boolean


# base imports
from .organization import Organization


@register_model
class MedicalOrganization(Organization):
    """A medical organization physical or not such as hospital institution or clinic"""

    healthPlanNetworkId: Optional[Union[str, List[str]]] = Field(
        None,
        description="Name or unique ID of network Networks are often reused across different insurance plans",
    )
    isAcceptingNewPatients: Optional[Union["bool", List["bool"]]] = Field(
        None, description="Whether the provider is accepting new patients"
    )
    medicalSpecialty: Optional[
        Union["MedicalSpecialty", str, List["MedicalSpecialty"], List[str]]
    ] = Field(None, description="A medical specialty of the provider")


# parent dependences
model_dependence("MedicalOrganization", "Organization")


# attribute dependences
model_dependence(
    "MedicalOrganization",
    "MedicalSpecialty",
)
