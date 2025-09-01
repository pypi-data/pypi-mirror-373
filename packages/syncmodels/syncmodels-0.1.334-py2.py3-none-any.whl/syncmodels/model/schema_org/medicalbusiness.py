# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .localbusiness import LocalBusiness


@register_model
class MedicalBusiness(LocalBusiness):
    """A particular physical or virtual business of an organization for medical purposes Examples of MedicalBusiness include different businesses run by health professionals"""


# parent dependences
model_dependence("MedicalBusiness", "LocalBusiness")


# attribute dependences
model_dependence(
    "MedicalBusiness",
)
