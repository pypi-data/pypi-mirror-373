# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import (
    DateTime,
    Time,
    Date,
    Grant,
    Text,
    Boolean,
    DefinedTerm,
    URL,
    Integer,
    Event,
)


# base imports
from .thing import Thing


@register_model
class Event(Thing):
    """An event happening at a certain time and location such as a concert lecture or festival Ticketing information may be added via the offers property Repeated events may be structured as separate Event objects"""

    about: Optional[Union["Thing", str, List["Thing"], List[str]]] = Field(
        None, description="The subject matter of the content Inverse property subjectOf"
    )
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
    aggregateRating: Optional[
        Union["AggregateRating", str, List["AggregateRating"], List[str]]
    ] = Field(
        None,
        description="The overall rating based on a collection of reviews or ratings of the item",
    )
    attendee: Optional[
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
        description="A person or organization attending the event Supersedes attendees",
    )
    audience: Optional[Union["Audience", str, List["Audience"], List[str]]] = Field(
        None,
        description="An intended audience i e a group for whom something was created Supersedes serviceAudience",
    )
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
    contributor: Optional[
        Union[
            "Organization",
            "Person",
            str,
            List["Organization"],
            List["Person"],
            List[str],
        ]
    ] = Field(None, description="A secondary contributor to the CreativeWork or Event")
    director: Optional[Union["Person", str, List["Person"], List[str]]] = Field(
        None,
        description="A director of e g TV radio movie video gaming etc content or of an event Directors can be associated with individual items or with a series episode clip Supersedes directors",
    )
    doorTime: Optional[Union[str, List[str]]] = Field(
        None, description="The time admission will commence"
    )
    duration: Optional[Union["Duration", str, List["Duration"], List[str]]] = Field(
        None,
        description="The duration of the item movie audio recording event etc in ISO 8601 duration format",
    )
    endDate: Optional[Union[str, List[str]]] = Field(
        None, description="The end date and time of the item in ISO 8601 date format"
    )
    eventAttendanceMode: Optional[
        Union[
            "EventAttendanceModeEnumeration",
            str,
            List["EventAttendanceModeEnumeration"],
            List[str],
        ]
    ] = Field(
        None,
        description="The eventAttendanceMode of an event indicates whether it occurs online offline or a mix",
    )
    eventSchedule: Optional[Union["Schedule", str, List["Schedule"], List[str]]] = (
        Field(
            None,
            description="Associates an Event with a Schedule There are circumstances where it is preferable to share a schedule for a series of repeating events rather than data on the individual events themselves For example a website or application might prefer to publish a schedule for a weekly gym class rather than provide data on every event A schedule could be processed by applications to add forthcoming events to a calendar An Event that is associated with a Schedule using this property should not have startDate or endDate properties These are instead defined within the associated Schedule this avoids any ambiguity for clients using the data The property might have repeated values to specify different schedules e g for different months or seasons",
        )
    )
    eventStatus: Optional[
        Union["EventStatusType", str, List["EventStatusType"], List[str]]
    ] = Field(
        None,
        description="An eventStatus of an event represents its status particularly useful when an event is cancelled or rescheduled",
    )
    funder: Optional[
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
        description="A person or organization that supports sponsors something through some kind of financial contribution",
    )
    funding: Optional[Union[str, List[str]]] = Field(
        None,
        description="A Grant that directly or indirectly provide funding or sponsorship for this item See also ownershipFundingInfo Inverse property fundedItem",
    )
    inLanguage: Optional[Union["Language", str, List["Language"], List[str]]] = Field(
        None,
        description="The language of the content or performance or used in an action Please use one of the language codes from the IETF BCP 47 standard See also availableLanguage Supersedes language",
    )
    isAccessibleForFree: Optional[Union["bool", List["bool"]]] = Field(
        None,
        description="A flag to signal that the item event or place is accessible for free Supersedes free",
    )
    keywords: Optional[Union[str, List[str]]] = Field(
        None,
        description="Keywords or tags used to describe some item Multiple textual entries in a keywords list are typically delimited by commas or by repeating the property",
    )
    location: Optional[
        Union[
            "Place",
            "PostalAddress",
            "VirtualLocation",
            str,
            List["Place"],
            List["PostalAddress"],
            List["VirtualLocation"],
            List[str],
        ]
    ] = Field(
        None,
        description="The location of for example where an event is happening where an organization is located or where an action takes place",
    )
    maximumAttendeeCapacity: Optional[Union[int, List[int]]] = Field(
        None,
        description="The total number of individuals that may attend an event or venue",
    )
    maximumPhysicalAttendeeCapacity: Optional[Union[int, List[int]]] = Field(
        None,
        description="The maximum physical attendee capacity of an Event whose eventAttendanceMode is OfflineEventAttendanceMode or the offline aspects in the case of a MixedEventAttendanceMode",
    )
    maximumVirtualAttendeeCapacity: Optional[Union[int, List[int]]] = Field(
        None,
        description="The maximum virtual attendee capacity of an Event whose eventAttendanceMode is OnlineEventAttendanceMode or the online aspects in the case of a MixedEventAttendanceMode",
    )
    offers: Optional[
        Union["Demand", "Offer", str, List["Demand"], List["Offer"], List[str]]
    ] = Field(
        None,
        description="An offer to provide this item for example an offer to sell a product rent the DVD of a movie perform a service or give away tickets to an event Use businessFunction to indicate the kind of transaction offered i e sell lease etc This property can also be used to describe a Demand While this property is listed as expected on a number of common types it can be used in others In that case using a second type such as Product or a subtype of Product can clarify the nature of the offer Inverse property itemOffered",
    )
    organizer: Optional[
        Union[
            "Organization",
            "Person",
            str,
            List["Organization"],
            List["Person"],
            List[str],
        ]
    ] = Field(None, description="An organizer of an Event")
    performer: Optional[
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
        description="A performer at the event for example a presenter musician musical group or actor Supersedes performers",
    )
    previousStartDate: Optional[Union[str, List[str]]] = Field(
        None,
        description="Used in conjunction with eventStatus for rescheduled or cancelled events This property contains the previously scheduled start date For rescheduled events the startDate property should be used for the newly scheduled start date In the rare case of an event that has been postponed and rescheduled multiple times this field may be repeated",
    )
    recordedIn: Optional[
        Union["CreativeWork", str, List["CreativeWork"], List[str]]
    ] = Field(
        None,
        description="The CreativeWork that captured all or part of this Event Inverse property recordedAt",
    )
    remainingAttendeeCapacity: Optional[Union[int, List[int]]] = Field(
        None,
        description="The number of attendee places for an event that remain unallocated",
    )
    review: Optional[Union["Review", str, List["Review"], List[str]]] = Field(
        None, description="A review of the item Supersedes reviews"
    )
    sponsor: Optional[
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
        description="A person or organization that supports a thing through a pledge promise or financial contribution E g a sponsor of a Medical Study or a corporate sponsor of an event",
    )
    startDate: Optional[Union[str, List[str]]] = Field(
        None, description="The start date and time of the item in ISO 8601 date format"
    )
    subEvent: Optional[Union[str, List[str]]] = Field(
        None,
        description="An Event that is part of this event For example a conference event includes many presentations each of which is a subEvent of the conference Supersedes subEvents Inverse property superEvent",
    )
    superEvent: Optional[Union[str, List[str]]] = Field(
        None,
        description="An event that this event is a part of For example a collection of individual music performances might each have a music festival as their superEvent Inverse property subEvent",
    )
    translator: Optional[
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
        description="Organization or person who adapts a creative work to different languages regional differences and technical requirements of a target market or that translates during some event",
    )
    typicalAgeRange: Optional[Union[str, List[str]]] = Field(
        None, description="The typical expected age range e g 7 9 11"
    )
    workFeatured: Optional[
        Union["CreativeWork", str, List["CreativeWork"], List[str]]
    ] = Field(
        None,
        description="A work featured in some event e g exhibited in an ExhibitionEvent Specific subproperties are available for workPerformed e g a play or a workPresented a Movie at a ScreeningEvent",
    )
    workPerformed: Optional[
        Union["CreativeWork", str, List["CreativeWork"], List[str]]
    ] = Field(
        None,
        description="A work performed in some event for example a play performed in a TheaterEvent",
    )


# parent dependences
model_dependence("Event", "Thing")


# attribute dependences
model_dependence(
    "Event",
    "AggregateRating",
    "Audience",
    "CreativeWork",
    "Demand",
    "Duration",
    "EventAttendanceModeEnumeration",
    "EventStatusType",
    "Language",
    "Offer",
    "Organization",
    "PerformingGroup",
    "Person",
    "Place",
    "PostalAddress",
    "Review",
    "Schedule",
    "Thing",
    "VirtualLocation",
)
