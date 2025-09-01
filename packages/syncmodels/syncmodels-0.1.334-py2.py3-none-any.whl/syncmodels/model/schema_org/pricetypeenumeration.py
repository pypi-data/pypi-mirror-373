# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .enumeration import Enumeration


@register_model
class PriceTypeEnumeration(Enumeration):
    """Enumerates different price types for example list price invoice price and sale price"""


# parent dependences
model_dependence("PriceTypeEnumeration", "Enumeration")


# attribute dependences
model_dependence(
    "PriceTypeEnumeration",
)
