# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Text


# base imports
from .dataset import Dataset


@register_model
class DataFeed(Dataset):
    """A single feed providing structured information about one or more entities or topics"""

    dataFeedElement: Optional[
        Union[
            "DataFeedItem", "Thing", str, List["DataFeedItem"], List["Thing"], List[str]
        ]
    ] = Field(
        None, description="An item within a data feed Data feeds may have many elements"
    )


# parent dependences
model_dependence("DataFeed", "Dataset")


# attribute dependences
model_dependence(
    "DataFeed",
    "DataFeedItem",
    "Thing",
)
