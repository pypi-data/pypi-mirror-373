# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .enumeration import Enumeration


@register_model
class MeasurementTypeEnumeration(Enumeration):
    """Enumeration of common measurement types or dimensions for example chest for a person inseam for pants gauge for screws or wheel for bicycles"""


# parent dependences
model_dependence("MeasurementTypeEnumeration", "Enumeration")


# attribute dependences
model_dependence(
    "MeasurementTypeEnumeration",
)
