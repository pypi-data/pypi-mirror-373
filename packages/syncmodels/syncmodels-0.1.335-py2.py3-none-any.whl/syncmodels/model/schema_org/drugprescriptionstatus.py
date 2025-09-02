# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .medicalenumeration import MedicalEnumeration


@register_model
class DrugPrescriptionStatus(MedicalEnumeration):
    """Indicates whether this drug is available by prescription or over the counter"""


# parent dependences
model_dependence("DrugPrescriptionStatus", "MedicalEnumeration")


# attribute dependences
model_dependence(
    "DrugPrescriptionStatus",
)
