# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .creativework import CreativeWork


@register_model
class MenuSection(CreativeWork):
    """A sub grouping of food or drink items in a menu E g courses such as Dinner Breakfast etc specific type of dishes such as Meat Vegan Drinks etc or some other classification made by the menu provider"""

    hasMenuItem: Optional[Union["MenuItem", str, List["MenuItem"], List[str]]] = Field(
        None, description="A food or drink item contained in a menu or menu section"
    )
    hasMenuSection: Optional[
        Union["MenuSection", str, List["MenuSection"], List[str]]
    ] = Field(
        None,
        description="A subgrouping of the menu by dishes course serving time period etc",
    )


# parent dependences
model_dependence("MenuSection", "CreativeWork")


# attribute dependences
model_dependence(
    "MenuSection",
    "MenuItem",
)
