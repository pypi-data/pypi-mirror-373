# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .intangible import Intangible


@register_model
class VirtualLocation(Intangible):
    """An online or virtual location for attending events For example one may attend an online seminar or educational event While a virtual location may be used as the location of an event virtual locations should not be confused with physical locations in the real world"""


# parent dependences
model_dependence("VirtualLocation", "Intangible")


# attribute dependences
model_dependence(
    "VirtualLocation",
)
