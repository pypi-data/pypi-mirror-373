# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Text


# base imports
from .biochementity import BioChemEntity


@register_model
class Gene(BioChemEntity):
    """A discrete unit of inheritance which affects one or more biological traits Source https en wikipedia org wiki Gene Examples include FOXP2 Forkhead box protein P2 SCARNA21 small Cajal body specific RNA 21 A agouti genotype"""

    alternativeOf: Optional["Gene"] = Field(
        None, description="Another gene which is a variation of this one"
    )
    encodesBioChemEntity: Optional["BioChemEntity"] = Field(
        None,
        description="Another BioChemEntity encoded by this one Inverse property isEncodedByBioChemEntity",
    )
    expressedIn: Optional[
        Union["AnatomicalStructure", "AnatomicalSystem", "BioChemEntity", "DefinedTerm"]
    ] = Field(
        None,
        description="Tissue organ biological sample etc in which activity of this gene has been observed experimentally For example brain digestive system",
    )
    hasBioPolymerSequence: Optional[str] = Field(
        None,
        description="A symbolic representation of a BioChemEntity For example a nucleotide sequence of a Gene or an amino acid sequence of a Protein",
    )


# parent dependences
model_dependence("Gene", "BioChemEntity")


# attribute dependences
model_dependence(
    "Gene",
    "AnatomicalStructure",
    "AnatomicalSystem",
    "BioChemEntity",
    "DefinedTerm",
)
