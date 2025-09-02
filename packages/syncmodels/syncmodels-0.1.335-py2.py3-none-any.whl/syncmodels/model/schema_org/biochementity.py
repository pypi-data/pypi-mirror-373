# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import URL, Text


# base imports
from .thing import Thing


@register_model
class BioChemEntity(Thing):
    """Any biological chemical or biochemical thing For example a protein a gene a chemical a synthetic chemical"""

    associatedDisease: Optional[Union["MedicalCondition", "PropertyValue", str]] = (
        Field(
            None,
            description="Disease associated to this BioChemEntity Such disease can be a MedicalCondition or a URL If you want to add an evidence supporting the association please use PropertyValue",
        )
    )
    bioChemInteraction: Optional["BioChemEntity"] = Field(
        None, description="A BioChemEntity that is known to interact with this item"
    )
    bioChemSimilarity: Optional["BioChemEntity"] = Field(
        None,
        description="A similar BioChemEntity e g obtained by fingerprint similarity algorithms",
    )
    biologicalRole: Optional["DefinedTerm"] = Field(
        None,
        description="A role played by the BioChemEntity within a biological context",
    )
    funding: Optional["Grant"] = Field(
        None,
        description="A Grant that directly or indirectly provide funding or sponsorship for this item See also ownershipFundingInfo Inverse property fundedItem",
    )
    hasBioChemEntityPart: Optional["BioChemEntity"] = Field(
        None,
        description="Indicates a BioChemEntity that in some sense has this BioChemEntity as a part Inverse property isPartOfBioChemEntity",
    )
    hasMolecularFunction: Optional[Union["DefinedTerm", "PropertyValue", str]] = Field(
        None,
        description="Molecular function performed by this BioChemEntity please use PropertyValue if you want to include any evidence",
    )
    hasRepresentation: Optional[Union["PropertyValue", str]] = Field(
        None,
        description="A common representation such as a protein sequence or chemical structure for this entity For images use schema org image",
    )
    isEncodedByBioChemEntity: Optional["Gene"] = Field(
        None,
        description="Another BioChemEntity encoding by this one Inverse property encodesBioChemEntity",
    )
    isInvolvedInBiologicalProcess: Optional[
        Union["DefinedTerm", "PropertyValue", str]
    ] = Field(
        None,
        description="Biological process this BioChemEntity is involved in please use PropertyValue if you want to include any evidence",
    )
    isLocatedInSubcellularLocation: Optional[
        Union["DefinedTerm", "PropertyValue", str]
    ] = Field(
        None,
        description="Subcellular location where this BioChemEntity is located please use PropertyValue if you want to include any evidence",
    )
    isPartOfBioChemEntity: Optional["BioChemEntity"] = Field(
        None,
        description="Indicates a BioChemEntity that is in some sense a part of this BioChemEntity Inverse property hasBioChemEntityPart",
    )
    taxonomicRange: Optional[Union["DefinedTerm", "Taxon", str]] = Field(
        None,
        description="The taxonomic grouping of the organism that expresses encodes or in some way related to the BioChemEntity",
    )


# parent dependences
model_dependence("BioChemEntity", "Thing")


# attribute dependences
model_dependence(
    "BioChemEntity",
    "DefinedTerm",
    "Gene",
    "Grant",
    "MedicalCondition",
    "PropertyValue",
    "Taxon",
)
