# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .enumeration import Enumeration


@register_model
class MusicAlbumProductionType(Enumeration):
    """Classification of the album by its type of content soundtrack live album studio album etc"""


# parent dependences
model_dependence("MusicAlbumProductionType", "Enumeration")


# attribute dependences
model_dependence(
    "MusicAlbumProductionType",
)
