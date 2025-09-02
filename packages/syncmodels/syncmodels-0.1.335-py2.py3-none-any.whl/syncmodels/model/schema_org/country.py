# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .administrativearea import AdministrativeArea


@register_model
class Country(AdministrativeArea):
    """A country"""


# parent dependences
model_dependence("Country", "AdministrativeArea")


# attribute dependences
model_dependence(
    "Country",
)
