# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Text, Number, DefinedTerm


# base imports
from .intangible import Intangible


@register_model
class Occupation(Intangible):
    """A profession may involve prolonged training and or a formal qualification"""

    educationRequirements: Optional[
        Union[
            "EducationalOccupationalCredential",
            str,
            List["EducationalOccupationalCredential"],
            List[str],
        ]
    ] = Field(
        None, description="Educational background needed for the position or Occupation"
    )
    estimatedSalary: Optional[
        Union[
            "MonetaryAmount",
            "MonetaryAmountDistribution",
            float,
            str,
            List["MonetaryAmount"],
            List["MonetaryAmountDistribution"],
            List[float],
            List[str],
        ]
    ] = Field(
        None,
        description="An estimated salary for a job posting or occupation based on a variety of variables including but not limited to industry job title and location Estimated salaries are often computed by outside organizations rather than the hiring organization who may not have committed to the estimated value",
    )
    experienceRequirements: Optional[
        Union[
            "OccupationalExperienceRequirements",
            str,
            List["OccupationalExperienceRequirements"],
            List[str],
        ]
    ] = Field(
        None,
        description="Description of skills and experience needed for the position or Occupation",
    )
    occupationLocation: Optional[
        Union["AdministrativeArea", str, List["AdministrativeArea"], List[str]]
    ] = Field(
        None,
        description="The region country for which this occupational description is appropriate Note that educational requirements and qualifications can vary between jurisdictions",
    )
    occupationalCategory: Optional[
        Union["CategoryCode", str, List["CategoryCode"], List[str]]
    ] = Field(
        None,
        description="A category describing the job preferably using a term from a taxonomy such as BLS O NET SOC ISCO 08 or similar with the property repeated for each applicable value Ideally the taxonomy should be identified and both the textual label and formal code for the category should be provided Note for historical reasons any textual label and formal code provided as a literal may be assumed to be from O NET SOC",
    )
    qualifications: Optional[
        Union[
            "EducationalOccupationalCredential",
            str,
            List["EducationalOccupationalCredential"],
            List[str],
        ]
    ] = Field(
        None, description="Specific qualifications required for this role or Occupation"
    )
    responsibilities: Optional[Union[str, List[str]]] = Field(
        None, description="Responsibilities associated with this role or Occupation"
    )
    skills: Optional[Union[str, List[str]]] = Field(
        None,
        description="A statement of knowledge skill ability task or any other assertion expressing a competency that is either claimed by a person an organization or desired or required to fulfill a role or to work in an occupation",
    )


# parent dependences
model_dependence("Occupation", "Intangible")


# attribute dependences
model_dependence(
    "Occupation",
    "AdministrativeArea",
    "CategoryCode",
    "EducationalOccupationalCredential",
    "MonetaryAmount",
    "MonetaryAmountDistribution",
    "OccupationalExperienceRequirements",
)
