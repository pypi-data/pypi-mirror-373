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
class SuperficialAnatomy(MedicalEntity):
    """Anatomical features that can be observed by sight without dissection including the form and proportions of the human body as well as surface landmarks that correspond to deeper subcutaneous structures Superficial anatomy plays an important role in sports medicine phlebotomy and other medical specialties as underlying anatomical structures can be identified through surface palpation For example during back surgery superficial anatomy can be used to palpate and count vertebrae to find the site of incision Or in phlebotomy superficial anatomy can be used to locate an underlying vein for example the median cubital vein can be located by palpating the borders of the cubital fossa such as the epicondyles of the humerus and then looking for the superficial signs of the vein such as size prominence ability to refill after depression and feel of surrounding tissue support As another example in a subluxation dislocation of the glenohumeral joint the bony structure becomes pronounced with the deltoid muscle failing to cover the glenohumeral joint allowing the edges of the scapula to be superficially visible Here the superficial anatomy is the visible edges of the scapula implying the underlying dislocation of the joint the related anatomical structure"""

    associatedPathophysiology: Optional[Union[str, List[str]]] = Field(
        None,
        description="If applicable a description of the pathophysiology associated with the anatomical system including potential abnormal changes in the mechanical physical and biochemical functions of the system",
    )
    relatedAnatomy: Optional[
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
        description="Anatomical systems or structures that relate to the superficial anatomy",
    )
    relatedCondition: Optional[
        Union["MedicalCondition", str, List["MedicalCondition"], List[str]]
    ] = Field(None, description="A medical condition associated with this anatomy")
    relatedTherapy: Optional[
        Union["MedicalTherapy", str, List["MedicalTherapy"], List[str]]
    ] = Field(None, description="A medical therapy related to this anatomy")
    significance: Optional[Union[str, List[str]]] = Field(
        None,
        description="The significance associated with the superficial anatomy as an example how characteristics of the superficial anatomy can suggest underlying medical conditions or courses of treatment",
    )


# parent dependences
model_dependence("SuperficialAnatomy", "MedicalEntity")


# attribute dependences
model_dependence(
    "SuperficialAnatomy",
    "AnatomicalStructure",
    "AnatomicalSystem",
    "MedicalCondition",
    "MedicalTherapy",
)
