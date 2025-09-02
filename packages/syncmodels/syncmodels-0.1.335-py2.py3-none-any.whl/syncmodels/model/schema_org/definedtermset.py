# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import DefinedTerm


# base imports
from .creativework import CreativeWork


@register_model
class DefinedTermSet(CreativeWork):
    """A set of defined terms for example a set of categories or a classification scheme a glossary dictionary or enumeration"""

    hasDefinedTerm: Optional[Union[str, List[str]]] = Field(
        None, description="A Defined Term contained in this term set"
    )


# parent dependences
model_dependence("DefinedTermSet", "CreativeWork")


# attribute dependences
model_dependence(
    "DefinedTermSet",
)
