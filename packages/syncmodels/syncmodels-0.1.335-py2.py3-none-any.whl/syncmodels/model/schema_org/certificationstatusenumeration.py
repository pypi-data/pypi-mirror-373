# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .enumeration import Enumeration


@register_model
class CertificationStatusEnumeration(Enumeration):
    """Enumerates the different statuses of a Certification Active and Inactive"""


# parent dependences
model_dependence("CertificationStatusEnumeration", "Enumeration")


# attribute dependences
model_dependence(
    "CertificationStatusEnumeration",
)
