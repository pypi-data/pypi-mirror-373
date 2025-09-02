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
class NutritionInformation(StructuredValue):
    """Nutritional information about the recipe"""

    calories: Optional[Union["Energy", str, List["Energy"], List[str]]] = Field(
        None, description="The number of calories"
    )
    carbohydrateContent: Optional[Union["Mass", str, List["Mass"], List[str]]] = Field(
        None, description="The number of grams of carbohydrates"
    )
    cholesterolContent: Optional[Union["Mass", str, List["Mass"], List[str]]] = Field(
        None, description="The number of milligrams of cholesterol"
    )
    fatContent: Optional[Union["Mass", str, List["Mass"], List[str]]] = Field(
        None, description="The number of grams of fat"
    )
    fiberContent: Optional[Union["Mass", str, List["Mass"], List[str]]] = Field(
        None, description="The number of grams of fiber"
    )
    proteinContent: Optional[Union["Mass", str, List["Mass"], List[str]]] = Field(
        None, description="The number of grams of protein"
    )
    saturatedFatContent: Optional[Union["Mass", str, List["Mass"], List[str]]] = Field(
        None, description="The number of grams of saturated fat"
    )
    servingSize: Optional[Union[str, List[str]]] = Field(
        None, description="The serving size in terms of the number of volume or mass"
    )
    sodiumContent: Optional[Union["Mass", str, List["Mass"], List[str]]] = Field(
        None, description="The number of milligrams of sodium"
    )
    sugarContent: Optional[Union["Mass", str, List["Mass"], List[str]]] = Field(
        None, description="The number of grams of sugar"
    )
    transFatContent: Optional[Union["Mass", str, List["Mass"], List[str]]] = Field(
        None, description="The number of grams of trans fat"
    )
    unsaturatedFatContent: Optional[Union["Mass", str, List["Mass"], List[str]]] = (
        Field(None, description="The number of grams of unsaturated fat")
    )


# parent dependences
model_dependence("NutritionInformation", "StructuredValue")


# attribute dependences
model_dependence(
    "NutritionInformation",
    "Energy",
    "Mass",
)
