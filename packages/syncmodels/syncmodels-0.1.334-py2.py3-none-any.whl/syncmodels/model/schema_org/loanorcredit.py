# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Number, Text, URL, Boolean


# base imports
from .financialproduct import FinancialProduct


@register_model
class LoanOrCredit(FinancialProduct):
    """A financial product for the loaning of an amount of money or line of credit under agreed terms and charges"""

    amount: Optional[
        Union[
            "MonetaryAmount", float, str, List["MonetaryAmount"], List[float], List[str]
        ]
    ] = Field(None, description="The amount of money")
    currency: Optional[Union[str, List[str]]] = Field(
        None,
        description="The currency in which the monetary amount is expressed Use standard formats ISO 4217 currency format e g USD Ticker symbol for cryptocurrencies e g BTC well known names for Local Exchange Trading Systems LETS and other currency types e g Ithaca HOUR",
    )
    gracePeriod: Optional[Union["Duration", str, List["Duration"], List[str]]] = Field(
        None,
        description="The period of time after any due date that the borrower has to fulfil its obligations before a default failure to pay is deemed to have occurred",
    )
    loanRepaymentForm: Optional[
        Union["RepaymentSpecification", str, List["RepaymentSpecification"], List[str]]
    ] = Field(
        None,
        description="A form of paying back money previously borrowed from a lender Repayment usually takes the form of periodic payments that normally include part principal plus interest in each payment",
    )
    loanTerm: Optional[
        Union["QuantitativeValue", str, List["QuantitativeValue"], List[str]]
    ] = Field(None, description="The duration of the loan or credit agreement")
    loanType: Optional[Union[str, List[str]]] = Field(
        None, description="The type of a loan or credit"
    )
    recourseLoan: Optional[Union["bool", List["bool"]]] = Field(
        None,
        description="The only way you get the money back in the event of default is the security Recourse is where you still have the opportunity to go back to the borrower for the rest of the money",
    )
    renegotiableLoan: Optional[Union["bool", List["bool"]]] = Field(
        None,
        description="Whether the terms for payment of interest can be renegotiated during the life of the loan",
    )
    requiredCollateral: Optional[Union["Thing", str, List["Thing"], List[str]]] = Field(
        None,
        description="Assets required to secure loan or credit repayments It may take form of third party pledge goods financial instruments cash securities etc",
    )


# parent dependences
model_dependence("LoanOrCredit", "FinancialProduct")


# attribute dependences
model_dependence(
    "LoanOrCredit",
    "Duration",
    "MonetaryAmount",
    "QuantitativeValue",
    "RepaymentSpecification",
    "Thing",
)
