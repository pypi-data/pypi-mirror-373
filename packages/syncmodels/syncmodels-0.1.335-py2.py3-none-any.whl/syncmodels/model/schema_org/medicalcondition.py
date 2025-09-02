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
class MedicalCondition(MedicalEntity):
    """Any condition of the human body that affects the normal functioning of a person whether physically or mentally Includes diseases injuries disabilities disorders syndromes etc"""

    associatedAnatomy: Optional[
        Union[
            "AnatomicalStructure",
            "AnatomicalSystem",
            "SuperficialAnatomy",
            str,
            List["AnatomicalStructure"],
            List["AnatomicalSystem"],
            List["SuperficialAnatomy"],
            List[str],
        ]
    ] = Field(
        None,
        description="The anatomy of the underlying organ system or structures associated with this entity",
    )
    differentialDiagnosis: Optional[
        Union["DDxElement", str, List["DDxElement"], List[str]]
    ] = Field(
        None,
        description="One of a set of differential diagnoses for the condition Specifically a closely related or competing diagnosis typically considered later in the cognitive process whereby this medical condition is distinguished from others most likely responsible for a similar collection of signs and symptoms to reach the most parsimonious diagnosis or diagnoses in a patient",
    )
    drug: Optional[Union["Drug", str, List["Drug"], List[str]]] = Field(
        None, description="Specifying a drug or medicine used in a medication procedure"
    )
    epidemiology: Optional[Union[str, List[str]]] = Field(
        None,
        description="The characteristics of associated patients such as age gender race etc",
    )
    expectedPrognosis: Optional[Union[str, List[str]]] = Field(
        None,
        description="The likely outcome in either the short term or long term of the medical condition",
    )
    naturalProgression: Optional[Union[str, List[str]]] = Field(
        None,
        description="The expected progression of the condition if it is not treated and allowed to progress naturally",
    )
    pathophysiology: Optional[Union[str, List[str]]] = Field(
        None,
        description="Changes in the normal mechanical physical and biochemical functions that are associated with this activity or condition",
    )
    possibleComplication: Optional[Union[str, List[str]]] = Field(
        None,
        description="A possible unexpected and unfavorable evolution of a medical condition Complications may include worsening of the signs or symptoms of the disease extension of the condition to other organ systems etc",
    )
    possibleTreatment: Optional[
        Union["MedicalTherapy", str, List["MedicalTherapy"], List[str]]
    ] = Field(
        None,
        description="A possible treatment to address this condition sign or symptom",
    )
    primaryPrevention: Optional[
        Union["MedicalTherapy", str, List["MedicalTherapy"], List[str]]
    ] = Field(
        None,
        description="A preventative therapy used to prevent an initial occurrence of the medical condition such as vaccination",
    )
    riskFactor: Optional[
        Union["MedicalRiskFactor", str, List["MedicalRiskFactor"], List[str]]
    ] = Field(
        None,
        description="A modifiable or non modifiable factor that increases the risk of a patient contracting this condition e g age coexisting condition",
    )
    secondaryPrevention: Optional[
        Union["MedicalTherapy", str, List["MedicalTherapy"], List[str]]
    ] = Field(
        None,
        description="A preventative therapy used to prevent reoccurrence of the medical condition after an initial episode of the condition",
    )
    signOrSymptom: Optional[
        Union["MedicalSignOrSymptom", str, List["MedicalSignOrSymptom"], List[str]]
    ] = Field(
        None,
        description="A sign or symptom of this condition Signs are objective or physically observable manifestations of the medical condition while symptoms are the subjective experience of the medical condition",
    )
    stage: Optional[
        Union["MedicalConditionStage", str, List["MedicalConditionStage"], List[str]]
    ] = Field(None, description="The stage of the condition if applicable")
    status: Optional[
        Union[
            "EventStatusType",
            "MedicalStudyStatus",
            str,
            List["EventStatusType"],
            List["MedicalStudyStatus"],
            List[str],
        ]
    ] = Field(None, description="The status of the study enumerated")
    typicalTest: Optional[Union["MedicalTest", str, List["MedicalTest"], List[str]]] = (
        Field(
            None, description="A medical test typically performed given this condition"
        )
    )


# parent dependences
model_dependence("MedicalCondition", "MedicalEntity")


# attribute dependences
model_dependence(
    "MedicalCondition",
    "AnatomicalStructure",
    "AnatomicalSystem",
    "DDxElement",
    "Drug",
    "EventStatusType",
    "MedicalConditionStage",
    "MedicalRiskFactor",
    "MedicalSignOrSymptom",
    "MedicalStudyStatus",
    "MedicalTest",
    "MedicalTherapy",
    "SuperficialAnatomy",
)
