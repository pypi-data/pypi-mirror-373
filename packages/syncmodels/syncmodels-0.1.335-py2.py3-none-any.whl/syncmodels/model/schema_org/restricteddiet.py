# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .enumeration import Enumeration


@register_model
class RestrictedDiet(Enumeration):
    """A diet restricted to certain foods or preparations for cultural religious health or lifestyle reasons"""


# parent dependences
model_dependence("RestrictedDiet", "Enumeration")


# attribute dependences
model_dependence(
    "RestrictedDiet",
)
