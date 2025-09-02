# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .intangible import Intangible


@register_model
class PaymentMethod(Intangible):
    """A payment method is a standardized procedure for transferring the monetary amount for a purchase Payment methods are characterized by the legal and technical structures used and by the organization or group carrying out the transaction The following legacy values should be accepted http purl org goodrelations v1 ByBankTransferInAdvance http purl org goodrelations v1 ByInvoice http purl org goodrelations v1 Cash http purl org goodrelations v1 CheckInAdvance http purl org goodrelations v1 COD http purl org goodrelations v1 DirectDebit http purl org goodrelations v1 GoogleCheckout http purl org goodrelations v1 PayPal http purl org goodrelations v1 PaySwarm Structured values are recommended for newer payment methods"""

    paymentMethodType: Optional[
        Union["PaymentMethodType", str, List["PaymentMethodType"], List[str]]
    ] = Field(None, description="The type of a payment method")


# parent dependences
model_dependence("PaymentMethod", "Intangible")


# attribute dependences
model_dependence(
    "PaymentMethod",
    "PaymentMethodType",
)
