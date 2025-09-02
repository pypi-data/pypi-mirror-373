# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Text


# base imports
from .action import Action


@register_model
class SearchAction(Action):
    """The act of searching for an object Related actions FindAction SearchAction generally leads to a FindAction but not necessarily"""

    query: Optional[Union[str, List[str]]] = Field(
        None, description="A sub property of instrument The query used on this action"
    )


# parent dependences
model_dependence("SearchAction", "Action")


# attribute dependences
model_dependence(
    "SearchAction",
)
