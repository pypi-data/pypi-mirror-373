# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Text


# base imports
from .article import Article


@register_model
class TechArticle(Article):
    """A technical article Example How to task topics step by step procedural troubleshooting specifications etc"""

    dependencies: Optional[Union[str, List[str]]] = Field(
        None, description="Prerequisites needed to fulfill steps in article"
    )
    proficiencyLevel: Optional[Union[str, List[str]]] = Field(
        None,
        description="Proficiency needed for this content expected values Beginner Expert",
    )


# parent dependences
model_dependence("TechArticle", "Article")


# attribute dependences
model_dependence(
    "TechArticle",
)
