# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .enumeration import Enumeration


@register_model
class ReturnFeesEnumeration(Enumeration):
    """Enumerates several kinds of policies for product return fees"""


# parent dependences
model_dependence("ReturnFeesEnumeration", "Enumeration")


# attribute dependences
model_dependence(
    "ReturnFeesEnumeration",
)
