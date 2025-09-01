# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Number, Text


# base imports
from .intangible import Intangible


@register_model
class BroadcastFrequencySpecification(Intangible):
    """The frequency in MHz and the modulation used for a particular BroadcastService"""

    broadcastFrequencyValue: Optional[
        Union[
            "QuantitativeValue",
            float,
            str,
            List["QuantitativeValue"],
            List[float],
            List[str],
        ]
    ] = Field(None, description="The frequency in MHz for a particular broadcast")
    broadcastSignalModulation: Optional[
        Union["QualitativeValue", str, List["QualitativeValue"], List[str]]
    ] = Field(
        None,
        description="The modulation e g FM AM etc used by a particular broadcast service",
    )
    broadcastSubChannel: Optional[Union[str, List[str]]] = Field(
        None, description="The subchannel used for the broadcast"
    )


# parent dependences
model_dependence("BroadcastFrequencySpecification", "Intangible")


# attribute dependences
model_dependence(
    "BroadcastFrequencySpecification",
    "QualitativeValue",
    "QuantitativeValue",
)
