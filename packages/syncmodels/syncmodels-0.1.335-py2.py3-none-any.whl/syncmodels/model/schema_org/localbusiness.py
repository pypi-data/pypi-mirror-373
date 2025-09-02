# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Text


# base imports
from .place import Place


@register_model
class LocalBusiness(Place):
    """A particular physical business or branch of an organization Examples of LocalBusiness include a restaurant a particular branch of a restaurant chain a branch of a bank a medical practice a club a bowling alley etc"""

    currenciesAccepted: Optional[Union[str, List[str]]] = Field(
        None,
        description="The currency accepted Use standard formats ISO 4217 currency format e g USD Ticker symbol for cryptocurrencies e g BTC well known names for Local Exchange Trading Systems LETS and other currency types e g Ithaca HOUR",
    )
    openingHours: Optional[Union[str, List[str]]] = Field(
        None,
        description="The general opening hours for a business Opening hours can be specified as a weekly time range starting with days then times per day Multiple days can be listed with commas separating each day Day or time ranges are specified using a hyphen Days are specified using the following two letter combinations Mo Tu We Th Fr Sa Su Times are specified using 24 00 format For example 3pm is specified as 15 00 10am as 10 00 Here is an example time itemprop openingHours datetime Tu Th 16 00 20 00 Tuesdays and Thursdays 4 8pm time If a business is open 7 days a week then it can be specified as time itemprop openingHours datetime Mo Su Monday through Sunday all day time",
    )
    paymentAccepted: Optional[Union[str, List[str]]] = Field(
        None,
        description="Cash Credit Card Cryptocurrency Local Exchange Tradings System etc",
    )
    priceRange: Optional[Union[str, List[str]]] = Field(
        None, description="The price range of the business for example"
    )


# parent dependences
model_dependence("LocalBusiness", "Place")


# attribute dependences
model_dependence(
    "LocalBusiness",
)
