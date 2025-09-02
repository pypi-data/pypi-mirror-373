# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import CssSelectorType, XPathType


# base imports
from .creativework import CreativeWork


@register_model
class WebPageElement(CreativeWork):
    """A web page element like a table or an image"""

    cssSelector: Optional[Union[str, List[str]]] = Field(
        None,
        description="A CSS selector e g of a SpeakableSpecification or WebPageElement In the latter case multiple matches within a page can constitute a single conceptual Web page element",
    )
    xpath: Optional[Union[str, List[str]]] = Field(
        None,
        description="An XPath e g of a SpeakableSpecification or WebPageElement In the latter case multiple matches within a page can constitute a single conceptual Web page element",
    )


# parent dependences
model_dependence("WebPageElement", "CreativeWork")


# attribute dependences
model_dependence(
    "WebPageElement",
)
