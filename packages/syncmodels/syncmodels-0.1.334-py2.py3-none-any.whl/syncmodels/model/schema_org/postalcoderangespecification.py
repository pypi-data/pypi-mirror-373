# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Text


# base imports
from .structuredvalue import StructuredValue


@register_model
class PostalCodeRangeSpecification(StructuredValue):
    """Indicates a range of postal codes usually defined as the set of valid codes between postalCodeBegin and postalCodeEnd inclusively"""

    postalCodeBegin: Optional[Union[str, List[str]]] = Field(
        None, description="First postal code in a range included"
    )
    postalCodeEnd: Optional[Union[str, List[str]]] = Field(
        None,
        description="Last postal code in the range included Needs to be after postalCodeBegin",
    )


# parent dependences
model_dependence("PostalCodeRangeSpecification", "StructuredValue")


# attribute dependences
model_dependence(
    "PostalCodeRangeSpecification",
)
