# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .medicalprocedure import MedicalProcedure


@register_model
class PhysicalExam(MedicalProcedure):
    """A type of physical examination of a patient performed by a physician"""


# parent dependences
model_dependence("PhysicalExam", "MedicalProcedure")


# attribute dependences
model_dependence(
    "PhysicalExam",
)
