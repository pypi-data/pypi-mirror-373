# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .creativework import CreativeWork


@register_model
class Claim(CreativeWork):
    """A Claim in Schema org represents a specific factually oriented claim that could be the itemReviewed in a ClaimReview The content of a claim can be summarized with the text property Variations on well known claims can have their common identity indicated via sameAs links and summarized with a name Ideally a Claim description includes enough contextual information to minimize the risk of ambiguity or inclarity In practice many claims are better understood in the context in which they appear or the interpretations provided by claim reviews Beyond ClaimReview the Claim type can be associated with related creative works for example a ScholarlyArticle or Question might be about some Claim At this time Schema org does not define any types of relationship between claims This is a natural area for future exploration"""

    appearance: Optional[
        Union["CreativeWork", str, List["CreativeWork"], List[str]]
    ] = Field(
        None, description="Indicates an occurrence of a Claim in some CreativeWork"
    )
    claimInterpreter: Optional[
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
        description="For a Claim interpreted from MediaObject content the interpretedAsClaim property can be used to indicate a claim contained implied or refined from the content of a MediaObject",
    )
    firstAppearance: Optional[
        Union["CreativeWork", str, List["CreativeWork"], List[str]]
    ] = Field(
        None,
        description="Indicates the first known occurrence of a Claim in some CreativeWork",
    )


# parent dependences
model_dependence("Claim", "CreativeWork")


# attribute dependences
model_dependence(
    "Claim",
    "CreativeWork",
    "Organization",
    "Person",
)
