# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .quantity import Quantity


@register_model
class Distance(Quantity):
    """Properties that take Distances as values are of the form Number Length unit of measure E g 7 ft"""


# parent dependences
model_dependence("Distance", "Quantity")


# attribute dependences
model_dependence(
    "Distance",
)
