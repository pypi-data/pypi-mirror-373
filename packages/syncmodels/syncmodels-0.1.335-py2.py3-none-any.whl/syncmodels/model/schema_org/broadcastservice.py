# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Text


# base imports
from .service import Service


@register_model
class BroadcastService(Service):
    """A delivery service through which content is provided via broadcast over the air or online"""

    broadcastAffiliateOf: Optional[
        Union["Organization", str, List["Organization"], List[str]]
    ] = Field(
        None,
        description="The media network s whose content is broadcast on this station",
    )
    broadcastDisplayName: Optional[Union[str, List[str]]] = Field(
        None,
        description="The name displayed in the channel guide For many US affiliates it is the network name",
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
    broadcastTimezone: Optional[Union[str, List[str]]] = Field(
        None,
        description="The timezone in ISO 8601 format for which the service bases its broadcasts",
    )
    broadcaster: Optional[
        Union["Organization", str, List["Organization"], List[str]]
    ] = Field(
        None, description="The organization owning or operating the broadcast service"
    )
    callSign: Optional[Union[str, List[str]]] = Field(
        None,
        description="A callsign as used in broadcasting and radio communications to identify people radio and TV stations or vehicles",
    )
    hasBroadcastChannel: Optional[
        Union["BroadcastChannel", str, List["BroadcastChannel"], List[str]]
    ] = Field(
        None,
        description="A broadcast channel of a broadcast service Inverse property providesBroadcastService",
    )
    inLanguage: Optional[Union["Language", str, List["Language"], List[str]]] = Field(
        None,
        description="The language of the content or performance or used in an action Please use one of the language codes from the IETF BCP 47 standard See also availableLanguage Supersedes language",
    )
    parentService: Optional[
        Union["BroadcastService", str, List["BroadcastService"], List[str]]
    ] = Field(
        None,
        description="A broadcast service to which the broadcast service may belong to such as regional variations of a national channel",
    )
    videoFormat: Optional[Union[str, List[str]]] = Field(
        None,
        description="The type of screening or video broadcast used e g IMAX 3D SD HD etc",
    )


# parent dependences
model_dependence("BroadcastService", "Service")


# attribute dependences
model_dependence(
    "BroadcastService",
    "BroadcastChannel",
    "BroadcastFrequencySpecification",
    "Language",
    "Organization",
)
