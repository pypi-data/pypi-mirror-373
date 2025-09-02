from pydantic import Field
from typing import Optional, Union

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .intangible import Intangible


@register_model
class Class(Intangible):
    """A class also often called a Type equivalent to rdfs Class"""

    supersededBy: Optional[Union["Class", "Enumeration", "Property"]] = Field(
        None,
        description="Relates a term i e a property class or enumeration to one that supersedes it",
    )


# attribute dependences
model_dependence(
    "Class",
    "Property",
    "Class",
    "Enumeration",
)
