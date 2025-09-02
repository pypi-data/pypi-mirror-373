# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .enumeration import Enumeration


@register_model
class WarrantyScope(Enumeration):
    """A range of services that will be provided to a customer free of charge in case of a defect or malfunction of a product Commonly used values http purl org goodrelations v1 Labor BringIn http purl org goodrelations v1 PartsAndLabor BringIn http purl org goodrelations v1 PartsAndLabor PickUp"""


# parent dependences
model_dependence("WarrantyScope", "Enumeration")


# attribute dependences
model_dependence(
    "WarrantyScope",
)
