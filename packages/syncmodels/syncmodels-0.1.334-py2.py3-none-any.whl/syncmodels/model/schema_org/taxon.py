# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Text, URL


# base imports
from .thing import Thing


@register_model
class Taxon(Thing):
    """A set of organisms asserted to represent a natural cohesive biological unit"""

    childTaxon: Optional[Union["Taxon", str]] = Field(
        None,
        description="Closest child taxa of the taxon in question Inverse property parentTaxon",
    )
    hasDefinedTerm: Optional["DefinedTerm"] = Field(
        None, description="A Defined Term contained in this term set"
    )
    parentTaxon: Optional[Union["Taxon", str]] = Field(
        None,
        description="Closest parent taxon of the taxon in question Inverse property childTaxon",
    )
    taxonRank: Optional[Union["PropertyValue", str]] = Field(
        None,
        description="The taxonomic rank of this taxon given preferably as a URI from a controlled vocabulary â typically the ranks from TDWG TaxonRank ontology or equivalent Wikidata URIs",
    )


# parent dependences
model_dependence("Taxon", "Thing")


# attribute dependences
model_dependence(
    "Taxon",
    "DefinedTerm",
    "PropertyValue",
)
