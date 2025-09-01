# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .enumeration import Enumeration


@register_model
class PriceComponentTypeEnumeration(Enumeration):
    """Enumerates different price components that together make up the total price for an offered product"""


# parent dependences
model_dependence("PriceComponentTypeEnumeration", "Enumeration")


# attribute dependences
model_dependence(
    "PriceComponentTypeEnumeration",
)
