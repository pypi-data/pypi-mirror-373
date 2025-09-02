# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Text, URL


# base imports
from .performinggroup import PerformingGroup


@register_model
class MusicGroup(PerformingGroup):
    """A musical group such as a band an orchestra or a choir Can also be a solo musician"""

    album: Optional[Union["MusicAlbum", str, List["MusicAlbum"], List[str]]] = Field(
        None, description="A music album Supersedes albums"
    )
    genre: Optional[Union[str, List[str]]] = Field(
        None, description="Genre of the creative work broadcast channel or group"
    )
    track: Optional[
        Union[
            "ItemList",
            "MusicRecording",
            str,
            List["ItemList"],
            List["MusicRecording"],
            List[str],
        ]
    ] = Field(
        None,
        description="A music recording track usually a single song If an ItemList is given the list should contain items of type MusicRecording Supersedes tracks",
    )


# parent dependences
model_dependence("MusicGroup", "PerformingGroup")


# attribute dependences
model_dependence(
    "MusicGroup",
    "ItemList",
    "MusicAlbum",
    "MusicRecording",
)
