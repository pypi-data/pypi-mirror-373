# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import URL, Text


# base imports
from .intangible import Intangible


@register_model
class HealthInsurancePlan(Intangible):
    """A US style health insurance plan including PPOs EPOs and HMOs"""

    benefitsSummaryUrl: Optional[Union[str, List[str]]] = Field(
        None,
        description="The URL that goes directly to the summary of benefits and coverage for the specific standard plan or plan variation",
    )
    contactPoint: Optional[
        Union["ContactPoint", str, List["ContactPoint"], List[str]]
    ] = Field(
        None,
        description="A contact point for a person or organization Supersedes contactPoints",
    )
    healthPlanDrugOption: Optional[Union[str, List[str]]] = Field(
        None, description="TODO"
    )
    healthPlanDrugTier: Optional[Union[str, List[str]]] = Field(
        None,
        description="The tier s of drugs offered by this formulary or insurance plan",
    )
    healthPlanId: Optional[Union[str, List[str]]] = Field(
        None,
        description="The 14 character HIOS generated Plan ID number Plan IDs must be unique even across different markets",
    )
    healthPlanMarketingUrl: Optional[Union[str, List[str]]] = Field(
        None,
        description="The URL that goes directly to the plan brochure for the specific standard plan or plan variation",
    )
    includesHealthPlanFormulary: Optional[
        Union["HealthPlanFormulary", str, List["HealthPlanFormulary"], List[str]]
    ] = Field(None, description="Formularies covered by this plan")
    includesHealthPlanNetwork: Optional[
        Union["HealthPlanNetwork", str, List["HealthPlanNetwork"], List[str]]
    ] = Field(None, description="Networks covered by this plan")
    usesHealthPlanIdStandard: Optional[Union[str, List[str]]] = Field(
        None,
        description="The standard for interpreting the Plan ID The preferred is HIOS See the Centers for Medicare Medicaid Services for more details",
    )


# parent dependences
model_dependence("HealthInsurancePlan", "Intangible")


# attribute dependences
model_dependence(
    "HealthInsurancePlan",
    "ContactPoint",
    "HealthPlanFormulary",
    "HealthPlanNetwork",
)
