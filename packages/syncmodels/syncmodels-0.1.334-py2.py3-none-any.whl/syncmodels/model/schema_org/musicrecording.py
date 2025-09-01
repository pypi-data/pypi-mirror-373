# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Text


# base imports
from .creativework import CreativeWork


@register_model
class MusicRecording(CreativeWork):
    """A music recording track usually a single song"""

    byArtist: Optional[
        Union[
            "MusicGroup", "Person", str, List["MusicGroup"], List["Person"], List[str]
        ]
    ] = Field(None, description="The artist that performed this album or recording")
    duration: Optional[Union["Duration", str, List["Duration"], List[str]]] = Field(
        None,
        description="The duration of the item movie audio recording event etc in ISO 8601 duration format",
    )
    inAlbum: Optional[Union["MusicAlbum", str, List["MusicAlbum"], List[str]]] = Field(
        None, description="The album to which this recording belongs"
    )
    inPlaylist: Optional[
        Union["MusicPlaylist", str, List["MusicPlaylist"], List[str]]
    ] = Field(None, description="The playlist to which this recording belongs")
    isrcCode: Optional[Union[str, List[str]]] = Field(
        None, description="The International Standard Recording Code for the recording"
    )
    recordingOf: Optional[
        Union["MusicComposition", str, List["MusicComposition"], List[str]]
    ] = Field(
        None,
        description="The composition this track is a recording of Inverse property recordedAs",
    )


# parent dependences
model_dependence("MusicRecording", "CreativeWork")


# attribute dependences
model_dependence(
    "MusicRecording",
    "Duration",
    "MusicAlbum",
    "MusicComposition",
    "MusicGroup",
    "MusicPlaylist",
    "Person",
)
