# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Text


# base imports
from .medicalentity import MedicalEntity


@register_model
class AnatomicalStructure(MedicalEntity):
    """Any part of the human body typically a component of an anatomical system Organs tissues and cells are all anatomical structures"""

    associatedPathophysiology: Optional[Union[str, List[str]]] = Field(
        None,
        description="If applicable a description of the pathophysiology associated with the anatomical system including potential abnormal changes in the mechanical physical and biochemical functions of the system",
    )
    bodyLocation: Optional[Union[str, List[str]]] = Field(
        None, description="Location in the body of the anatomical structure"
    )
    connectedTo: Optional[
        Union["AnatomicalStructure", str, List["AnatomicalStructure"], List[str]]
    ] = Field(
        None,
        description="Other anatomical structures to which this structure is connected",
    )
    diagram: Optional[Union["ImageObject", str, List["ImageObject"], List[str]]] = (
        Field(
            None,
            description="An image containing a diagram that illustrates the structure and or its component substructures and or connections with other structures",
        )
    )
    partOfSystem: Optional[
        Union["AnatomicalSystem", str, List["AnatomicalSystem"], List[str]]
    ] = Field(
        None,
        description="The anatomical or organ system that this structure is part of",
    )
    relatedCondition: Optional[
        Union["MedicalCondition", str, List["MedicalCondition"], List[str]]
    ] = Field(None, description="A medical condition associated with this anatomy")
    relatedTherapy: Optional[
        Union["MedicalTherapy", str, List["MedicalTherapy"], List[str]]
    ] = Field(None, description="A medical therapy related to this anatomy")
    subStructure: Optional[
        Union["AnatomicalStructure", str, List["AnatomicalStructure"], List[str]]
    ] = Field(
        None,
        description="Component sub structure s that comprise this anatomical structure",
    )


# parent dependences
model_dependence("AnatomicalStructure", "MedicalEntity")


# attribute dependences
model_dependence(
    "AnatomicalStructure",
    "AnatomicalSystem",
    "ImageObject",
    "MedicalCondition",
    "MedicalTherapy",
)
