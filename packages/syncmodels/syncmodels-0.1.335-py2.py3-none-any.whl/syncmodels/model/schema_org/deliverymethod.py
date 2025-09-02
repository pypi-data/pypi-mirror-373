# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .enumeration import Enumeration


@register_model
class DeliveryMethod(Enumeration):
    """A delivery method is a standardized procedure for transferring the product or service to the destination of fulfillment chosen by the customer Delivery methods are characterized by the means of transportation used and by the organization or group that is the contracting party for the sending organization or person Commonly used values http purl org goodrelations v1 DeliveryModeDirectDownload http purl org goodrelations v1 DeliveryModeFreight http purl org goodrelations v1 DeliveryModeMail http purl org goodrelations v1 DeliveryModeOwnFleet http purl org goodrelations v1 DeliveryModePickUp http purl org goodrelations v1 DHL http purl org goodrelations v1 FederalExpress http purl org goodrelations v1 UPS"""


# parent dependences
model_dependence("DeliveryMethod", "Enumeration")


# attribute dependences
model_dependence(
    "DeliveryMethod",
)
