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
class Rating(Intangible):
    """A rating is an evaluation on a numeric scale such as 1 to 5 stars"""

    author: Optional[
        Union[
            "Organization",
            "Person",
            str,
            List["Organization"],
            List["Person"],
            List[str],
        ]
    ] = Field(
        None,
        description="The author of this content or rating Please note that author is special in that HTML 5 provides a special mechanism for indicating authorship via the rel tag That is equivalent to this and may be used interchangeably",
    )
    bestRating: Optional[Union[float, str, List[float], List[str]]] = Field(
        None, description="The highest value allowed in this rating system"
    )
    ratingExplanation: Optional[Union[str, List[str]]] = Field(
        None,
        description="A short explanation e g one to two sentences providing background context and other information that led to the conclusion expressed in the rating This is particularly applicable to ratings associated with fact check markup using ClaimReview",
    )
    ratingValue: Optional[Union[float, str, List[float], List[str]]] = Field(
        None,
        description="The rating for the content Usage guidelines Use values from 0123456789 Unicode DIGIT ZERO U 0030 to DIGIT NINE U 0039 rather than superficially similar Unicode symbols Use Unicode FULL STOP U 002E rather than to indicate a decimal point Avoid using these symbols as a readability separator",
    )
    reviewAspect: Optional[Union[str, List[str]]] = Field(
        None,
        description="This Review or Rating is relevant to this part or facet of the itemReviewed",
    )
    worstRating: Optional[Union[float, str, List[float], List[str]]] = Field(
        None, description="The lowest value allowed in this rating system"
    )


# parent dependences
model_dependence("Rating", "Intangible")


# attribute dependences
model_dependence(
    "Rating",
    "Organization",
    "Person",
)
