# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .energyefficiencyenumeration import EnergyEfficiencyEnumeration


@register_model
class EUEnergyEfficiencyEnumeration(EnergyEfficiencyEnumeration):
    """Enumerates the EU energy efficiency classes A G as well as A A and A as defined in EU directive 2017 1369"""


# parent dependences
model_dependence("EUEnergyEfficiencyEnumeration", "EnergyEfficiencyEnumeration")


# attribute dependences
model_dependence(
    "EUEnergyEfficiencyEnumeration",
)
