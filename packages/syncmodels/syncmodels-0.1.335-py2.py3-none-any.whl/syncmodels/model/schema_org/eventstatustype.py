# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .statusenumeration import StatusEnumeration


@register_model
class EventStatusType(StatusEnumeration):
    """EventStatusType is an enumeration type whose instances represent several states that an Event may be in"""


# parent dependences
model_dependence("EventStatusType", "StatusEnumeration")


# attribute dependences
model_dependence(
    "EventStatusType",
)
