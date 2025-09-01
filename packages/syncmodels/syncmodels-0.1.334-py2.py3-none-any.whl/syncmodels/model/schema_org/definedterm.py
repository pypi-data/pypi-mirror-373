# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import URL, Text


# base imports
from .intangible import Intangible


@register_model
class DefinedTerm(Intangible):
    """A word name acronym phrase etc with a formal definition Often used in the context of category or subject classification glossaries or dictionaries product or creative work types etc Use the name property for the term being defined use termCode if the term has an alpha numeric code allocated use description to provide the definition of the term"""

    inDefinedTermSet: Optional[
        Union["DefinedTermSet", str, List["DefinedTermSet"], List[str]]
    ] = Field(None, description="A DefinedTermSet that contains this term")
    termCode: Optional[Union[str, List[str]]] = Field(
        None,
        description="A code that identifies this DefinedTerm within a DefinedTermSet",
    )


# parent dependences
model_dependence("DefinedTerm", "Intangible")


# attribute dependences
model_dependence(
    "DefinedTerm",
    "DefinedTermSet",
)
