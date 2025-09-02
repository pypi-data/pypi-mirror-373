# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .paymentcard import PaymentCard


@register_model
class CreditCard(PaymentCard):
    """A card payment method of a particular brand or name Used to mark up a particular payment method and or the financial product service that supplies the card account Commonly used values http purl org goodrelations v1 AmericanExpress http purl org goodrelations v1 DinersClub http purl org goodrelations v1 Discover http purl org goodrelations v1 JCB http purl org goodrelations v1 MasterCard http purl org goodrelations v1 VISA"""


# parent dependences
model_dependence("CreditCard", "PaymentCard")


# attribute dependences
model_dependence(
    "CreditCard",
)
