# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .definedtermset import DefinedTermSet


@register_model
class CategoryCodeSet(DefinedTermSet):
    """A set of Category Code values"""

    hasCategoryCode: Optional[
        Union["CategoryCode", str, List["CategoryCode"], List[str]]
    ] = Field(None, description="A Category code contained in this code set")


# parent dependences
model_dependence("CategoryCodeSet", "DefinedTermSet")


# attribute dependences
model_dependence(
    "CategoryCodeSet",
    "CategoryCode",
)
