# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .webpage import WebPage


@register_model
class FAQPage(WebPage):
    """A FAQPage is a WebPage presenting one or more Frequently asked questions see also QAPage"""


# parent dependences
model_dependence("FAQPage", "WebPage")


# attribute dependences
model_dependence(
    "FAQPage",
)
