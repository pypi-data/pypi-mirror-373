# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import URL, Text


# base imports
from .intangible import Intangible


@register_model
class Brand(Intangible):
    """A brand is a name used by an organization or business person for labeling a product product group or similar"""

    aggregateRating: Optional[
        Union["AggregateRating", str, List["AggregateRating"], List[str]]
    ] = Field(
        None,
        description="The overall rating based on a collection of reviews or ratings of the item",
    )
    logo: Optional[Union["ImageObject", str, List["ImageObject"], List[str]]] = Field(
        None, description="An associated logo"
    )
    review: Optional[Union["Review", str, List["Review"], List[str]]] = Field(
        None, description="A review of the item Supersedes reviews"
    )
    slogan: Optional[Union[str, List[str]]] = Field(
        None, description="A slogan or motto associated with the item"
    )


# parent dependences
model_dependence("Brand", "Intangible")


# attribute dependences
model_dependence(
    "Brand",
    "AggregateRating",
    "ImageObject",
    "Review",
)
