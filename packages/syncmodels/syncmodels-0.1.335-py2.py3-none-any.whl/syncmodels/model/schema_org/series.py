# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .intangible import Intangible


@register_model
class Series(Intangible):
    """A Series in schema org is a group of related items typically but not necessarily of the same kind See also CreativeWorkSeries EventSeries"""


# parent dependences
model_dependence("Series", "Intangible")


# attribute dependences
model_dependence(
    "Series",
)
