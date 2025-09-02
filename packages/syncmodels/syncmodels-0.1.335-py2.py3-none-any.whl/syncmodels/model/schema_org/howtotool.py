# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .howtoitem import HowToItem


@register_model
class HowToTool(HowToItem):
    """A tool used but not consumed when performing instructions for how to achieve a result"""


# parent dependences
model_dependence("HowToTool", "HowToItem")


# attribute dependences
model_dependence(
    "HowToTool",
)
