# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Number, Text, URL


# base imports
from .service import Service


@register_model
class FinancialProduct(Service):
    """A product provided to consumers and businesses by financial institutions such as banks insurance companies brokerage firms consumer finance companies and investment companies which comprise the financial services industry"""

    annualPercentageRate: Optional[
        Union[
            "QuantitativeValue",
            float,
            str,
            List["QuantitativeValue"],
            List[float],
            List[str],
        ]
    ] = Field(
        None,
        description="The annual rate that is charged for borrowing or made by investing expressed as a single percentage number that represents the actual yearly cost of funds over the term of a loan This includes any fees or additional costs associated with the transaction",
    )
    feesAndCommissionsSpecification: Optional[Union[str, List[str]]] = Field(
        None,
        description="Description of fees commissions and other terms applied either to a class of financial product or by a financial service organization",
    )
    interestRate: Optional[
        Union[
            "QuantitativeValue",
            float,
            str,
            List["QuantitativeValue"],
            List[float],
            List[str],
        ]
    ] = Field(
        None,
        description="The interest rate charged or paid applicable to the financial product Note This is different from the calculated annualPercentageRate",
    )


# parent dependences
model_dependence("FinancialProduct", "Service")


# attribute dependences
model_dependence(
    "FinancialProduct",
    "QuantitativeValue",
)
