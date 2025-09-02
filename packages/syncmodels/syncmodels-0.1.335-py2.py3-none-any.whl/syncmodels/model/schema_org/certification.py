# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Date, DateTime, DefinedTerm, Text, URL


# base imports
from .creativework import CreativeWork


@register_model
class Certification(CreativeWork):
    """A Certification is an official and authoritative statement about a subject for example a product service person or organization A certification is typically issued by an indendent certification body for example a professional organization or government It formally attests certain characteristics about the subject for example Organizations can be ISO certified Food products can be certified Organic or Vegan a Person can be a certified professional a Place can be certified for food processing There are certifications for many domains regulatory organizational recycling food efficiency educational ecological etc A certification is a form of credential as are accreditations and licenses Mapped from the gs1 CertificationDetails class in the GS1 Web Vocabulary"""

    about: Optional[Union["Thing", str, List["Thing"], List[str]]] = Field(
        None, description="The subject matter of the content Inverse property subjectOf"
    )
    auditDate: Optional[Union[str, List[str]]] = Field(
        None,
        description="Date when a certification was last audited See also gs1 certificationAuditDate",
    )
    certificationIdentification: Optional[Union[str, List[str]]] = Field(
        None,
        description="Identifier of a certification instance as registered with an independent certification body Typically this identifier can be used to consult and verify the certification instance See also gs1 certificationIdentification",
    )
    certificationRating: Optional[Union["Rating", str, List["Rating"], List[str]]] = (
        Field(
            None,
            description="Rating of a certification instance as defined by an independent certification body Typically this rating can be used to rate the level to which the requirements of the certification instance are fulfilled See also gs1 certificationValue",
        )
    )
    certificationStatus: Optional[
        Union[
            "CertificationStatusEnumeration",
            str,
            List["CertificationStatusEnumeration"],
            List[str],
        ]
    ] = Field(
        None,
        description="Indicates the current status of a certification active or inactive See also gs1 certificationStatus",
    )
    datePublished: Optional[Union[str, List[str]]] = Field(
        None,
        description="Date of first publication or broadcast For example the date a CreativeWork was broadcast or a Certification was issued",
    )
    expires: Optional[Union[str, List[str]]] = Field(
        None,
        description="Date the content expires and is no longer useful or available For example a VideoObject or NewsArticle whose availability or relevance is time limited a ClaimReview fact check whose publisher wants to indicate that it may no longer be relevant or helpful to highlight after some date or a Certification the validity has expired",
    )
    hasMeasurement: Optional[
        Union["QuantitativeValue", str, List["QuantitativeValue"], List[str]]
    ] = Field(
        None,
        description="A measurement of an item For example the inseam of pants the wheel size of a bicycle the gauge of a screw or the carbon footprint measured for certification by an authority Usually an exact measurement but can also be a range of measurements for adjustable products for example belts and ski bindings",
    )
    issuedBy: Optional[Union["Organization", str, List["Organization"], List[str]]] = (
        Field(
            None,
            description="The organization issuing the item for example a Permit Ticket or Certification",
        )
    )
    logo: Optional[Union["ImageObject", str, List["ImageObject"], List[str]]] = Field(
        None, description="An associated logo"
    )
    validFrom: Optional[Union[str, List[str]]] = Field(
        None, description="The date when the item becomes valid"
    )
    validIn: Optional[
        Union["AdministrativeArea", str, List["AdministrativeArea"], List[str]]
    ] = Field(
        None,
        description="The geographic area where the item is valid Applies for example to a Permit a Certification or an EducationalOccupationalCredential",
    )


# parent dependences
model_dependence("Certification", "CreativeWork")


# attribute dependences
model_dependence(
    "Certification",
    "AdministrativeArea",
    "CertificationStatusEnumeration",
    "ImageObject",
    "Organization",
    "QuantitativeValue",
    "Rating",
    "Thing",
)
