# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .itemlist import ItemList


@register_model
class OfferCatalog(ItemList):
    """An OfferCatalog is an ItemList that contains related Offers and or further OfferCatalogs that are offeredBy the same provider"""


# parent dependences
model_dependence("OfferCatalog", "ItemList")


# attribute dependences
model_dependence(
    "OfferCatalog",
)
