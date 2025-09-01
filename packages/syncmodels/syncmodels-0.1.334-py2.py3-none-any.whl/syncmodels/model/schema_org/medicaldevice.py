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
class MedicalDevice(MedicalEntity):
    """Any object used in a medical capacity such as to diagnose or treat a patient"""

    adverseOutcome: Optional[
        Union["MedicalEntity", str, List["MedicalEntity"], List[str]]
    ] = Field(
        None,
        description="A possible complication and or side effect of this therapy If it is known that an adverse outcome is serious resulting in death disability or permanent damage requiring hospitalization or otherwise life threatening or requiring immediate medical attention tag it as a seriousAdverseOutcome instead",
    )
    contraindication: Optional[
        Union[
            "MedicalContraindication", str, List["MedicalContraindication"], List[str]
        ]
    ] = Field(None, description="A contraindication for this therapy")
    postOp: Optional[Union[str, List[str]]] = Field(
        None,
        description="A description of the postoperative procedures care and or followups for this device",
    )
    preOp: Optional[Union[str, List[str]]] = Field(
        None,
        description="A description of the workup testing and other preparations required before implanting this device",
    )
    procedure: Optional[Union[str, List[str]]] = Field(
        None,
        description="A description of the procedure involved in setting up using and or installing the device",
    )
    seriousAdverseOutcome: Optional[
        Union["MedicalEntity", str, List["MedicalEntity"], List[str]]
    ] = Field(
        None,
        description="A possible serious complication and or serious side effect of this therapy Serious adverse outcomes include those that are life threatening result in death disability or permanent damage require hospitalization or prolong existing hospitalization cause congenital anomalies or birth defects or jeopardize the patient and may require medical or surgical intervention to prevent one of the outcomes in this definition",
    )


# parent dependences
model_dependence("MedicalDevice", "MedicalEntity")


# attribute dependences
model_dependence(
    "MedicalDevice",
    "MedicalContraindication",
    "MedicalEntity",
)
