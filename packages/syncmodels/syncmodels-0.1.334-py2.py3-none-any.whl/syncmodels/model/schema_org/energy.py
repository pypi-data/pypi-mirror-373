# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .quantity import Quantity


@register_model
class Energy(Quantity):
    """Properties that take Energy as values are of the form Number Energy unit of measure"""


# parent dependences
model_dependence("Energy", "Quantity")


# attribute dependences
model_dependence(
    "Energy",
)
