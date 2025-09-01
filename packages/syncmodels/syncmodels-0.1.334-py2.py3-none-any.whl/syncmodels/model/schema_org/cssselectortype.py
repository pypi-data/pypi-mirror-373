# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .text import Text


@register_model
class CssSelectorType(Text):
    """Text representing a CSS selector"""


# parent dependences
model_dependence("CssSelectorType", "Text")


# attribute dependences
model_dependence(
    "CssSelectorType",
)
