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
class AnatomicalSystem(MedicalEntity):
    """An anatomical system is a group of anatomical structures that work together to perform a certain task Anatomical systems such as organ systems are one organizing principle of anatomy and can include circulatory digestive endocrine integumentary immune lymphatic muscular nervous reproductive respiratory skeletal urinary vestibular and other systems"""

    associatedPathophysiology: Optional[Union[str, List[str]]] = Field(
        None,
        description="If applicable a description of the pathophysiology associated with the anatomical system including potential abnormal changes in the mechanical physical and biochemical functions of the system",
    )
    comprisedOf: Optional[
        Union[
            "AnatomicalStructure",
            "AnatomicalSystem",
            str,
            List["AnatomicalStructure"],
            List["AnatomicalSystem"],
            List[str],
        ]
    ] = Field(
        None,
        description="Specifying something physically contained by something else Typically used here for the underlying anatomical structures such as organs that comprise the anatomical system",
    )
    relatedCondition: Optional[
        Union["MedicalCondition", str, List["MedicalCondition"], List[str]]
    ] = Field(None, description="A medical condition associated with this anatomy")
    relatedStructure: Optional[
        Union["AnatomicalStructure", str, List["AnatomicalStructure"], List[str]]
    ] = Field(
        None,
        description="Related anatomical structure s that are not part of the system but relate or connect to it such as vascular bundles associated with an organ system",
    )
    relatedTherapy: Optional[
        Union["MedicalTherapy", str, List["MedicalTherapy"], List[str]]
    ] = Field(None, description="A medical therapy related to this anatomy")


# parent dependences
model_dependence("AnatomicalSystem", "MedicalEntity")


# attribute dependences
model_dependence(
    "AnatomicalSystem",
    "AnatomicalStructure",
    "MedicalCondition",
    "MedicalTherapy",
)
