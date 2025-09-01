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
class MedicalProcedure(MedicalEntity):
    """A process of care used in either a diagnostic therapeutic preventive or palliative capacity that relies on invasive surgical non invasive or other techniques"""

    bodyLocation: Optional[Union[str, List[str]]] = Field(
        None, description="Location in the body of the anatomical structure"
    )
    followup: Optional[Union[str, List[str]]] = Field(
        None,
        description="Typical or recommended followup care after the procedure is performed",
    )
    howPerformed: Optional[Union[str, List[str]]] = Field(
        None, description="How the procedure is performed"
    )
    preparation: Optional[
        Union["MedicalEntity", str, List["MedicalEntity"], List[str]]
    ] = Field(
        None,
        description="Typical preparation that a patient must undergo before having the procedure performed",
    )
    procedureType: Optional[
        Union["MedicalProcedureType", str, List["MedicalProcedureType"], List[str]]
    ] = Field(
        None,
        description="The type of procedure for example Surgical Noninvasive or Percutaneous",
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


# parent dependences
model_dependence("MedicalProcedure", "MedicalEntity")


# attribute dependences
model_dependence(
    "MedicalProcedure",
    "EventStatusType",
    "MedicalEntity",
    "MedicalProcedureType",
    "MedicalStudyStatus",
)
