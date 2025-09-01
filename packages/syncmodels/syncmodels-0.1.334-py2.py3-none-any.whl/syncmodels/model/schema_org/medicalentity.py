# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Grant, Text


# base imports
from .thing import Thing


@register_model
class MedicalEntity(Thing):
    """The most generic type of entity related to health and the practice of medicine"""

    code: Optional[Union["MedicalCode", str, List["MedicalCode"], List[str]]] = Field(
        None,
        description="A medical code for the entity taken from a controlled vocabulary or ontology such as ICD 9 DiseasesDB MeSH SNOMED CT RxNorm etc",
    )
    funding: Optional[Union[str, List[str]]] = Field(
        None,
        description="A Grant that directly or indirectly provide funding or sponsorship for this item See also ownershipFundingInfo Inverse property fundedItem",
    )
    guideline: Optional[
        Union["MedicalGuideline", str, List["MedicalGuideline"], List[str]]
    ] = Field(None, description="A medical guideline related to this entity")
    legalStatus: Optional[
        Union[
            "DrugLegalStatus",
            "MedicalEnumeration",
            str,
            List["DrugLegalStatus"],
            List["MedicalEnumeration"],
            List[str],
        ]
    ] = Field(
        None,
        description="The drug or supplement s legal status including any controlled substance schedules that apply",
    )
    medicineSystem: Optional[
        Union["MedicineSystem", str, List["MedicineSystem"], List[str]]
    ] = Field(
        None,
        description="The system of medicine that includes this MedicalEntity for example evidence based homeopathic chiropractic etc",
    )
    recognizingAuthority: Optional[
        Union["Organization", str, List["Organization"], List[str]]
    ] = Field(
        None,
        description="If applicable the organization that officially recognizes this entity as part of its endorsed system of medicine",
    )
    relevantSpecialty: Optional[
        Union["MedicalSpecialty", str, List["MedicalSpecialty"], List[str]]
    ] = Field(
        None,
        description="If applicable a medical specialty in which this entity is relevant",
    )
    study: Optional[Union["MedicalStudy", str, List["MedicalStudy"], List[str]]] = (
        Field(None, description="A medical study or trial related to this entity")
    )


# parent dependences
model_dependence("MedicalEntity", "Thing")


# attribute dependences
model_dependence(
    "MedicalEntity",
    "DrugLegalStatus",
    "MedicalCode",
    "MedicalEnumeration",
    "MedicalGuideline",
    "MedicalSpecialty",
    "MedicalStudy",
    "MedicineSystem",
    "Organization",
)
