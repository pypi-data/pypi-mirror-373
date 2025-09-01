# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .enumeration import Enumeration


@register_model
class MusicReleaseFormatType(Enumeration):
    """Format of this release the type of recording media used i e compact disc digital media LP etc"""


# parent dependences
model_dependence("MusicReleaseFormatType", "Enumeration")


# attribute dependences
model_dependence(
    "MusicReleaseFormatType",
)
