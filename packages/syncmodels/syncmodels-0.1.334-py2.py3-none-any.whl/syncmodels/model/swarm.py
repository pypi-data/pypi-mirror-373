"""
This file supports Swarm Tasks
"""

from datetime import datetime, timedelta

from typing import Any, Union, List, Tuple, Dict, Optional
from typing_extensions import Annotated

from syncmodels.definitions import UID_TYPE
from syncmodels.model import BaseModel, field_validator, Field, Datetime


# ---------------------------------------------------------
# PricemonItem
# ---------------------------------------------------------
# TODO: Inherit from smartmodels.model.app (or similar)
class SwarmTask(BaseModel):
    """A Pricemon Item model"""

    id: UID_TYPE = Field(
        description="ID",
    )
    kind__: str = Field(
        description="Task Kind",
    )
    url: Optional[str] = Field(
        None,
        description="Task URL",
    )
    datetime: Optional[Datetime] = Field(
        None,
        description="Task datetime",
    )
    last: Optional[Datetime] = Field(
        None,
        description="Task datetime",
    )
    bot: Optional[str] = Field(
        None,
        description="Assigned Bot",
    )
    fquid: Optional[UID_TYPE] = Field(
        None,
        description="FQUID",
    )
    payload: Optional[Dict[str, Union[str, int, float]]] = Field(
        None,
        description="Free task payload attribute",
    )
