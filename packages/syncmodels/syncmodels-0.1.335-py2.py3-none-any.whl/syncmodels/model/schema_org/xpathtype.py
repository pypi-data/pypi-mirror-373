# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .text import Text


@register_model
class XPathType(Text):
    """Text representing an XPath typically but not necessarily version 1 0"""


# parent dependences
model_dependence("XPathType", "Text")


# attribute dependences
model_dependence(
    "XPathType",
)
