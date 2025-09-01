# from __future__ import annotations

from pydantic import Field
from typing import Optional, Union, ForwardRef

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .enumeration import Enumeration


@register_model
class AdultOrientedEnumeration(Enumeration):
    """Enumeration of considerations that make a product relevant or potentially restricted for adults only"""


model_dependence("AdultOrientedEnumeration", "Enumeration")
# attribute dependences
model_dependence(
    "AdultOrientedEnumeration",
)
