# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Number


# base imports
from .structuredvalue import StructuredValue


@register_model
class QuantitativeValueDistribution(StructuredValue):
    """A statistical distribution of values"""

    duration: Optional[Union["Duration", str, List["Duration"], List[str]]] = Field(
        None,
        description="The duration of the item movie audio recording event etc in ISO 8601 duration format",
    )
    median: Optional[Union[float, List[float]]] = Field(
        None, description="The median value"
    )
    percentile10: Optional[Union[float, List[float]]] = Field(
        None, description="The 10th percentile value"
    )
    percentile25: Optional[Union[float, List[float]]] = Field(
        None, description="The 25th percentile value"
    )
    percentile75: Optional[Union[float, List[float]]] = Field(
        None, description="The 75th percentile value"
    )
    percentile90: Optional[Union[float, List[float]]] = Field(
        None, description="The 90th percentile value"
    )


# parent dependences
model_dependence("QuantitativeValueDistribution", "StructuredValue")


# attribute dependences
model_dependence(
    "QuantitativeValueDistribution",
    "Duration",
)
