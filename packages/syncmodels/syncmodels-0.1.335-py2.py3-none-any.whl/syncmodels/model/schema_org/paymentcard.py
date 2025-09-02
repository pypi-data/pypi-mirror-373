# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Boolean, Number


# base imports
from .paymentmethod import PaymentMethod


@register_model
class PaymentCard(PaymentMethod):
    """A payment method using a credit debit store or other card to associate the payment with an account"""

    cashBack: Optional[Union["bool", float, List["bool"], List[float]]] = Field(
        None,
        description="A cardholder benefit that pays the cardholder a small percentage of their net expenditures",
    )
    contactlessPayment: Optional[Union["bool", List["bool"]]] = Field(
        None,
        description="A secure method for consumers to purchase products or services via debit credit or smartcards by using RFID or NFC technology",
    )
    floorLimit: Optional[
        Union["MonetaryAmount", str, List["MonetaryAmount"], List[str]]
    ] = Field(
        None,
        description="A floor limit is the amount of money above which credit card transactions must be authorized",
    )
    monthlyMinimumRepaymentAmount: Optional[
        Union[
            "MonetaryAmount", float, str, List["MonetaryAmount"], List[float], List[str]
        ]
    ] = Field(
        None,
        description="The minimum payment is the lowest amount of money that one is required to pay on a credit card statement each month",
    )


# parent dependences
model_dependence("PaymentCard", "PaymentMethod")


# attribute dependences
model_dependence(
    "PaymentCard",
    "MonetaryAmount",
)
