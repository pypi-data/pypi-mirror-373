# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Text


# base imports
from .musicplaylist import MusicPlaylist


@register_model
class MusicRelease(MusicPlaylist):
    """A MusicRelease is a specific release of a music album"""

    catalogNumber: Optional[Union[int, str, List[int], List[str]]] = Field(
        None, description="The catalog number for the release"
    )
    creditedTo: Optional[
        Union[
            "Organization",
            "Person",
            str,
            List["Organization"],
            List["Person"],
            List[str],
        ]
    ] = Field(
        None,
        description="The group the release is credited to if different than the byArtist For example Red and Blue is credited to Stefani Germanotta Band but by Lady Gaga",
    )
    duration: Optional[Union["Duration", str, List["Duration"], List[str]]] = Field(
        None,
        description="The duration of the item movie audio recording event etc in ISO 8601 duration format",
    )
    musicReleaseFormat: Optional[
        Union["MusicReleaseFormatType", str, List["MusicReleaseFormatType"], List[str]]
    ] = Field(
        None,
        description="Format of this release the type of recording media used i e compact disc digital media LP etc",
    )
    recordLabel: Optional[
        Union["Organization", str, List["Organization"], List[str]]
    ] = Field(None, description="The label that issued the release")
    releaseOf: Optional[Union["MusicAlbum", str, List["MusicAlbum"], List[str]]] = (
        Field(
            None,
            description="The album this is a release of Inverse property albumRelease",
        )
    )


# parent dependences
model_dependence("MusicRelease", "MusicPlaylist")


# attribute dependences
model_dependence(
    "MusicRelease",
    "Duration",
    "MusicAlbum",
    "MusicReleaseFormatType",
    "Organization",
    "Person",
)
