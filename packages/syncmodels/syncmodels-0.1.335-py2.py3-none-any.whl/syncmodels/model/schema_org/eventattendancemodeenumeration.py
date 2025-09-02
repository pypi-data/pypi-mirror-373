# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .enumeration import Enumeration


@register_model
class EventAttendanceModeEnumeration(Enumeration):
    """An EventAttendanceModeEnumeration value is one of potentially several modes of organising an event relating to whether it is online or offline"""


# parent dependences
model_dependence("EventAttendanceModeEnumeration", "Enumeration")


# attribute dependences
model_dependence(
    "EventAttendanceModeEnumeration",
)
