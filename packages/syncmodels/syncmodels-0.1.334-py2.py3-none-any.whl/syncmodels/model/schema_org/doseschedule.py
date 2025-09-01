# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Text, Number


# base imports
from .medicalintangible import MedicalIntangible


@register_model
class DoseSchedule(MedicalIntangible):
    """A specific dosing schedule for a drug or supplement"""

    doseUnit: Optional[Union[str, List[str]]] = Field(
        None, description="The unit of the dose e g mg"
    )
    doseValue: Optional[
        Union[
            "QualitativeValue",
            float,
            str,
            List["QualitativeValue"],
            List[float],
            List[str],
        ]
    ] = Field(None, description="The value of the dose e g 500")
    frequency: Optional[Union[str, List[str]]] = Field(
        None, description="How often the dose is taken e g daily"
    )
    targetPopulation: Optional[Union[str, List[str]]] = Field(
        None,
        description="Characteristics of the population for which this is intended or which typically uses it e g adults",
    )


# parent dependences
model_dependence("DoseSchedule", "MedicalIntangible")


# attribute dependences
model_dependence(
    "DoseSchedule",
    "QualitativeValue",
)
