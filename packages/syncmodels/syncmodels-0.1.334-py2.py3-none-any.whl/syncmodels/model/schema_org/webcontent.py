# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .creativework import CreativeWork


@register_model
class WebContent(CreativeWork):
    """WebContent is a type representing all WebPage WebSite and WebPageElement content It is sometimes the case that detailed distinctions between Web pages sites and their parts are not always important or obvious The WebContent type makes it easier to describe Web addressable content without requiring such distinctions to always be stated The intent is that the existing types WebPage WebSite and WebPageElement will eventually be declared as subtypes of WebContent"""


# parent dependences
model_dependence("WebContent", "CreativeWork")


# attribute dependences
model_dependence(
    "WebContent",
)
