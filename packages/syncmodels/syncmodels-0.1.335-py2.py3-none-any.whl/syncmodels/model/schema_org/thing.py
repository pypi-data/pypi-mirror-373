# from __future__ import annotations

from pydantic import BaseModel, Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Text, URL, TextObject, PropertyValue, Event


@register_model
class Thing(BaseModel):
    """The most generic type of item"""

    additionalType: Optional[Union[str, List[str]]] = Field(
        None,
        description="An additional type for the item typically used for adding more specific types from external vocabularies in microdata syntax This is a relationship between something and a class that the thing is in Typically the value is a URI identified RDF class and in this case corresponds to the use of rdf type in RDF Text values can be used sparingly for cases where useful information can be added without their being an appropriate schema to reference In the case of text values the class label should follow the schema org style guide",
    )
    alternateName: Optional[Union[str, List[str]]] = Field(
        None, description="An alias for the item"
    )
    description: Optional[Union[str, List[str]]] = Field(
        None, description="A description of the item"
    )
    disambiguatingDescription: Optional[Union[str, List[str]]] = Field(
        None,
        description="A sub property of description A short description of the item used to disambiguate from other similar items Information from other properties in particular name may be necessary for the description to be useful for disambiguation",
    )
    identifier: Optional[Union[str, List[str]]] = Field(
        None,
        description="The identifier property represents any kind of identifier for any kind of Thing such as ISBNs GTIN codes UUIDs etc Schema org provides dedicated properties for representing many of these either as textual strings or as URL URI links See background notes for more details",
    )
    image: Optional[Union["ImageObject", str, List["ImageObject"], List[str]]] = Field(
        None,
        description="An image of the item This can be a URL or a fully described ImageObject",
    )
    mainEntityOfPage: Optional[
        Union["CreativeWork", str, List["CreativeWork"], List[str]]
    ] = Field(
        None,
        description="Indicates a page or other CreativeWork for which this thing is the main entity being described See background notes for details Inverse property mainEntity",
    )
    name: Optional[Union[str, List[str]]] = Field(
        None, description="The name of the item"
    )
    potentialAction: Optional[Union["Action", str, List["Action"], List[str]]] = Field(
        None,
        description="Indicates a potential Action which describes an idealized action in which this thing would play an object role",
    )
    sameAs: Optional[Union[str, List[str]]] = Field(
        None,
        description="URL of a reference Web page that unambiguously indicates the item s identity E g the URL of the item s Wikipedia page Wikidata entry or official website",
    )
    subjectOf: Optional[Union["CreativeWork", str, List["CreativeWork"], List[str]]] = (
        Field(
            None,
            description="A CreativeWork or Event about this Thing Inverse property about",
        )
    )
    url: Optional[Union[str, List[str]]] = Field(None, description="URL of the item")
    id: Optional[Union[str, List[str]]] = Field(
        None, description="the id of the object"
    )


# parent dependences


# attribute dependences
model_dependence(
    "Thing",
    "Action",
    "CreativeWork",
    "ImageObject",
    "str",
)
