# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Text


# base imports
from .organization import Organization


@register_model
class Corporation(Organization):
    """Organization A business corporation"""

    tickerSymbol: Optional[Union[str, List[str]]] = Field(
        None,
        description="The exchange traded instrument associated with a Corporation object The tickerSymbol is expressed as an exchange and an instrument name separated by a space character For the exchange component of the tickerSymbol attribute we recommend using the controlled vocabulary of Market Identifier Codes MIC specified in ISO 15022",
    )


# parent dependences
model_dependence("Corporation", "Organization")


# attribute dependences
model_dependence(
    "Corporation",
)
