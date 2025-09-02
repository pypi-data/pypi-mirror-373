# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .musicplaylist import MusicPlaylist


@register_model
class MusicAlbum(MusicPlaylist):
    """A collection of music tracks"""

    albumProductionType: Optional[
        Union[
            "MusicAlbumProductionType", str, List["MusicAlbumProductionType"], List[str]
        ]
    ] = Field(
        None,
        description="Classification of the album by its type of content soundtrack live album studio album etc",
    )
    albumRelease: Optional[
        Union["MusicRelease", str, List["MusicRelease"], List[str]]
    ] = Field(None, description="A release of this album Inverse property releaseOf")
    albumReleaseType: Optional[
        Union["MusicAlbumReleaseType", str, List["MusicAlbumReleaseType"], List[str]]
    ] = Field(
        None, description="The kind of release which this album is single EP or album"
    )
    byArtist: Optional[
        Union[
            "MusicGroup", "Person", str, List["MusicGroup"], List["Person"], List[str]
        ]
    ] = Field(None, description="The artist that performed this album or recording")


# parent dependences
model_dependence("MusicAlbum", "MusicPlaylist")


# attribute dependences
model_dependence(
    "MusicAlbum",
    "MusicAlbumProductionType",
    "MusicAlbumReleaseType",
    "MusicGroup",
    "MusicRelease",
    "Person",
)
