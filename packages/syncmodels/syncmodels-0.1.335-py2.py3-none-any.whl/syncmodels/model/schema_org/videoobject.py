# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Text


# base imports
from .mediaobject import MediaObject


@register_model
class VideoObject(MediaObject):
    """A video file"""

    actor: Optional[
        Union[
            "PerformingGroup",
            "Person",
            str,
            List["PerformingGroup"],
            List["Person"],
            List[str],
        ]
    ] = Field(
        None,
        description="An actor individual or a group e g in TV radio movie video games etc or in an event Actors can be associated with individual items or with a series episode clip Supersedes actors",
    )
    caption: Optional[Union["MediaObject", str, List["MediaObject"], List[str]]] = (
        Field(
            None,
            description="The caption for this object For downloadable machine formats closed caption subtitles etc use MediaObject and indicate the encodingFormat",
        )
    )
    director: Optional[Union["Person", str, List["Person"], List[str]]] = Field(
        None,
        description="A director of e g TV radio movie video gaming etc content or of an event Directors can be associated with individual items or with a series episode clip Supersedes directors",
    )
    embeddedTextCaption: Optional[Union[str, List[str]]] = Field(
        None,
        description="Represents textual captioning from a MediaObject e g text of a meme",
    )
    musicBy: Optional[
        Union[
            "MusicGroup", "Person", str, List["MusicGroup"], List["Person"], List[str]
        ]
    ] = Field(None, description="The composer of the soundtrack")
    transcript: Optional[Union[str, List[str]]] = Field(
        None,
        description="If this MediaObject is an AudioObject or VideoObject the transcript of that object",
    )
    videoFrameSize: Optional[Union[str, List[str]]] = Field(
        None, description="The frame size of the video"
    )
    videoQuality: Optional[Union[str, List[str]]] = Field(
        None, description="The quality of the video"
    )


# parent dependences
model_dependence("VideoObject", "MediaObject")


# attribute dependences
model_dependence(
    "VideoObject",
    "MediaObject",
    "MusicGroup",
    "PerformingGroup",
    "Person",
)
