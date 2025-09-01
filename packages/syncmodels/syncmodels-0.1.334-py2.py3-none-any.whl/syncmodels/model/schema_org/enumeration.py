# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .intangible import Intangible


@register_model
class Enumeration(Intangible):
    """Lists or enumerationsâ for example a list of cuisines or music genres etc"""

    supersededBy: Optional[
        Union[
            "Class",
            "Enumeration",
            "Property",
            str,
            List["Class"],
            List["Enumeration"],
            List["Property"],
            List[str],
        ]
    ] = Field(
        None,
        description="Relates a term i e a property class or enumeration to one that supersedes it",
    )


# parent dependences
model_dependence("Enumeration", "Intangible")


# attribute dependences
model_dependence(
    "Enumeration",
    "Class",
    "Property",
)
