# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .intangible import Intangible


@register_model
class Property(Intangible):
    """A property used to indicate attributes and relationships of some Thing equivalent to rdf Property"""

    domainIncludes: Optional[Union["Class", str, List["Class"], List[str]]] = Field(
        None,
        description="Relates a property to a class that is one of the type s the property is expected to be used on",
    )
    inverseOf: Optional[Union["Property", str, List["Property"], List[str]]] = Field(
        None,
        description="Relates a property to a property that is its inverse Inverse properties relate the same pairs of items to each other but in reversed direction For example the alumni and alumniOf properties are inverseOf each other Some properties don t have explicit inverses in these situations RDFa and JSON LD syntax for reverse properties can be used",
    )
    rangeIncludes: Optional[Union["Class", str, List["Class"], List[str]]] = Field(
        None,
        description="Relates a property to a class that constitutes one of the expected type s for values of the property",
    )
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
model_dependence("Property", "Intangible")


# attribute dependences
model_dependence(
    "Property",
    "Class",
    "Enumeration",
)
