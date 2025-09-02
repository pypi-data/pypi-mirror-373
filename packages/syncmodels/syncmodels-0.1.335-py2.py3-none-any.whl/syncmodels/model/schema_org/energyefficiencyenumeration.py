# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .enumeration import Enumeration


@register_model
class EnergyEfficiencyEnumeration(Enumeration):
    """Enumerates energy efficiency levels also known as classes or ratings and certifications that are part of several international energy efficiency standards"""


# parent dependences
model_dependence("EnergyEfficiencyEnumeration", "Enumeration")


# attribute dependences
model_dependence(
    "EnergyEfficiencyEnumeration",
)
