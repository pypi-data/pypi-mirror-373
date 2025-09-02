# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .medicalentity import MedicalEntity


@register_model
class DrugClass(MedicalEntity):
    """A class of medical drugs e g statins Classes can represent general pharmacological class common mechanisms of action common physiological effects etc"""

    drug: Optional[Union["Drug", str, List["Drug"], List[str]]] = Field(
        None, description="Specifying a drug or medicine used in a medication procedure"
    )


# parent dependences
model_dependence("DrugClass", "MedicalEntity")


# attribute dependences
model_dependence(
    "DrugClass",
    "Drug",
)
