# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .medicalprocedure import MedicalProcedure


@register_model
class TherapeuticProcedure(MedicalProcedure):
    """A medical procedure intended primarily for therapeutic purposes aimed at improving a health condition"""

    adverseOutcome: Optional[
        Union["MedicalEntity", str, List["MedicalEntity"], List[str]]
    ] = Field(
        None,
        description="A possible complication and or side effect of this therapy If it is known that an adverse outcome is serious resulting in death disability or permanent damage requiring hospitalization or otherwise life threatening or requiring immediate medical attention tag it as a seriousAdverseOutcome instead",
    )
    doseSchedule: Optional[
        Union["DoseSchedule", str, List["DoseSchedule"], List[str]]
    ] = Field(
        None,
        description="A dosing schedule for the drug for a given population either observed recommended or maximum dose based on the type used",
    )
    drug: Optional[Union["Drug", str, List["Drug"], List[str]]] = Field(
        None, description="Specifying a drug or medicine used in a medication procedure"
    )


# parent dependences
model_dependence("TherapeuticProcedure", "MedicalProcedure")


# attribute dependences
model_dependence(
    "TherapeuticProcedure",
    "DoseSchedule",
    "Drug",
    "MedicalEntity",
)
