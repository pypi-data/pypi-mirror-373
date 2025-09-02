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
class MedicalStudy(MedicalEntity):
    """A medical study is an umbrella type covering all kinds of research studies relating to human medicine or health including observational studies and interventional trials and registries randomized controlled or not When the specific type of study is known use one of the extensions of this type such as MedicalTrial or MedicalObservationalStudy Also note that this type should be used to mark up data that describes the study itself to tag an article that publishes the results of a study use MedicalScholarlyArticle Note use the code property of MedicalEntity to store study IDs e g clinicaltrials gov ID"""

    healthCondition: Optional[
        Union["MedicalCondition", str, List["MedicalCondition"], List[str]]
    ] = Field(
        None,
        description="Specifying the health condition s of a patient medical study or other target audience",
    )
    sponsor: Optional[
        Union[
            "Organization",
            "Person",
            str,
            List["Organization"],
            List["Person"],
            List[str],
        ]
    ] = Field(
        None,
        description="A person or organization that supports a thing through a pledge promise or financial contribution E g a sponsor of a Medical Study or a corporate sponsor of an event",
    )
    status: Optional[
        Union[
            "EventStatusType",
            "MedicalStudyStatus",
            str,
            List["EventStatusType"],
            List["MedicalStudyStatus"],
            List[str],
        ]
    ] = Field(None, description="The status of the study enumerated")
    studyLocation: Optional[
        Union["AdministrativeArea", str, List["AdministrativeArea"], List[str]]
    ] = Field(None, description="The location in which the study is taking took place")
    studySubject: Optional[
        Union["MedicalEntity", str, List["MedicalEntity"], List[str]]
    ] = Field(
        None,
        description="A subject of the study i e one of the medical conditions therapies devices drugs etc investigated by the study",
    )


# parent dependences
model_dependence("MedicalStudy", "MedicalEntity")


# attribute dependences
model_dependence(
    "MedicalStudy",
    "AdministrativeArea",
    "EventStatusType",
    "MedicalCondition",
    "MedicalEntity",
    "MedicalStudyStatus",
    "Organization",
    "Person",
)
