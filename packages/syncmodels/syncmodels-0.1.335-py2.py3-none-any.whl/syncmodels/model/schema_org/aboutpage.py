# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .webpage import WebPage


@register_model
class AboutPage(WebPage):
    """Web page type About page"""


# parent dependences
model_dependence("AboutPage", "WebPage")


# attribute dependences
model_dependence(
    "AboutPage",
)
