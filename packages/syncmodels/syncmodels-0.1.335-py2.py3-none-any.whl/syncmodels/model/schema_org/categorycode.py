# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Text, URL


# base imports
from .definedterm import DefinedTerm


@register_model
class CategoryCode(DefinedTerm):
    """A Category Code"""

    codeValue: Optional[Union[str, List[str]]] = Field(
        None, description="A short textual code that uniquely identifies the value"
    )
    inCodeSet: Optional[
        Union["CategoryCodeSet", str, List["CategoryCodeSet"], List[str]]
    ] = Field(None, description="A CategoryCodeSet that contains this category code")


# parent dependences
model_dependence("CategoryCode", "DefinedTerm")


# attribute dependences
model_dependence(
    "CategoryCode",
    "CategoryCodeSet",
)
