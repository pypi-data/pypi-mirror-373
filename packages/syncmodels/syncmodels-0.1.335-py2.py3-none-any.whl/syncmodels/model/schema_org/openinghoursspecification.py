# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Time, Date, DateTime


# base imports
from .structuredvalue import StructuredValue


@register_model
class OpeningHoursSpecification(StructuredValue):
    """A structured value providing information about the opening hours of a place or a certain service inside a place The place is open if the opens property is specified and closed otherwise If the value for the closes property is less than the value for the opens property then the hour range is assumed to span over the next day"""

    closes: Optional[Union[str, List[str]]] = Field(
        None,
        description="The closing hour of the place or service on the given day s of the week",
    )
    dayOfWeek: Optional[Union["DayOfWeek", str, List["DayOfWeek"], List[str]]] = Field(
        None, description="The day of the week for which these opening hours are valid"
    )
    opens: Optional[Union[str, List[str]]] = Field(
        None,
        description="The opening hour of the place or service on the given day s of the week",
    )
    validFrom: Optional[Union[str, List[str]]] = Field(
        None, description="The date when the item becomes valid"
    )
    validThrough: Optional[Union[str, List[str]]] = Field(
        None,
        description="The date after when the item is not valid For example the end of an offer salary period or a period of opening hours",
    )


# parent dependences
model_dependence("OpeningHoursSpecification", "StructuredValue")


# attribute dependences
model_dependence(
    "OpeningHoursSpecification",
    "DayOfWeek",
)
