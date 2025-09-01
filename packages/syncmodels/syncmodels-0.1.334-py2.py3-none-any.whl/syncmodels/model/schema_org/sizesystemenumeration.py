# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .enumeration import Enumeration


@register_model
class SizeSystemEnumeration(Enumeration):
    """Enumerates common size systems for different categories of products for example EN 13402 or UK for wearables or Imperial for screws"""


# parent dependences
model_dependence("SizeSystemEnumeration", "Enumeration")


# attribute dependences
model_dependence(
    "SizeSystemEnumeration",
)
