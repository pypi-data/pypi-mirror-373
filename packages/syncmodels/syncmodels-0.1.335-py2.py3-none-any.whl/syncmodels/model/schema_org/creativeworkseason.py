# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Date, DateTime, Integer, Text


# base imports
from .creativework import CreativeWork


@register_model
class CreativeWorkSeason(CreativeWork):
    """A media season e g TV radio video game etc"""

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
    endDate: Optional[Union[str, List[str]]] = Field(
        None, description="The end date and time of the item in ISO 8601 date format"
    )
    episode: Optional[Union["Episode", str, List["Episode"], List[str]]] = Field(
        None,
        description="An episode of a TV radio or game media within a series or season Supersedes episodes",
    )
    numberOfEpisodes: Optional[Union[int, List[int]]] = Field(
        None, description="The number of episodes in this season or series"
    )
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
    seasonNumber: Optional[Union[int, str, List[int], List[str]]] = Field(
        None, description="Position of the season within an ordered group of seasons"
    )
    startDate: Optional[Union[str, List[str]]] = Field(
        None, description="The start date and time of the item in ISO 8601 date format"
    )
    trailer: Optional[Union["VideoObject", str, List["VideoObject"], List[str]]] = (
        Field(
            None,
            description="The trailer of a movie or TV radio series season episode etc",
        )
    )


# parent dependences
model_dependence("CreativeWorkSeason", "CreativeWork")


# attribute dependences
model_dependence(
    "CreativeWorkSeason",
    "CreativeWorkSeries",
    "Episode",
    "Organization",
    "PerformingGroup",
    "Person",
    "VideoObject",
)
