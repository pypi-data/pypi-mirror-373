# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .medicalbusiness import MedicalBusiness


@register_model
class Pharmacy(MedicalBusiness):
    """A pharmacy or drugstore"""


# parent dependences
model_dependence("Pharmacy", "MedicalBusiness")


# attribute dependences
model_dependence(
    "Pharmacy",
)
