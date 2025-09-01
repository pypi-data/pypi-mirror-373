# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .enumeration import Enumeration


@register_model
class Specialty(Enumeration):
    """Any branch of a field in which people typically develop specific expertise usually after significant study time and effort"""


# parent dependences
model_dependence("Specialty", "Enumeration")


# attribute dependences
model_dependence(
    "Specialty",
)
