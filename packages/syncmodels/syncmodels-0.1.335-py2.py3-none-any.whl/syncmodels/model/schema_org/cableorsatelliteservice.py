# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .service import Service


@register_model
class CableOrSatelliteService(Service):
    """A service which provides access to media programming like TV or radio Access may be via cable or satellite"""


# parent dependences
model_dependence("CableOrSatelliteService", "Service")


# attribute dependences
model_dependence(
    "CableOrSatelliteService",
)
