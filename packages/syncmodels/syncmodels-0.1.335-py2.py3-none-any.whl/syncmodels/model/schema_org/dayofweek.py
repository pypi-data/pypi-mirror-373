# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .enumeration import Enumeration


@register_model
class DayOfWeek(Enumeration):
    """The day of the week e g used to specify to which day the opening hours of an OpeningHoursSpecification refer Originally URLs from GoodRelations were used for Monday Tuesday Wednesday Thursday Friday Saturday Sunday plus a special entry for PublicHolidays these have now been integrated directly into schema org"""


# parent dependences
model_dependence("DayOfWeek", "Enumeration")


# attribute dependences
model_dependence(
    "DayOfWeek",
)
