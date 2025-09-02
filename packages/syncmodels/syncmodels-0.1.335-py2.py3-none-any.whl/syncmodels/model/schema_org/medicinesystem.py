# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .medicalenumeration import MedicalEnumeration


@register_model
class MedicineSystem(MedicalEnumeration):
    """Systems of medical practice"""


# parent dependences
model_dependence("MedicineSystem", "MedicalEnumeration")


# attribute dependences
model_dependence(
    "MedicineSystem",
)
