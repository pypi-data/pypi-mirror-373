# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .enumeration import Enumeration


@register_model
class MedicalEnumeration(Enumeration):
    """Enumerations related to health and the practice of medicine A concept that is used to attribute a quality to another concept as a qualifier a collection of items or a listing of all of the elements of a set in medicine practice"""


# parent dependences
model_dependence("MedicalEnumeration", "Enumeration")


# attribute dependences
model_dependence(
    "MedicalEnumeration",
)
