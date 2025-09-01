# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Event, Text


# base imports
from .creativework import CreativeWork


@register_model
class MusicComposition(CreativeWork):
    """A musical composition"""

    composer: Optional[
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
        description="The person or organization who wrote a composition or who is the composer of a work performed at some event",
    )
    firstPerformance: Optional[Union[str, List[str]]] = Field(
        None, description="The date and place the work was first performed"
    )
    includedComposition: Optional[
        Union["MusicComposition", str, List["MusicComposition"], List[str]]
    ] = Field(
        None,
        description="Smaller compositions included in this work e g a movement in a symphony",
    )
    iswcCode: Optional[Union[str, List[str]]] = Field(
        None,
        description="The International Standard Musical Work Code for the composition",
    )
    lyricist: Optional[Union["Person", str, List["Person"], List[str]]] = Field(
        None, description="The person who wrote the words"
    )
    lyrics: Optional[Union["CreativeWork", str, List["CreativeWork"], List[str]]] = (
        Field(None, description="The words in the song")
    )
    musicArrangement: Optional[
        Union["MusicComposition", str, List["MusicComposition"], List[str]]
    ] = Field(None, description="An arrangement derived from the composition")
    musicCompositionForm: Optional[Union[str, List[str]]] = Field(
        None, description="The type of composition e g overture sonata symphony etc"
    )
    musicalKey: Optional[Union[str, List[str]]] = Field(
        None, description="The key mode or scale this composition uses"
    )
    recordedAs: Optional[
        Union["MusicRecording", str, List["MusicRecording"], List[str]]
    ] = Field(
        None, description="An audio recording of the work Inverse property recordingOf"
    )


# parent dependences
model_dependence("MusicComposition", "CreativeWork")


# attribute dependences
model_dependence(
    "MusicComposition",
    "CreativeWork",
    "MusicRecording",
    "Organization",
    "Person",
)
