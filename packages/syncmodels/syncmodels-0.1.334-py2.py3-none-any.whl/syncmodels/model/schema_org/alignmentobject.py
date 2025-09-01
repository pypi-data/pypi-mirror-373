# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Text, URL


# base imports
from .intangible import Intangible


@register_model
class AlignmentObject(Intangible):
    """An intangible item that describes an alignment between a learning resource and a node in an educational framework Should not be used where the nature of the alignment can be described using a simple property for example to express that a resource teaches or assesses a competency"""

    alignmentType: Optional[Union[str, List[str]]] = Field(
        None,
        description="A category of alignment between the learning resource and the framework node Recommended values include requires textComplexity readingLevel and educationalSubject",
    )
    educationalFramework: Optional[Union[str, List[str]]] = Field(
        None,
        description="The framework to which the resource being described is aligned",
    )
    targetDescription: Optional[Union[str, List[str]]] = Field(
        None,
        description="The description of a node in an established educational framework",
    )
    targetName: Optional[Union[str, List[str]]] = Field(
        None, description="The name of a node in an established educational framework"
    )
    targetUrl: Optional[Union[str, List[str]]] = Field(
        None, description="The URL of a node in an established educational framework"
    )


# parent dependences
model_dependence("AlignmentObject", "Intangible")


# attribute dependences
model_dependence(
    "AlignmentObject",
)
