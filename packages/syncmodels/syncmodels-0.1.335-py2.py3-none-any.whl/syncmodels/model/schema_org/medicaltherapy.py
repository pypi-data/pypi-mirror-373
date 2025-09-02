# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Text


# base imports
from .therapeuticprocedure import TherapeuticProcedure


@register_model
class MedicalTherapy(TherapeuticProcedure):
    """Any medical intervention designed to prevent treat and cure human diseases and medical conditions including both curative and palliative therapies Medical therapies are typically processes of care relying upon pharmacotherapy behavioral therapy supportive therapy with fluid or nutrition for example or detoxification e g hemodialysis aimed at improving or preventing a health condition"""

    contraindication: Optional[
        Union[
            "MedicalContraindication", str, List["MedicalContraindication"], List[str]
        ]
    ] = Field(None, description="A contraindication for this therapy")
    duplicateTherapy: Optional[
        Union["MedicalTherapy", str, List["MedicalTherapy"], List[str]]
    ] = Field(None, description="A therapy that duplicates or overlaps this one")
    seriousAdverseOutcome: Optional[
        Union["MedicalEntity", str, List["MedicalEntity"], List[str]]
    ] = Field(
        None,
        description="A possible serious complication and or serious side effect of this therapy Serious adverse outcomes include those that are life threatening result in death disability or permanent damage require hospitalization or prolong existing hospitalization cause congenital anomalies or birth defects or jeopardize the patient and may require medical or surgical intervention to prevent one of the outcomes in this definition",
    )


# parent dependences
model_dependence("MedicalTherapy", "TherapeuticProcedure")


# attribute dependences
model_dependence(
    "MedicalTherapy",
    "MedicalContraindication",
    "MedicalEntity",
)
