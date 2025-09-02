# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .intangible import Intangible


@register_model
class MediaSubscription(Intangible):
    """A subscription which allows a user to access media including audio video books etc"""

    authenticator: Optional[
        Union["Organization", str, List["Organization"], List[str]]
    ] = Field(
        None,
        description="The Organization responsible for authenticating the user s subscription For example many media apps require a cable satellite provider to authenticate your subscription before playing media",
    )
    expectsAcceptanceOf: Optional[Union["Offer", str, List["Offer"], List[str]]] = (
        Field(
            None,
            description="An Offer which must be accepted before the user can perform the Action For example the user may need to buy a movie before being able to watch it",
        )
    )


# parent dependences
model_dependence("MediaSubscription", "Intangible")


# attribute dependences
model_dependence(
    "MediaSubscription",
    "Offer",
    "Organization",
)
