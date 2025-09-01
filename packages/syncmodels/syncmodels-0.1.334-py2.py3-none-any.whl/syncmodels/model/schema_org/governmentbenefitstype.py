# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .enumeration import Enumeration


@register_model
class GovernmentBenefitsType(Enumeration):
    """GovernmentBenefitsType enumerates several kinds of government benefits to support the COVID 19 situation Note that this structure may not capture all benefits offered"""


# parent dependences
model_dependence("GovernmentBenefitsType", "Enumeration")


# attribute dependences
model_dependence(
    "GovernmentBenefitsType",
)
