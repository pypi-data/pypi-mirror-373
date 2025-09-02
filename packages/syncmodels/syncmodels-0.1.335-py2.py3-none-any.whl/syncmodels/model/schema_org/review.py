# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Text


# base imports
from .creativework import CreativeWork


@register_model
class Review(CreativeWork):
    """A review of an item for example of a restaurant movie or store"""

    associatedClaimReview: Optional[Union["Review", str, List["Review"], List[str]]] = (
        Field(
            None,
            description="An associated ClaimReview related by specific common content topic or claim The expectation is that this property would be most typically used in cases where a single activity is conducting both claim reviews and media reviews in which case relatedMediaReview would commonly be used on a ClaimReview while relatedClaimReview would be used on MediaReview",
        )
    )
    associatedMediaReview: Optional[Union["Review", str, List["Review"], List[str]]] = (
        Field(
            None,
            description="An associated MediaReview related by specific common content topic or claim The expectation is that this property would be most typically used in cases where a single activity is conducting both claim reviews and media reviews in which case relatedMediaReview would commonly be used on a ClaimReview while relatedClaimReview would be used on MediaReview",
        )
    )
    associatedReview: Optional[Union["Review", str, List["Review"], List[str]]] = Field(
        None, description="An associated Review"
    )
    itemReviewed: Optional[Union["Thing", str, List["Thing"], List[str]]] = Field(
        None, description="The item that is being reviewed rated"
    )
    negativeNotes: Optional[
        Union[
            "ItemList",
            "ListItem",
            "WebContent",
            str,
            List["ItemList"],
            List["ListItem"],
            List["WebContent"],
            List[str],
        ]
    ] = Field(
        None,
        description="Provides negative considerations regarding something most typically in pro con lists for reviews alongside positiveNotes For symmetry In the case of a Review the property describes the itemReviewed from the perspective of the review in the case of a Product the product itself is being described Since product descriptions tend to emphasise positive claims it may be relatively unusual to find negativeNotes used in this way Nevertheless for the sake of symmetry negativeNotes can be used on Product The property values can be expressed either as unstructured text repeated as necessary or if ordered as a list in which case the most negative is at the beginning of the list",
    )
    positiveNotes: Optional[
        Union[
            "ItemList",
            "ListItem",
            "WebContent",
            str,
            List["ItemList"],
            List["ListItem"],
            List["WebContent"],
            List[str],
        ]
    ] = Field(
        None,
        description="Provides positive considerations regarding something for example product highlights or alongside negativeNotes pro con lists for reviews In the case of a Review the property describes the itemReviewed from the perspective of the review in the case of a Product the product itself is being described The property values can be expressed either as unstructured text repeated as necessary or if ordered as a list in which case the most positive is at the beginning of the list",
    )
    reviewAspect: Optional[Union[str, List[str]]] = Field(
        None,
        description="This Review or Rating is relevant to this part or facet of the itemReviewed",
    )
    reviewBody: Optional[Union[str, List[str]]] = Field(
        None, description="The actual body of the review"
    )
    reviewRating: Optional[Union["Rating", str, List["Rating"], List[str]]] = Field(
        None,
        description="The rating given in this review Note that reviews can themselves be rated The reviewRating applies to rating given by the review The aggregateRating property applies to the review itself as a creative work",
    )


# parent dependences
model_dependence("Review", "CreativeWork")


# attribute dependences
model_dependence(
    "Review",
    "ItemList",
    "ListItem",
    "Rating",
    "Thing",
    "WebContent",
)
