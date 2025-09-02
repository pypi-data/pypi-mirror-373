# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .medicalentity import MedicalEntity


@register_model
class MedicalContraindication(MedicalEntity):
    """A condition or factor that serves as a reason to withhold a certain medical therapy Contraindications can be absolute there are no reasonable circumstances for undertaking a course of action or relative the patient is at higher risk of complications but these risks may be outweighed by other considerations or mitigated by other measures"""


# parent dependences
model_dependence("MedicalContraindication", "MedicalEntity")


# attribute dependences
model_dependence(
    "MedicalContraindication",
)
