# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .structuredvalue import StructuredValue


@register_model
class WarrantyPromise(StructuredValue):
    """A structured value representing the duration and scope of services that will be provided to a customer free of charge in case of a defect or malfunction of a product"""

    durationOfWarranty: Optional[
        Union["QuantitativeValue", str, List["QuantitativeValue"], List[str]]
    ] = Field(
        None,
        description="The duration of the warranty promise Common unitCode values are ANN for year MON for months or DAY for days",
    )
    warrantyScope: Optional[
        Union["WarrantyScope", str, List["WarrantyScope"], List[str]]
    ] = Field(None, description="The scope of the warranty promise")


# parent dependences
model_dependence("WarrantyPromise", "StructuredValue")


# attribute dependences
model_dependence(
    "WarrantyPromise",
    "QuantitativeValue",
    "WarrantyScope",
)
