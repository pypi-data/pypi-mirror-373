# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import (
    Text,
    InteractionCounter,
    Date,
    URL,
    Grant,
    GenderType,
    DefinedTerm,
    Event,
)


# base imports
from .thing import Thing


@register_model
class Person(Thing):
    """A person alive dead undead or fictional"""

    additionalName: Optional[Union[str, List[str]]] = Field(
        None,
        description="An additional name for a Person can be used for a middle name",
    )
    address: Optional[Union["PostalAddress", str, List["PostalAddress"], List[str]]] = (
        Field(None, description="Physical address of the item")
    )
    affiliation: Optional[
        Union["Organization", str, List["Organization"], List[str]]
    ] = Field(
        None,
        description="An organization that this person is affiliated with For example a school university a club or a team",
    )
    agentInteractionStatistic: Optional[Union[str, List[str]]] = Field(
        None,
        description="The number of completed interactions for this entity in a particular role the agent in a particular action indicated in the statistic and in a particular context i e interactionService",
    )
    alumniOf: Optional[
        Union[
            "EducationalOrganization",
            "Organization",
            str,
            List["EducationalOrganization"],
            List["Organization"],
            List[str],
        ]
    ] = Field(
        None,
        description="An organization that the person is an alumni of Inverse property alumni",
    )
    award: Optional[Union[str, List[str]]] = Field(
        None, description="An award won by or for this item Supersedes awards"
    )
    birthDate: Optional[Union[str, List[str]]] = Field(
        None, description="Date of birth"
    )
    birthPlace: Optional[Union["Place", str, List["Place"], List[str]]] = Field(
        None, description="The place where the person was born"
    )
    brand: Optional[
        Union[
            "Brand", "Organization", str, List["Brand"], List["Organization"], List[str]
        ]
    ] = Field(
        None,
        description="The brand s associated with a product or service or the brand s maintained by an organization or business person",
    )
    callSign: Optional[Union[str, List[str]]] = Field(
        None,
        description="A callsign as used in broadcasting and radio communications to identify people radio and TV stations or vehicles",
    )
    children: Optional[Union["Person", str, List["Person"], List[str]]] = Field(
        None, description="A child of the person"
    )
    colleague: Optional[Union["Person", str, List["Person"], List[str]]] = Field(
        None, description="A colleague of the person Supersedes colleagues"
    )
    contactPoint: Optional[
        Union["ContactPoint", str, List["ContactPoint"], List[str]]
    ] = Field(
        None,
        description="A contact point for a person or organization Supersedes contactPoints",
    )
    deathDate: Optional[Union[str, List[str]]] = Field(
        None, description="Date of death"
    )
    deathPlace: Optional[Union["Place", str, List["Place"], List[str]]] = Field(
        None, description="The place where the person died"
    )
    duns: Optional[Union[str, List[str]]] = Field(
        None,
        description="The Dun Bradstreet DUNS number for identifying an organization or business person",
    )
    email: Optional[Union[str, List[str]]] = Field(None, description="Email address")
    familyName: Optional[Union[str, List[str]]] = Field(
        None, description="Family name In the U S the last name of a Person"
    )
    faxNumber: Optional[Union[int, str, List[int], List[str]]] = Field(
        None, description="The fax number"
    )
    follows: Optional[Union["Person", str, List["Person"], List[str]]] = Field(
        None, description="The most generic uni directional social relation"
    )
    funder: Optional[
        Union[
            "Organization",
            "Person",
            str,
            List["Organization"],
            List["Person"],
            List[str],
        ]
    ] = Field(
        None,
        description="A person or organization that supports sponsors something through some kind of financial contribution",
    )
    funding: Optional[Union[str, List[str]]] = Field(
        None,
        description="A Grant that directly or indirectly provide funding or sponsorship for this item See also ownershipFundingInfo Inverse property fundedItem",
    )
    gender: Optional[Union[str, List[str]]] = Field(
        None,
        description="Gender of something typically a Person but possibly also fictional characters animals etc While https schema org Male and https schema org Female may be used text strings are also acceptable for people who do not identify as a binary gender The gender property can also be used in an extended sense to cover e g the gender of sports teams As with the gender of individuals we do not try to enumerate all possibilities A mixed gender SportsTeam can be indicated with a text value of Mixed",
    )
    givenName: Optional[Union[str, List[str]]] = Field(
        None, description="Given name In the U S the first name of a Person"
    )
    globalLocationNumber: Optional[Union[int, str, List[int], List[str]]] = Field(
        None,
        description="The Global Location Number GLN sometimes also referred to as International Location Number or ILN of the respective organization person or place The GLN is a 13 digit number used to identify parties and physical locations",
    )
    hasCertification: Optional[
        Union["Certification", str, List["Certification"], List[str]]
    ] = Field(
        None,
        description="Certification information about a product organization service place or person",
    )
    hasCredential: Optional[
        Union[
            "EducationalOccupationalCredential",
            str,
            List["EducationalOccupationalCredential"],
            List[str],
        ]
    ] = Field(None, description="A credential awarded to the Person or Organization")
    hasOccupation: Optional[Union["Occupation", str, List["Occupation"], List[str]]] = (
        Field(
            None,
            description="The Person s occupation For past professions use Role for expressing dates",
        )
    )
    hasOfferCatalog: Optional[
        Union["OfferCatalog", str, List["OfferCatalog"], List[str]]
    ] = Field(
        None,
        description="Indicates an OfferCatalog listing for this Organization Person or Service",
    )
    hasPOS: Optional[Union["Place", str, List["Place"], List[str]]] = Field(
        None, description="Points of Sales operated by the organization or person"
    )
    height: Optional[
        Union[
            "Distance",
            "QuantitativeValue",
            int,
            str,
            List["Distance"],
            List["QuantitativeValue"],
            List[int],
            List[str],
        ]
    ] = Field(None, description="The height of the item")
    homeLocation: Optional[
        Union[
            "ContactPoint", "Place", str, List["ContactPoint"], List["Place"], List[str]
        ]
    ] = Field(None, description="A contact location for a person s residence")
    honorificPrefix: Optional[Union[str, List[str]]] = Field(
        None,
        description="An honorific prefix preceding a Person s name such as Dr Mrs Mr",
    )
    honorificSuffix: Optional[Union[str, List[str]]] = Field(
        None,
        description="An honorific suffix following a Person s name such as M D PhD MSCSW",
    )
    interactionStatistic: Optional[Union[str, List[str]]] = Field(
        None,
        description="The number of interactions for the CreativeWork using the WebSite or SoftwareApplication The most specific child type of InteractionCounter should be used Supersedes interactionCount",
    )
    isicV4: Optional[Union[str, List[str]]] = Field(
        None,
        description="The International Standard of Industrial Classification of All Economic Activities ISIC Revision 4 code for a particular organization business person or place",
    )
    jobTitle: Optional[Union[str, List[str]]] = Field(
        None, description="The job title of the person for example Financial Manager"
    )
    knows: Optional[Union["Person", str, List["Person"], List[str]]] = Field(
        None, description="The most generic bi directional social work relation"
    )
    knowsAbout: Optional[Union["Thing", str, List["Thing"], List[str]]] = Field(
        None,
        description="Of a Person and less typically of an Organization to indicate a topic that is known about suggesting possible expertise but not implying it We do not distinguish skill levels here or relate this to educational content events objectives or JobPosting descriptions",
    )
    knowsLanguage: Optional[Union["Language", str, List["Language"], List[str]]] = (
        Field(
            None,
            description="Of a Person and less typically of an Organization to indicate a known language We do not distinguish skill levels or reading writing speaking signing here Use language codes from the IETF BCP 47 standard",
        )
    )
    makesOffer: Optional[Union["Offer", str, List["Offer"], List[str]]] = Field(
        None,
        description="A pointer to products or services offered by the organization or person Inverse property offeredBy",
    )
    memberOf: Optional[
        Union[
            "MemberProgramTier",
            "Organization",
            "ProgramMembership",
            str,
            List["MemberProgramTier"],
            List["Organization"],
            List["ProgramMembership"],
            List[str],
        ]
    ] = Field(
        None,
        description="An Organization or ProgramMembership to which this Person or Organization belongs Inverse property member",
    )
    naics: Optional[Union[str, List[str]]] = Field(
        None,
        description="The North American Industry Classification System NAICS code for a particular organization or business person",
    )
    nationality: Optional[Union["Country", str, List["Country"], List[str]]] = Field(
        None, description="Nationality of the person"
    )
    netWorth: Optional[
        Union[
            "MonetaryAmount",
            "PriceSpecification",
            str,
            List["MonetaryAmount"],
            List["PriceSpecification"],
            List[str],
        ]
    ] = Field(
        None,
        description="The total financial value of the person as calculated by subtracting assets from liabilities",
    )
    owns: Optional[
        Union[
            "OwnershipInfo",
            "Product",
            str,
            List["OwnershipInfo"],
            List["Product"],
            List[str],
        ]
    ] = Field(None, description="Products owned by the organization or person")
    parent: Optional[Union["Person", str, List["Person"], List[str]]] = Field(
        None, description="A parent of this person Supersedes parents"
    )
    performerIn: Optional[Union[str, List[str]]] = Field(
        None, description="Event that this person is a performer or participant in"
    )
    publishingPrinciples: Optional[
        Union["CreativeWork", str, List["CreativeWork"], List[str]]
    ] = Field(
        None,
        description="The publishingPrinciples property indicates typically via URL a document describing the editorial principles of an Organization or individual e g a Person writing a blog that relate to their activities as a publisher e g ethics or diversity policies When applied to a CreativeWork e g NewsArticle the principles are those of the party primarily responsible for the creation of the CreativeWork While such policies are most typically expressed in natural language sometimes related information e g indicating a funder can be expressed using schema org terminology",
    )
    relatedTo: Optional[Union["Person", str, List["Person"], List[str]]] = Field(
        None, description="The most generic familial relation"
    )
    seeks: Optional[Union["Demand", str, List["Demand"], List[str]]] = Field(
        None,
        description="A pointer to products or services sought by the organization or person demand",
    )
    sibling: Optional[Union["Person", str, List["Person"], List[str]]] = Field(
        None, description="A sibling of the person Supersedes siblings"
    )
    skills: Optional[Union[str, List[str]]] = Field(
        None,
        description="A statement of knowledge skill ability task or any other assertion expressing a competency that is either claimed by a person an organization or desired or required to fulfill a role or to work in an occupation",
    )
    sponsor: Optional[
        Union[
            "Organization",
            "Person",
            str,
            List["Organization"],
            List["Person"],
            List[str],
        ]
    ] = Field(
        None,
        description="A person or organization that supports a thing through a pledge promise or financial contribution E g a sponsor of a Medical Study or a corporate sponsor of an event",
    )
    spouse: Optional[Union["Person", str, List["Person"], List[str]]] = Field(
        None, description="The person s spouse"
    )
    taxID: Optional[Union[str, List[str]]] = Field(
        None,
        description="The Tax Fiscal ID of the organization or person e g the TIN in the US or the CIF NIF in Spain",
    )
    telephone: Optional[Union[str, List[str]]] = Field(
        None, description="The telephone number"
    )
    vatID: Optional[Union[str, List[str]]] = Field(
        None, description="The Value added Tax ID of the organization or person"
    )
    weight: Optional[
        Union["QuantitativeValue", str, List["QuantitativeValue"], List[str]]
    ] = Field(None, description="The weight of the product or person")
    workLocation: Optional[
        Union[
            "ContactPoint", "Place", str, List["ContactPoint"], List["Place"], List[str]
        ]
    ] = Field(None, description="A contact location for a person s place of work")
    worksFor: Optional[Union["Organization", str, List["Organization"], List[str]]] = (
        Field(None, description="Organizations that the person works for")
    )


# parent dependences
model_dependence("Person", "Thing")


# attribute dependences
model_dependence(
    "Person",
    "Brand",
    "Certification",
    "ContactPoint",
    "Country",
    "CreativeWork",
    "Demand",
    "Distance",
    "EducationalOccupationalCredential",
    "EducationalOrganization",
    "Language",
    "MemberProgramTier",
    "MonetaryAmount",
    "Occupation",
    "Offer",
    "OfferCatalog",
    "Organization",
    "OwnershipInfo",
    "Place",
    "PostalAddress",
    "PriceSpecification",
    "Product",
    "ProgramMembership",
    "QuantitativeValue",
    "Thing",
)
