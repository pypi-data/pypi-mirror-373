# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import DateTime, Time, Text, Integer


# base imports
from .structuredvalue import StructuredValue


@register_model
class InteractionCounter(StructuredValue):
    """A summary of how users have interacted with this CreativeWork In most cases authors will use a subtype to specify the specific type of interaction"""

    endTime: Optional[str] = Field(
        None,
        description="The endTime of something For a reserved event or service e g FoodEstablishmentReservation the time that it is expected to end For actions that span a period of time when the action was performed E g John wrote a book from January to December For media including audio and video it s the time offset of the end of a clip within a larger file Note that Event uses startDate endDate instead of startTime endTime even when describing dates with times This situation may be clarified in future revisions",
    )
    interactionService: Optional[Union["SoftwareApplication", "WebSite"]] = Field(
        None,
        description="The WebSite or SoftwareApplication where the interactions took place",
    )
    interactionType: Optional["Action"] = Field(
        None,
        description="The Action representing the type of interaction For up votes 1s etc use LikeAction For down votes use DislikeAction Otherwise use the most specific Action",
    )
    location: Optional[Union["Place", "PostalAddress", "VirtualLocation", str]] = Field(
        None,
        description="The location of for example where an event is happening where an organization is located or where an action takes place",
    )
    startTime: Optional[str] = Field(
        None,
        description="The startTime of something For a reserved event or service e g FoodEstablishmentReservation the time that it is expected to start For actions that span a period of time when the action was performed E g John wrote a book from January to December For media including audio and video it s the time offset of the start of a clip within a larger file Note that Event uses startDate endDate instead of startTime endTime even when describing dates with times This situation may be clarified in future revisions",
    )
    userInteractionCount: Optional[int] = Field(
        None,
        description="The number of interactions for the CreativeWork using the WebSite or SoftwareApplication",
    )


# parent dependences
model_dependence("InteractionCounter", "StructuredValue")


# attribute dependences
model_dependence(
    "InteractionCounter",
    "Action",
    "Place",
    "PostalAddress",
    "SoftwareApplication",
    "VirtualLocation",
    "WebSite",
)
