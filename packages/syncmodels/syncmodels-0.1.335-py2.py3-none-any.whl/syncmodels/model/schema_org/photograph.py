# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .creativework import CreativeWork


@register_model
class Photograph(CreativeWork):
    """A photograph"""


# parent dependences
model_dependence("Photograph", "CreativeWork")


# attribute dependences
model_dependence(
    "Photograph",
)
