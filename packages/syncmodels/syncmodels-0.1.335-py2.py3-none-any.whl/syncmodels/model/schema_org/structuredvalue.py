# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .intangible import Intangible


@register_model
class StructuredValue(Intangible):
    """Structured values are used when the value of a property has a more complex structure than simply being a textual value or a reference to another thing"""


# parent dependences
model_dependence("StructuredValue", "Intangible")


# attribute dependences
model_dependence(
    "StructuredValue",
)
