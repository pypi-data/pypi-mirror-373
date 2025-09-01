# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .enumeration import Enumeration


@register_model
class MusicAlbumReleaseType(Enumeration):
    """The kind of release which this album is single EP or album"""


# parent dependences
model_dependence("MusicAlbumReleaseType", "Enumeration")


# attribute dependences
model_dependence(
    "MusicAlbumReleaseType",
)
