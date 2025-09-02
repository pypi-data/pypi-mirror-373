# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Date, DateTime


# base imports
from .propertyvalue import PropertyValue


@register_model
class LocationFeatureSpecification(PropertyValue):
    """Specifies a location feature by providing a structured value representing a feature of an accommodation as a property value pair of varying degrees of formality"""

    hoursAvailable: Optional[
        Union[
            "OpeningHoursSpecification",
            str,
            List["OpeningHoursSpecification"],
            List[str],
        ]
    ] = Field(
        None, description="The hours during which this service or contact is available"
    )
    validFrom: Optional[Union[str, List[str]]] = Field(
        None, description="The date when the item becomes valid"
    )
    validThrough: Optional[Union[str, List[str]]] = Field(
        None,
        description="The date after when the item is not valid For example the end of an offer salary period or a period of opening hours",
    )


# parent dependences
model_dependence("LocationFeatureSpecification", "PropertyValue")


# attribute dependences
model_dependence(
    "LocationFeatureSpecification",
    "OpeningHoursSpecification",
)
