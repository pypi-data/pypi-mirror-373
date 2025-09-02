# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Boolean, Text, Integer


# base imports
from .creativework import CreativeWork


@register_model
class Book(CreativeWork):
    """A book"""

    abridged: Optional[Union["bool", List["bool"]]] = Field(
        None, description="Indicates whether the book is an abridged edition"
    )
    bookEdition: Optional[Union[str, List[str]]] = Field(
        None, description="The edition of the book"
    )
    bookFormat: Optional[
        Union["BookFormatType", str, List["BookFormatType"], List[str]]
    ] = Field(None, description="The format of the book")
    illustrator: Optional[Union["Person", str, List["Person"], List[str]]] = Field(
        None, description="The illustrator of the book"
    )
    isbn: Optional[Union[str, List[str]]] = Field(
        None, description="The ISBN of the book"
    )
    numberOfPages: Optional[Union[int, List[int]]] = Field(
        None, description="The number of pages in the book"
    )


# parent dependences
model_dependence("Book", "CreativeWork")


# attribute dependences
model_dependence(
    "Book",
    "BookFormatType",
    "Person",
)
