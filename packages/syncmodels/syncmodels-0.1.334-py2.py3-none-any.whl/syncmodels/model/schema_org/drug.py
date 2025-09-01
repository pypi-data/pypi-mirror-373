# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Text, Boolean, URL


# base imports
from .substance import Substance


@register_model
class Drug(Substance):
    """A chemical or biologic substance used as a medical therapy that has a physiological effect on an organism Here the term drug is used interchangeably with the term medicine although clinical knowledge makes a clear difference between them"""

    activeIngredient: Optional[Union[str, List[str]]] = Field(
        None,
        description="An active ingredient typically chemical compounds and or biologic substances",
    )
    administrationRoute: Optional[Union[str, List[str]]] = Field(
        None, description="A route by which this drug may be administered e g oral"
    )
    alcoholWarning: Optional[Union[str, List[str]]] = Field(
        None,
        description="Any precaution guidance contraindication etc related to consumption of alcohol while taking this drug",
    )
    availableStrength: Optional[
        Union["DrugStrength", str, List["DrugStrength"], List[str]]
    ] = Field(None, description="An available dosage strength for the drug")
    breastfeedingWarning: Optional[Union[str, List[str]]] = Field(
        None,
        description="Any precaution guidance contraindication etc related to this drug s use by breastfeeding mothers",
    )
    clinicalPharmacology: Optional[Union[str, List[str]]] = Field(
        None,
        description="Description of the absorption and elimination of drugs including their concentration pharmacokinetics pK and biological effects pharmacodynamics pD Supersedes clincalPharmacology",
    )
    dosageForm: Optional[Union[str, List[str]]] = Field(
        None,
        description="A dosage form in which this drug supplement is available e g tablet suspension injection",
    )
    doseSchedule: Optional[
        Union["DoseSchedule", str, List["DoseSchedule"], List[str]]
    ] = Field(
        None,
        description="A dosing schedule for the drug for a given population either observed recommended or maximum dose based on the type used",
    )
    drugClass: Optional[Union["DrugClass", str, List["DrugClass"], List[str]]] = Field(
        None, description="The class of drug this belongs to e g statins"
    )
    drugUnit: Optional[Union[str, List[str]]] = Field(
        None, description="The unit in which the drug is measured e g 5 mg tablet"
    )
    foodWarning: Optional[Union[str, List[str]]] = Field(
        None,
        description="Any precaution guidance contraindication etc related to consumption of specific foods while taking this drug",
    )
    includedInHealthInsurancePlan: Optional[
        Union["HealthInsurancePlan", str, List["HealthInsurancePlan"], List[str]]
    ] = Field(None, description="The insurance plans that cover this drug")
    interactingDrug: Optional[Union["Drug", str, List["Drug"], List[str]]] = Field(
        None,
        description="Another drug that is known to interact with this drug in a way that impacts the effect of this drug or causes a risk to the patient Note disease interactions are typically captured as contraindications",
    )
    isAvailableGenerically: Optional[Union["bool", List["bool"]]] = Field(
        None,
        description="True if the drug is available in a generic form regardless of name",
    )
    isProprietary: Optional[Union["bool", List["bool"]]] = Field(
        None,
        description="True if this item s name is a proprietary brand name vs generic name",
    )
    labelDetails: Optional[Union[str, List[str]]] = Field(
        None, description="Link to the drug s label details"
    )
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
    maximumIntake: Optional[
        Union["MaximumDoseSchedule", str, List["MaximumDoseSchedule"], List[str]]
    ] = Field(
        None,
        description="Recommended intake of this supplement for a given population as defined by a specific recommending authority",
    )
    mechanismOfAction: Optional[Union[str, List[str]]] = Field(
        None,
        description="The specific biochemical interaction through which this drug or supplement produces its pharmacological effect",
    )
    nonProprietaryName: Optional[Union[str, List[str]]] = Field(
        None, description="The generic name of this drug or supplement"
    )
    overdosage: Optional[Union[str, List[str]]] = Field(
        None,
        description="Any information related to overdose on a drug including signs or symptoms treatments contact information for emergency response",
    )
    pregnancyCategory: Optional[
        Union["DrugPregnancyCategory", str, List["DrugPregnancyCategory"], List[str]]
    ] = Field(None, description="Pregnancy category of this drug")
    pregnancyWarning: Optional[Union[str, List[str]]] = Field(
        None,
        description="Any precaution guidance contraindication etc related to this drug s use during pregnancy",
    )
    prescribingInfo: Optional[Union[str, List[str]]] = Field(
        None, description="Link to prescribing information for the drug"
    )
    prescriptionStatus: Optional[
        Union["DrugPrescriptionStatus", str, List["DrugPrescriptionStatus"], List[str]]
    ] = Field(
        None,
        description="Indicates the status of drug prescription e g local catalogs classifications or whether the drug is available by prescription or over the counter etc",
    )
    proprietaryName: Optional[Union[str, List[str]]] = Field(
        None,
        description="Proprietary name given to the diet plan typically by its originator or creator",
    )
    relatedDrug: Optional[Union["Drug", str, List["Drug"], List[str]]] = Field(
        None,
        description="Any other drug related to this one for example commonly prescribed alternatives",
    )
    rxcui: Optional[Union[str, List[str]]] = Field(
        None, description="The RxCUI drug identifier from RXNORM"
    )
    warning: Optional[Union[str, List[str]]] = Field(
        None, description="Any FDA or other warnings about the drug text or URL"
    )


# parent dependences
model_dependence("Drug", "Substance")


# attribute dependences
model_dependence(
    "Drug",
    "DoseSchedule",
    "DrugClass",
    "DrugLegalStatus",
    "DrugPregnancyCategory",
    "DrugPrescriptionStatus",
    "DrugStrength",
    "HealthInsurancePlan",
    "MaximumDoseSchedule",
    "MedicalEnumeration",
)
