# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import DefinedTerm, Text, URL


# base imports
from .creativework import CreativeWork


@register_model
class EducationalOccupationalCredential(CreativeWork):
    """An educational or occupational credential A diploma academic degree certification qualification badge etc that may be awarded to a person or other entity that meets the requirements defined by the credentialer"""

    competencyRequired: Optional[Union[str, List[str]]] = Field(
        None,
        description="Knowledge skill ability or personal attribute that must be demonstrated by a person or other entity in order to do something such as earn an Educational Occupational Credential or understand a LearningResource",
    )
    credentialCategory: Optional[Union[str, List[str]]] = Field(
        None,
        description="The category or type of credential being described for example degreeâ â certificateâ â badgeâ or more specific term",
    )
    educationalLevel: Optional[Union[str, List[str]]] = Field(
        None,
        description="The level in terms of progression through an educational or training context Examples of educational levels include beginner intermediate or advanced and formal sets of level indicators",
    )
    recognizedBy: Optional[
        Union["Organization", str, List["Organization"], List[str]]
    ] = Field(
        None,
        description="An organization that acknowledges the validity value or utility of a credential Note recognition may include a process of quality assurance or accreditation",
    )
    validFor: Optional[Union["Duration", str, List["Duration"], List[str]]] = Field(
        None, description="The duration of validity of a permit or similar thing"
    )
    validIn: Optional[
        Union["AdministrativeArea", str, List["AdministrativeArea"], List[str]]
    ] = Field(
        None,
        description="The geographic area where the item is valid Applies for example to a Permit a Certification or an EducationalOccupationalCredential",
    )


# parent dependences
model_dependence("EducationalOccupationalCredential", "CreativeWork")


# attribute dependences
model_dependence(
    "EducationalOccupationalCredential",
    "AdministrativeArea",
    "Duration",
    "Organization",
)
