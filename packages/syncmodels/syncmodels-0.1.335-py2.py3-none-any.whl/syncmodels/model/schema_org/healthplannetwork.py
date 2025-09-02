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
class HealthPlanNetwork(Intangible):
    """A US style health insurance plan network"""

    healthPlanCostSharing: Optional[Union["bool", List["bool"]]] = Field(
        None,
        description="The costs to the patient for services under this network or formulary",
    )
    healthPlanNetworkId: Optional[Union[str, List[str]]] = Field(
        None,
        description="Name or unique ID of network Networks are often reused across different insurance plans",
    )
    healthPlanNetworkTier: Optional[Union[str, List[str]]] = Field(
        None, description="The tier s for this network"
    )


# parent dependences
model_dependence("HealthPlanNetwork", "Intangible")


# attribute dependences
model_dependence(
    "HealthPlanNetwork",
)
