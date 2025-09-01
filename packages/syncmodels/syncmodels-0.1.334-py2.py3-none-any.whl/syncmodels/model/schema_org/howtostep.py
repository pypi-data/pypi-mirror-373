# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .listitem import ListItem


@register_model
class HowToStep(ListItem):
    """A step in the instructions for how to achieve a result It is an ordered list with HowToDirection and or HowToTip items"""


# parent dependences
model_dependence("HowToStep", "ListItem")


# attribute dependences
model_dependence(
    "HowToStep",
)
