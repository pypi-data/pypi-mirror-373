# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .enumeration import Enumeration


@register_model
class ItemListOrderType(Enumeration):
    """Enumerated for values for itemListOrder for indicating how an ordered ItemList is organized"""


# parent dependences
model_dependence("ItemListOrderType", "Enumeration")


# attribute dependences
model_dependence(
    "ItemListOrderType",
)
