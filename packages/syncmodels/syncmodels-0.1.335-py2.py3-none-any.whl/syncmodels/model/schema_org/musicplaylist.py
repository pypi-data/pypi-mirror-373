# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Integer


# base imports
from .creativework import CreativeWork


@register_model
class MusicPlaylist(CreativeWork):
    """A collection of music tracks in playlist form"""

    numTracks: Optional[Union[int, List[int]]] = Field(
        None, description="The number of tracks in this album or playlist"
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
model_dependence("MusicPlaylist", "CreativeWork")


# attribute dependences
model_dependence(
    "MusicPlaylist",
    "ItemList",
    "MusicRecording",
)
