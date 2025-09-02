# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .organization import Organization


@register_model
class PerformingGroup(Organization):
    """A performance group such as a band an orchestra or a circus"""


# parent dependences
model_dependence("PerformingGroup", "Organization")


# attribute dependences
model_dependence(
    "PerformingGroup",
)
