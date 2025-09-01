# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .medicalintangible import MedicalIntangible


@register_model
class DDxElement(MedicalIntangible):
    """An alternative closely related condition typically considered later in the differential diagnosis process along with the signs that are used to distinguish it"""

    diagnosis: Optional[
        Union["MedicalCondition", str, List["MedicalCondition"], List[str]]
    ] = Field(
        None,
        description="One or more alternative conditions considered in the differential diagnosis process as output of a diagnosis process",
    )
    distinguishingSign: Optional[
        Union["MedicalSignOrSymptom", str, List["MedicalSignOrSymptom"], List[str]]
    ] = Field(
        None,
        description="One of a set of signs and symptoms that can be used to distinguish this diagnosis from others in the differential diagnosis",
    )


# parent dependences
model_dependence("DDxElement", "MedicalIntangible")


# attribute dependences
model_dependence(
    "DDxElement",
    "MedicalCondition",
    "MedicalSignOrSymptom",
)
