# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .enumeration import Enumeration


@register_model
class TierBenefitEnumeration(Enumeration):
    """An enumeration of possible benefits as part of a loyalty members program"""


# parent dependences
model_dependence("TierBenefitEnumeration", "Enumeration")


# attribute dependences
model_dependence(
    "TierBenefitEnumeration",
)
