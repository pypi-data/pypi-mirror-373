# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .thing import Thing


@register_model
class Intangible(Thing):
    """A utility class that serves as the umbrella for a number of intangible things such as quantities structured values etc"""


# parent dependences
model_dependence("Intangible", "Thing")


# attribute dependences
model_dependence(
    "Intangible",
)
