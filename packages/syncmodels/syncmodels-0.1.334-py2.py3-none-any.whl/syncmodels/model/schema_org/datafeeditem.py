# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Date, DateTime


# base imports
from .intangible import Intangible


@register_model
class DataFeedItem(Intangible):
    """A single item within a larger data feed"""

    dateCreated: Optional[Union[str, List[str]]] = Field(
        None,
        description="The date on which the CreativeWork was created or the item was added to a DataFeed",
    )
    dateDeleted: Optional[Union[str, List[str]]] = Field(
        None, description="The datetime the item was removed from the DataFeed"
    )
    dateModified: Optional[Union[str, List[str]]] = Field(
        None,
        description="The date on which the CreativeWork was most recently modified or when the item s entry was modified within a DataFeed",
    )
    item: Optional[Union["Thing", str, List["Thing"], List[str]]] = Field(
        None,
        description="An entity represented by an entry in a list or data feed e g an artist in a list of artists",
    )


# parent dependences
model_dependence("DataFeedItem", "Intangible")


# attribute dependences
model_dependence(
    "DataFeedItem",
    "Thing",
)
