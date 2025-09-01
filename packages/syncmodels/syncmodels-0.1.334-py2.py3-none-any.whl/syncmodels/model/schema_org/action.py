# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import DateTime, Time, Text, URL


# base imports
from .thing import Thing


@register_model
class Action(Thing):
    """An action performed by a direct agent and indirect participants upon a direct object Optionally happens at a location with the help of an inanimate instrument The execution of the action may produce a result Specific action sub type documentation specifies the exact expectation of each argument role See also blog post and Actions overview document"""

    actionProcess: Optional[Union["HowTo", str, List["HowTo"], List[str]]] = Field(
        None, description="Description of the process by which the action was performed"
    )
    actionStatus: Optional[
        Union["ActionStatusType", str, List["ActionStatusType"], List[str]]
    ] = Field(None, description="Indicates the current disposition of the Action")
    agent: Optional[
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
        description="The direct performer or driver of the action animate or inanimate E g John wrote a book",
    )
    endTime: Optional[Union[str, List[str]]] = Field(
        None,
        description="The endTime of something For a reserved event or service e g FoodEstablishmentReservation the time that it is expected to end For actions that span a period of time when the action was performed E g John wrote a book from January to December For media including audio and video it s the time offset of the end of a clip within a larger file Note that Event uses startDate endDate instead of startTime endTime even when describing dates with times This situation may be clarified in future revisions",
    )
    error: Optional[Union["Thing", str, List["Thing"], List[str]]] = Field(
        None,
        description="For failed actions more information on the cause of the failure",
    )
    instrument: Optional[Union["Thing", str, List["Thing"], List[str]]] = Field(
        None,
        description="The object that helped the agent perform the action E g John wrote a book with a pen",
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
    object: Optional[Union["Thing", str, List["Thing"], List[str]]] = Field(
        None,
        description="The object upon which the action is carried out whose state is kept intact or changed Also known as the semantic roles patient affected or undergoer which change their state or theme which doesn t E g John read a book",
    )
    participant: Optional[
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
        description="Other co agents that participated in the action indirectly E g John wrote a book with Steve",
    )
    provider: Optional[
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
        description="The service provider service operator or service performer the goods producer Another party a seller may offer those services or goods on behalf of the provider A provider may also serve as the seller Supersedes carrier",
    )
    result: Optional[Union["Thing", str, List["Thing"], List[str]]] = Field(
        None, description="The result produced in the action E g John wrote a book"
    )
    startTime: Optional[Union[str, List[str]]] = Field(
        None,
        description="The startTime of something For a reserved event or service e g FoodEstablishmentReservation the time that it is expected to start For actions that span a period of time when the action was performed E g John wrote a book from January to December For media including audio and video it s the time offset of the start of a clip within a larger file Note that Event uses startDate endDate instead of startTime endTime even when describing dates with times This situation may be clarified in future revisions",
    )
    target: Optional[Union["EntryPoint", str, List["EntryPoint"], List[str]]] = Field(
        None, description="Indicates a target EntryPoint or url for an Action"
    )


# parent dependences
model_dependence("Action", "Thing")


# attribute dependences
model_dependence(
    "Action",
    "ActionStatusType",
    "EntryPoint",
    "HowTo",
    "Organization",
    "Person",
    "Place",
    "PostalAddress",
    "Thing",
    "VirtualLocation",
)
