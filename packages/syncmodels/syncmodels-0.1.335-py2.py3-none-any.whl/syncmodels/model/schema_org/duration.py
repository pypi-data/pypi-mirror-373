# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .quantity import Quantity


@register_model
class Duration(Quantity):
    """Quantity Duration use ISO 8601 duration format"""


# parent dependences
model_dependence("Duration", "Quantity")


# attribute dependences
model_dependence(
    "Duration",
)
