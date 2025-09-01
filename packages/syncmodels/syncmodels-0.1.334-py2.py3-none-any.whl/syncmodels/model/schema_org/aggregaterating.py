# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Integer


# base imports
from .rating import Rating


@register_model
class AggregateRating(Rating):
    """The average rating based on multiple ratings or reviews"""

    itemReviewed: Optional[Union["Thing", str, List["Thing"], List[str]]] = Field(
        None, description="The item that is being reviewed rated"
    )
    ratingCount: Optional[Union[int, List[int]]] = Field(
        None, description="The count of total number of ratings"
    )
    reviewCount: Optional[Union[int, List[int]]] = Field(
        None, description="The count of total number of reviews"
    )


# parent dependences
model_dependence("AggregateRating", "Rating")


# attribute dependences
model_dependence(
    "AggregateRating",
    "Thing",
)
