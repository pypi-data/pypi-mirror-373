# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .webpage import WebPage


@register_model
class ItemPage(WebPage):
    """A page devoted to a single item such as a particular product or hotel"""


# parent dependences
model_dependence("ItemPage", "WebPage")


# attribute dependences
model_dependence(
    "ItemPage",
)
