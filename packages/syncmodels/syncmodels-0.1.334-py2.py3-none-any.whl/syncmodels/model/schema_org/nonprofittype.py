# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .enumeration import Enumeration


@register_model
class NonprofitType(Enumeration):
    """NonprofitType enumerates several kinds of official non profit types of which a non profit organization can be"""


# parent dependences
model_dependence("NonprofitType", "Enumeration")


# attribute dependences
model_dependence(
    "NonprofitType",
)
