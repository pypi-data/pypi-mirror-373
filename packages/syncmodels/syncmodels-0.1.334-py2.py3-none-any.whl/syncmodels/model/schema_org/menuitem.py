# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .intangible import Intangible


@register_model
class MenuItem(Intangible):
    """A food or drink item listed in a menu or menu section"""

    menuAddOn: Optional[
        Union[
            "MenuItem",
            "MenuSection",
            str,
            List["MenuItem"],
            List["MenuSection"],
            List[str],
        ]
    ] = Field(
        None,
        description="Additional menu item s such as a side dish of salad or side order of fries that can be added to this menu item Additionally it can be a menu section containing allowed add on menu items for this menu item",
    )
    nutrition: Optional[
        Union["NutritionInformation", str, List["NutritionInformation"], List[str]]
    ] = Field(None, description="Nutrition information about the recipe or menu item")
    offers: Optional[
        Union["Demand", "Offer", str, List["Demand"], List["Offer"], List[str]]
    ] = Field(
        None,
        description="An offer to provide this item for example an offer to sell a product rent the DVD of a movie perform a service or give away tickets to an event Use businessFunction to indicate the kind of transaction offered i e sell lease etc This property can also be used to describe a Demand While this property is listed as expected on a number of common types it can be used in others In that case using a second type such as Product or a subtype of Product can clarify the nature of the offer Inverse property itemOffered",
    )
    suitableForDiet: Optional[
        Union["RestrictedDiet", str, List["RestrictedDiet"], List[str]]
    ] = Field(
        None,
        description="Indicates a dietary restriction or guideline for which this recipe or menu item is suitable e g diabetic halal etc",
    )


# parent dependences
model_dependence("MenuItem", "Intangible")


# attribute dependences
model_dependence(
    "MenuItem",
    "Demand",
    "MenuSection",
    "NutritionInformation",
    "Offer",
    "RestrictedDiet",
)
