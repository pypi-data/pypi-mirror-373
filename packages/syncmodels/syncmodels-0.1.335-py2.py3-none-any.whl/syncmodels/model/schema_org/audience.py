# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Text


# base imports
from .intangible import Intangible


@register_model
class Audience(Intangible):
    """Intended audience for an item i e the group for whom the item was created"""

    audienceType: Optional[Union[str, List[str]]] = Field(
        None,
        description="The target group associated with a given audience e g veterans car owners musicians etc",
    )
    geographicArea: Optional[
        Union["AdministrativeArea", str, List["AdministrativeArea"], List[str]]
    ] = Field(None, description="The geographic area associated with the audience")


# parent dependences
model_dependence("Audience", "Intangible")


# attribute dependences
model_dependence(
    "Audience",
    "AdministrativeArea",
)
