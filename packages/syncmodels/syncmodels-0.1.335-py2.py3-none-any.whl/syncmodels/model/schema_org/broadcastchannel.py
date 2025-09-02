# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Text, URL


# base imports
from .intangible import Intangible


@register_model
class BroadcastChannel(Intangible):
    """A unique instance of a BroadcastService on a CableOrSatelliteService lineup"""

    broadcastChannelId: Optional[Union[str, List[str]]] = Field(
        None,
        description="The unique address by which the BroadcastService can be identified in a provider lineup In US this is typically a number",
    )
    broadcastFrequency: Optional[
        Union[
            "BroadcastFrequencySpecification",
            str,
            List["BroadcastFrequencySpecification"],
            List[str],
        ]
    ] = Field(
        None,
        description="The frequency used for over the air broadcasts Numeric values or simple ranges e g 87 99 In addition a shortcut idiom is supported for frequencies of AM and FM radio channels e g 87 FM",
    )
    broadcastServiceTier: Optional[Union[str, List[str]]] = Field(
        None,
        description="The type of service required to have access to the channel e g Standard or Premium",
    )
    genre: Optional[Union[str, List[str]]] = Field(
        None, description="Genre of the creative work broadcast channel or group"
    )
    inBroadcastLineup: Optional[
        Union[
            "CableOrSatelliteService", str, List["CableOrSatelliteService"], List[str]
        ]
    ] = Field(None, description="The CableOrSatelliteService offering the channel")
    providesBroadcastService: Optional[
        Union["BroadcastService", str, List["BroadcastService"], List[str]]
    ] = Field(
        None,
        description="The BroadcastService offered on this channel Inverse property hasBroadcastChannel",
    )


# parent dependences
model_dependence("BroadcastChannel", "Intangible")


# attribute dependences
model_dependence(
    "BroadcastChannel",
    "BroadcastFrequencySpecification",
    "BroadcastService",
    "CableOrSatelliteService",
)
