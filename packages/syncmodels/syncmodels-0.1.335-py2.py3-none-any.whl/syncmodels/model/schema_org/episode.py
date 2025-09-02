# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Integer, Text


# base imports
from .creativework import CreativeWork


@register_model
class Episode(CreativeWork):
    """A media episode e g TV radio video game which can be part of a series or season"""

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
    director: Optional[Union["Person", str, List["Person"], List[str]]] = Field(
        None,
        description="A director of e g TV radio movie video gaming etc content or of an event Directors can be associated with individual items or with a series episode clip Supersedes directors",
    )
    duration: Optional[Union["Duration", str, List["Duration"], List[str]]] = Field(
        None,
        description="The duration of the item movie audio recording event etc in ISO 8601 duration format",
    )
    episodeNumber: Optional[Union[int, str, List[int], List[str]]] = Field(
        None, description="Position of the episode within an ordered group of episodes"
    )
    musicBy: Optional[
        Union[
            "MusicGroup", "Person", str, List["MusicGroup"], List["Person"], List[str]
        ]
    ] = Field(None, description="The composer of the soundtrack")
    partOfSeason: Optional[
        Union["CreativeWorkSeason", str, List["CreativeWorkSeason"], List[str]]
    ] = Field(None, description="The season to which this episode belongs")
    partOfSeries: Optional[
        Union["CreativeWorkSeries", str, List["CreativeWorkSeries"], List[str]]
    ] = Field(
        None,
        description="The series to which this episode or season belongs Supersedes partOfTVSeries",
    )
    productionCompany: Optional[
        Union["Organization", str, List["Organization"], List[str]]
    ] = Field(
        None,
        description="The production company or studio responsible for the item e g series video game episode etc",
    )
    trailer: Optional[Union["VideoObject", str, List["VideoObject"], List[str]]] = (
        Field(
            None,
            description="The trailer of a movie or TV radio series season episode etc",
        )
    )


# parent dependences
model_dependence("Episode", "CreativeWork")


# attribute dependences
model_dependence(
    "Episode",
    "CreativeWorkSeason",
    "CreativeWorkSeries",
    "Duration",
    "MusicGroup",
    "Organization",
    "PerformingGroup",
    "Person",
    "VideoObject",
)
