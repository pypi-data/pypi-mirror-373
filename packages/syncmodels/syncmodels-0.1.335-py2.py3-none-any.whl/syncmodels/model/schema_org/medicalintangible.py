# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .medicalentity import MedicalEntity


@register_model
class MedicalIntangible(MedicalEntity):
    """A utility class that serves as the umbrella for a number of intangible things in the medical space"""


# parent dependences
model_dependence("MedicalIntangible", "MedicalEntity")


# attribute dependences
model_dependence(
    "MedicalIntangible",
)
