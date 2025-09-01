# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .enumeration import Enumeration


@register_model
class DigitalPlatformEnumeration(Enumeration):
    """Enumerates some common technology platforms for use with properties such as actionPlatform It is not supposed to be comprehensive when a suitable code is not enumerated here textual or URL values can be used instead These codes are at a fairly high level and do not deal with versioning and other nuance Additional codes can be suggested in github"""


# parent dependences
model_dependence("DigitalPlatformEnumeration", "Enumeration")


# attribute dependences
model_dependence(
    "DigitalPlatformEnumeration",
)
