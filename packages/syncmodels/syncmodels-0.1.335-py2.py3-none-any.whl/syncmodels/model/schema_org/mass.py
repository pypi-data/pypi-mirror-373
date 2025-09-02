# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .quantity import Quantity


@register_model
class Mass(Quantity):
    """Properties that take Mass as values are of the form Number Mass unit of measure E g 7 kg"""


# parent dependences
model_dependence("Mass", "Quantity")


# attribute dependences
model_dependence(
    "Mass",
)
