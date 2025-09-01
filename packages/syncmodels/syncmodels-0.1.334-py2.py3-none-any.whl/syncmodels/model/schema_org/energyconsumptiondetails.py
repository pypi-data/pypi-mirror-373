# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .intangible import Intangible


@register_model
class EnergyConsumptionDetails(Intangible):
    """EnergyConsumptionDetails represents information related to the energy efficiency of a product that consumes energy The information that can be provided is based on international regulations such as for example EU directive 2017 1369 for energy labeling and the Energy labeling rule under the Energy Policy and Conservation Act EPCA in the US"""

    energyEfficiencyScaleMax: Optional[
        Union[
            "EUEnergyEfficiencyEnumeration",
            str,
            List["EUEnergyEfficiencyEnumeration"],
            List[str],
        ]
    ] = Field(
        None,
        description="Specifies the most energy efficient class on the regulated EU energy consumption scale for the product category a product belongs to For example energy consumption for televisions placed on the market after January 1 2020 is scaled from D to A",
    )
    energyEfficiencyScaleMin: Optional[
        Union[
            "EUEnergyEfficiencyEnumeration",
            str,
            List["EUEnergyEfficiencyEnumeration"],
            List[str],
        ]
    ] = Field(
        None,
        description="Specifies the least energy efficient class on the regulated EU energy consumption scale for the product category a product belongs to For example energy consumption for televisions placed on the market after January 1 2020 is scaled from D to A",
    )
    hasEnergyEfficiencyCategory: Optional[
        Union[
            "EnergyEfficiencyEnumeration",
            str,
            List["EnergyEfficiencyEnumeration"],
            List[str],
        ]
    ] = Field(
        None,
        description="Defines the energy efficiency Category which could be either a rating out of range of values or a yes no certification for a product according to an international energy efficiency standard",
    )


# parent dependences
model_dependence("EnergyConsumptionDetails", "Intangible")


# attribute dependences
model_dependence(
    "EnergyConsumptionDetails",
    "EUEnergyEfficiencyEnumeration",
    "EnergyEfficiencyEnumeration",
)
