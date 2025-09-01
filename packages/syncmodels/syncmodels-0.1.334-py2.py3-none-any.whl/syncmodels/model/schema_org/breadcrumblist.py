# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .itemlist import ItemList


@register_model
class BreadcrumbList(ItemList):
    """A BreadcrumbList is an ItemList consisting of a chain of linked Web pages typically described using at least their URL and their name and typically ending with the current page The position property is used to reconstruct the order of the items in a BreadcrumbList The convention is that a breadcrumb list has an itemListOrder of ItemListOrderAscending lower values listed first and that the first items in this list correspond to the top or beginning of the breadcrumb trail e g with a site or section homepage The specific values of position are not assigned meaning for a BreadcrumbList but they should be integers e g beginning with 1 for the first item in the list"""


# parent dependences
model_dependence("BreadcrumbList", "ItemList")


# attribute dependences
model_dependence(
    "BreadcrumbList",
)
