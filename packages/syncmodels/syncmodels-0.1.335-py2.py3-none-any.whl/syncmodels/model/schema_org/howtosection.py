# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .listitem import ListItem


@register_model
class HowToSection(ListItem):
    """A sub grouping of steps in the instructions for how to achieve a result e g steps for making a pie crust within a pie recipe"""


# parent dependences
model_dependence("HowToSection", "ListItem")


# attribute dependences
model_dependence(
    "HowToSection",
)
