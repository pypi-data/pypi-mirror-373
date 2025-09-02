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
class WebSite(CreativeWork):
    """A WebSite is a set of related web pages and other items typically served from a single web domain and accessible via URLs"""

    issn: Optional[Union[str, List[str]]] = Field(
        None,
        description="The International Standard Serial Number ISSN that identifies this serial publication You can repeat this property to identify different formats of or the linking ISSN ISSN L for this serial publication",
    )


# parent dependences
model_dependence("WebSite", "CreativeWork")


# attribute dependences
model_dependence(
    "WebSite",
)
