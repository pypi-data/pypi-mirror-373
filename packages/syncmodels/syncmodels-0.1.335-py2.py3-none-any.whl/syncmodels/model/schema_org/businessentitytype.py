# from __future__ import annotations

from pydantic import Field
from typing import Optional, Union, Any

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .enumeration import Enumeration


@register_model
class BusinessEntityType(Enumeration):
    """A business entity type is a conceptual entity representing the legal form the size the main line of business the position in the value chain or any combination thereof of an organization or business person Commonly used values http purl org goodrelations v1 Business http purl org goodrelations v1 Enduser http purl org goodrelations v1 PublicInstitution http purl org goodrelations v1 Reseller"""


# parent dependences
model_dependence("BusinessEntityType", "Enumeration")


# attribute dependences
model_dependence(
    "BusinessEntityType",
)
