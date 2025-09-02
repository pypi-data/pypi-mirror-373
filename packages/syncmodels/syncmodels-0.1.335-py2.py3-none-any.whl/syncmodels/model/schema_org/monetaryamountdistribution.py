# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Text


# base imports
from .quantitativevaluedistribution import QuantitativeValueDistribution


@register_model
class MonetaryAmountDistribution(QuantitativeValueDistribution):
    """A statistical distribution of monetary amounts"""

    currency: Optional[Union[str, List[str]]] = Field(
        None,
        description="The currency in which the monetary amount is expressed Use standard formats ISO 4217 currency format e g USD Ticker symbol for cryptocurrencies e g BTC well known names for Local Exchange Trading Systems LETS and other currency types e g Ithaca HOUR",
    )


# parent dependences
model_dependence("MonetaryAmountDistribution", "QuantitativeValueDistribution")


# attribute dependences
model_dependence(
    "MonetaryAmountDistribution",
)
