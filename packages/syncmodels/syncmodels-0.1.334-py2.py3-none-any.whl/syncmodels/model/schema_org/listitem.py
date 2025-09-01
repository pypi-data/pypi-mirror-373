# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Integer, Text


# base imports
from .intangible import Intangible


@register_model
class ListItem(Intangible):
    """An list item e g a step in a checklist or how to description"""

    item: Optional[Union["Thing", str, List["Thing"], List[str]]] = Field(
        None,
        description="An entity represented by an entry in a list or data feed e g an artist in a list of artists",
    )
    nextItem: Optional[Union["ListItem", str, List["ListItem"], List[str]]] = Field(
        None, description="A link to the ListItem that follows the current one"
    )
    position: Optional[Union[int, str, List[int], List[str]]] = Field(
        None, description="The position of an item in a series or sequence of items"
    )
    previousItem: Optional[Union["ListItem", str, List["ListItem"], List[str]]] = Field(
        None, description="A link to the ListItem that precedes the current one"
    )


# parent dependences
model_dependence("ListItem", "Intangible")


# attribute dependences
model_dependence(
    "ListItem",
    "Thing",
)
