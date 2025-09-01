# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .event import Event


@register_model
class PublicationEvent(Event):
    """A PublicationEvent corresponds indifferently to the event of publication for a CreativeWork of any type e g a broadcast event an on demand event a book journal publication via a variety of delivery media"""

    publishedBy: Optional[
        Union[
            "Organization",
            "Person",
            str,
            List["Organization"],
            List["Person"],
            List[str],
        ]
    ] = Field(None, description="An agent associated with the publication event")
    publishedOn: Optional[
        Union["BroadcastService", str, List["BroadcastService"], List[str]]
    ] = Field(
        None, description="A broadcast service associated with the publication event"
    )


# parent dependences
model_dependence("PublicationEvent", "Event")


# attribute dependences
model_dependence(
    "PublicationEvent",
    "BroadcastService",
    "Organization",
    "Person",
)
