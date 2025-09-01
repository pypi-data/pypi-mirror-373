# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .place import Place


@register_model
class AdministrativeArea(Place):
    """A geographical region typically under the jurisdiction of a particular government"""


# parent dependences
model_dependence("AdministrativeArea", "Place")


# attribute dependences
model_dependence(
    "AdministrativeArea",
)
