# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .specialty import Specialty


@register_model
class MedicalSpecialty(Specialty):
    """Any specific branch of medical science or practice Medical specialities include clinical specialties that pertain to particular organ systems and their respective disease states as well as allied health specialties Enumerated type"""


# parent dependences
model_dependence("MedicalSpecialty", "Specialty")


# attribute dependences
model_dependence(
    "MedicalSpecialty",
)
