# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .enumeration import Enumeration


@register_model
class MediaEnumeration(Enumeration):
    """MediaEnumeration enumerations are lists of codes labels etc useful for describing media objects They may be reflections of externally developed lists or created at schema org or a combination"""


# parent dependences
model_dependence("MediaEnumeration", "Enumeration")


# attribute dependences
model_dependence(
    "MediaEnumeration",
)
