# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .doseschedule import DoseSchedule


@register_model
class MaximumDoseSchedule(DoseSchedule):
    """The maximum dosing schedule considered safe for a drug or supplement as recommended by an authority or by the drug supplement s manufacturer Capture the recommending authority in the recognizingAuthority property of MedicalEntity"""


# parent dependences
model_dependence("MaximumDoseSchedule", "DoseSchedule")


# attribute dependences
model_dependence(
    "MaximumDoseSchedule",
)
