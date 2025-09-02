# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .intangible import Intangible


@register_model
class Quantity(Intangible):
    """Quantities such as distance time mass weight etc Particular instances of say Mass are entities like 3 kg or 4 milligrams"""


# parent dependences
model_dependence("Quantity", "Intangible")


# attribute dependences
model_dependence(
    "Quantity",
)
