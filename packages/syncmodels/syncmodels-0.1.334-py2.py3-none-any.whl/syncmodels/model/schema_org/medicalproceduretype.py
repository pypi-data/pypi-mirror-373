# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .medicalenumeration import MedicalEnumeration


@register_model
class MedicalProcedureType(MedicalEnumeration):
    """An enumeration that describes different types of medical procedures"""


# parent dependences
model_dependence("MedicalProcedureType", "MedicalEnumeration")


# attribute dependences
model_dependence(
    "MedicalProcedureType",
)
