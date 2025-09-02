# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .enumeration import Enumeration


@register_model
class PaymentMethodType(Enumeration):
    """The type of payment method only for generic payment types specific forms of payments like card payment should be expressed using subclasses of PaymentMethod"""


# parent dependences
model_dependence("PaymentMethodType", "Enumeration")


# attribute dependences
model_dependence(
    "PaymentMethodType",
)
