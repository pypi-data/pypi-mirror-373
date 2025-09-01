# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Integer


# base imports
from .creativework import CreativeWork


@register_model
class Comment(CreativeWork):
    """A comment on an item for example a comment on a blog post The comment s content is expressed via the text property and its topic via about properties shared with all CreativeWorks"""

    downvoteCount: Optional[Union[int, List[int]]] = Field(
        None,
        description="The number of downvotes this question answer or comment has received from the community",
    )
    parentItem: Optional[
        Union[
            "Comment",
            "CreativeWork",
            str,
            List["Comment"],
            List["CreativeWork"],
            List[str],
        ]
    ] = Field(
        None,
        description="The parent of a question answer or item in general Typically used for Q A discussion threads e g a chain of comments with the first comment being an Article or other CreativeWork See also comment which points from something to a comment about it",
    )
    sharedContent: Optional[
        Union["CreativeWork", str, List["CreativeWork"], List[str]]
    ] = Field(
        None,
        description="A CreativeWork such as an image video or audio clip shared as part of this posting",
    )
    upvoteCount: Optional[Union[int, List[int]]] = Field(
        None,
        description="The number of upvotes this question answer or comment has received from the community",
    )


# parent dependences
model_dependence("Comment", "CreativeWork")


# attribute dependences
model_dependence(
    "Comment",
    "CreativeWork",
)
