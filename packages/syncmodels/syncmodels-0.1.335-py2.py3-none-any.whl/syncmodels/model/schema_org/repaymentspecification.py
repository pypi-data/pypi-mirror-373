# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Number


# base imports
from .structuredvalue import StructuredValue


@register_model
class RepaymentSpecification(StructuredValue):
    """A structured value representing repayment"""

    downPayment: Optional[
        Union[
            "MonetaryAmount", float, str, List["MonetaryAmount"], List[float], List[str]
        ]
    ] = Field(
        None,
        description="a type of payment made in cash during the onset of the purchase of an expensive good service The payment typically represents only a percentage of the full purchase price",
    )
    earlyPrepaymentPenalty: Optional[
        Union["MonetaryAmount", str, List["MonetaryAmount"], List[str]]
    ] = Field(
        None,
        description="The amount to be paid as a penalty in the event of early payment of the loan",
    )
    loanPaymentAmount: Optional[
        Union["MonetaryAmount", str, List["MonetaryAmount"], List[str]]
    ] = Field(None, description="The amount of money to pay in a single payment")
    loanPaymentFrequency: Optional[Union[float, List[float]]] = Field(
        None,
        description="Frequency of payments due i e number of months between payments This is defined as a frequency i e the reciprocal of a period of time",
    )
    numberOfLoanPayments: Optional[Union[float, List[float]]] = Field(
        None,
        description="The number of payments contractually required at origination to repay the loan For monthly paying loans this is the number of months from the contractual first payment date to the maturity date",
    )


# parent dependences
model_dependence("RepaymentSpecification", "StructuredValue")


# attribute dependences
model_dependence(
    "RepaymentSpecification",
    "MonetaryAmount",
)
