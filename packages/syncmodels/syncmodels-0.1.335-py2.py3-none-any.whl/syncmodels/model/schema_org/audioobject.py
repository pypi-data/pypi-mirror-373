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
class AudioObject(MediaObject):
    """An audio file"""

    caption: Optional[Union["MediaObject", str, List["MediaObject"], List[str]]] = (
        Field(
            None,
            description="The caption for this object For downloadable machine formats closed caption subtitles etc use MediaObject and indicate the encodingFormat",
        )
    )
    embeddedTextCaption: Optional[Union[str, List[str]]] = Field(
        None,
        description="Represents textual captioning from a MediaObject e g text of a meme",
    )
    transcript: Optional[Union[str, List[str]]] = Field(
        None,
        description="If this MediaObject is an AudioObject or VideoObject the transcript of that object",
    )


# parent dependences
model_dependence("AudioObject", "MediaObject")


# attribute dependences
model_dependence(
    "AudioObject",
    "MediaObject",
)
