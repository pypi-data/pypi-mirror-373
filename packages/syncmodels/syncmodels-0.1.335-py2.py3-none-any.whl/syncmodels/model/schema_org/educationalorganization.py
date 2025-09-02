# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .organization import Organization


@register_model
class EducationalOrganization(Organization):
    """An educational organization"""

    alumni: Optional[Union["Person", str, List["Person"], List[str]]] = Field(
        None, description="Alumni of an organization Inverse property alumniOf"
    )


# parent dependences
model_dependence("EducationalOrganization", "Organization")


# attribute dependences
model_dependence(
    "EducationalOrganization",
    "Person",
)
