# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Integer, Text, Number


# base imports
from .creativework import CreativeWork


@register_model
class Clip(CreativeWork):
    """A short TV or radio program or a segment part of a program"""

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
    clipNumber: Optional[Union[int, str, List[int], List[str]]] = Field(
        None, description="Position of the clip within an ordered group of clips"
    )
    director: Optional[Union["Person", str, List["Person"], List[str]]] = Field(
        None,
        description="A director of e g TV radio movie video gaming etc content or of an event Directors can be associated with individual items or with a series episode clip Supersedes directors",
    )
    endOffset: Optional[
        Union[
            "HyperTocEntry", float, str, List["HyperTocEntry"], List[float], List[str]
        ]
    ] = Field(
        None,
        description="The end time of the clip expressed as the number of seconds from the beginning of the work",
    )
    musicBy: Optional[
        Union[
            "MusicGroup", "Person", str, List["MusicGroup"], List["Person"], List[str]
        ]
    ] = Field(None, description="The composer of the soundtrack")
    partOfEpisode: Optional[Union["Episode", str, List["Episode"], List[str]]] = Field(
        None, description="The episode to which this clip belongs"
    )
    partOfSeason: Optional[
        Union["CreativeWorkSeason", str, List["CreativeWorkSeason"], List[str]]
    ] = Field(None, description="The season to which this episode belongs")
    partOfSeries: Optional[
        Union["CreativeWorkSeries", str, List["CreativeWorkSeries"], List[str]]
    ] = Field(
        None,
        description="The series to which this episode or season belongs Supersedes partOfTVSeries",
    )
    startOffset: Optional[
        Union[
            "HyperTocEntry", float, str, List["HyperTocEntry"], List[float], List[str]
        ]
    ] = Field(
        None,
        description="The start time of the clip expressed as the number of seconds from the beginning of the work",
    )


# parent dependences
model_dependence("Clip", "CreativeWork")


# attribute dependences
model_dependence(
    "Clip",
    "CreativeWorkSeason",
    "CreativeWorkSeries",
    "Episode",
    "HyperTocEntry",
    "MusicGroup",
    "PerformingGroup",
    "Person",
)
