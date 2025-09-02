# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .statusenumeration import StatusEnumeration


@register_model
class ActionStatusType(StatusEnumeration):
    """The status of an Action"""


# parent dependences
model_dependence("ActionStatusType", "StatusEnumeration")


# attribute dependences
model_dependence(
    "ActionStatusType",
)
