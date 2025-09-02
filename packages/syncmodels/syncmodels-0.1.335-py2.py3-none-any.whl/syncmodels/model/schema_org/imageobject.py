# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Text, PropertyValue, Boolean


# base imports
from .mediaobject import MediaObject


@register_model
class ImageObject(MediaObject):
    """An image file"""

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
    exifData: Optional[Union[str, List[str]]] = Field(
        None, description="exif data for this object"
    )
    representativeOfPage: Optional[Union["bool", List["bool"]]] = Field(
        None,
        description="Indicates whether this image is representative of the content of the page",
    )


# parent dependences
model_dependence("ImageObject", "MediaObject")


# attribute dependences
model_dependence(
    "ImageObject",
    "MediaObject",
)
