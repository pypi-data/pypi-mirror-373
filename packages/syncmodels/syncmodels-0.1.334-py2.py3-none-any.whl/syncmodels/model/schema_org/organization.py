# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Text, URL, InteractionCounter, Date, Event, Grant, DefinedTerm


# base imports
from .thing import Thing


@register_model
class Organization(Thing):
    """An organization such as a school NGO corporation club etc"""

    acceptedPaymentMethod: Optional[
        Union[
            "LoanOrCredit",
            "PaymentMethod",
            str,
            List["LoanOrCredit"],
            List["PaymentMethod"],
            List[str],
        ]
    ] = Field(
        None,
        description="The payment method s that are accepted in general by an organization or for some specific demand or offer",
    )
    actionableFeedbackPolicy: Optional[
        Union["CreativeWork", str, List["CreativeWork"], List[str]]
    ] = Field(
        None,
        description="For a NewsMediaOrganization or other news related Organization a statement about public engagement activities for news media the newsroomâ s including involving the public digitally or otherwise in coverage decisions reporting and activities after publication",
    )
    address: Optional[Union["PostalAddress", str, List["PostalAddress"], List[str]]] = (
        Field(None, description="Physical address of the item")
    )
    agentInteractionStatistic: Optional[Union[str, List[str]]] = Field(
        None,
        description="The number of completed interactions for this entity in a particular role the agent in a particular action indicated in the statistic and in a particular context i e interactionService",
    )
    aggregateRating: Optional[
        Union["AggregateRating", str, List["AggregateRating"], List[str]]
    ] = Field(
        None,
        description="The overall rating based on a collection of reviews or ratings of the item",
    )
    alumni: Optional[Union["Person", str, List["Person"], List[str]]] = Field(
        None, description="Alumni of an organization Inverse property alumniOf"
    )
    areaServed: Optional[
        Union[
            "AdministrativeArea",
            "GeoShape",
            "Place",
            str,
            List["AdministrativeArea"],
            List["GeoShape"],
            List["Place"],
            List[str],
        ]
    ] = Field(
        None,
        description="The geographic area where a service or offered item is provided Supersedes serviceArea",
    )
    award: Optional[Union[str, List[str]]] = Field(
        None, description="An award won by or for this item Supersedes awards"
    )
    brand: Optional[
        Union[
            "Brand", "Organization", str, List["Brand"], List["Organization"], List[str]
        ]
    ] = Field(
        None,
        description="The brand s associated with a product or service or the brand s maintained by an organization or business person",
    )
    contactPoint: Optional[
        Union["ContactPoint", str, List["ContactPoint"], List[str]]
    ] = Field(
        None,
        description="A contact point for a person or organization Supersedes contactPoints",
    )
    correctionsPolicy: Optional[
        Union["CreativeWork", str, List["CreativeWork"], List[str]]
    ] = Field(
        None,
        description="For an Organization e g NewsMediaOrganization a statement describing in news media the newsroomâ s disclosure and correction policy for errors",
    )
    department: Optional[
        Union["Organization", str, List["Organization"], List[str]]
    ] = Field(
        None,
        description="A relationship between an organization and a department of that organization also described as an organization allowing different urls logos opening hours For example a store with a pharmacy or a bakery with a cafe",
    )
    dissolutionDate: Optional[Union[str, List[str]]] = Field(
        None, description="The date that this organization was dissolved"
    )
    diversityPolicy: Optional[
        Union["CreativeWork", str, List["CreativeWork"], List[str]]
    ] = Field(
        None,
        description="Statement on diversity policy by an Organization e g a NewsMediaOrganization For a NewsMediaOrganization a statement describing the newsroomâ s diversity policy on both staffing and sources typically providing staffing data",
    )
    diversityStaffingReport: Optional[
        Union["Article", str, List["Article"], List[str]]
    ] = Field(
        None,
        description="For an Organization often but not necessarily a NewsMediaOrganization a report on staffing diversity issues In a news context this might be for example ASNE or RTDNA US reports or self reported",
    )
    duns: Optional[Union[str, List[str]]] = Field(
        None,
        description="The Dun Bradstreet DUNS number for identifying an organization or business person",
    )
    email: Optional[Union[str, List[str]]] = Field(None, description="Email address")
    employee: Optional[Union["Person", str, List["Person"], List[str]]] = Field(
        None, description="Someone working for this organization Supersedes employees"
    )
    ethicsPolicy: Optional[
        Union["CreativeWork", str, List["CreativeWork"], List[str]]
    ] = Field(
        None,
        description="Statement about ethics policy e g of a NewsMediaOrganization regarding journalistic and publishing practices or of a Restaurant a page describing food source policies In the case of a NewsMediaOrganization an ethicsPolicy is typically a statement describing the personal organizational and corporate standards of behavior expected by the organization",
    )
    event: Optional[Union[str, List[str]]] = Field(
        None,
        description="Upcoming or past event associated with this place organization or action Supersedes events",
    )
    faxNumber: Optional[Union[int, str, List[int], List[str]]] = Field(
        None, description="The fax number"
    )
    founder: Optional[
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
        description="A person or organization who founded this organization Supersedes founders",
    )
    foundingDate: Optional[Union[str, List[str]]] = Field(
        None, description="The date that this organization was founded"
    )
    foundingLocation: Optional[Union["Place", str, List["Place"], List[str]]] = Field(
        None, description="The place where the Organization was founded"
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
    hasGS1DigitalLink: Optional[Union[str, List[str]]] = Field(
        None,
        description="The GS1 digital link associated with the object This URL should conform to the particular requirements of digital links The link should only contain the Application Identifiers AIs that are relevant for the entity being annotated for instance a Product or an Organization and for the correct granularity In particular for products A Digital Link that contains a serial number AI 21 should only be present on instances of IndividualProductA Digital Link that contains a lot number AI 10 should be annotated as SomeProduct if only products from that lot are sold or IndividualProduct if there is only a specific product A Digital Link that contains a global model number AI 8013 should be attached to a Product or a ProductModel Other item types should be adapted similarly",
    )
    hasMemberProgram: Optional[
        Union["MemberProgram", str, List["MemberProgram"], List[str]]
    ] = Field(
        None,
        description="MemberProgram offered by an Organization for example an eCommerce merchant or an airline",
    )
    hasMerchantReturnPolicy: Optional[
        Union["MerchantReturnPolicy", str, List["MerchantReturnPolicy"], List[str]]
    ] = Field(
        None,
        description="Specifies a MerchantReturnPolicy that may be applicable Supersedes hasProductReturnPolicy",
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
    interactionStatistic: Optional[Union[str, List[str]]] = Field(
        None,
        description="The number of interactions for the CreativeWork using the WebSite or SoftwareApplication The most specific child type of InteractionCounter should be used Supersedes interactionCount",
    )
    isicV4: Optional[Union[str, List[str]]] = Field(
        None,
        description="The International Standard of Industrial Classification of All Economic Activities ISIC Revision 4 code for a particular organization business person or place",
    )
    iso6523Code: Optional[Union[str, List[str]]] = Field(
        None,
        description="An organization identifier as defined in ISO 6523 1 The identifier should be in the XXXX YYYYYY ZZZ or XXXX YYYYYYformat Where XXXX is a 4 digit ICD International Code Designator YYYYYY is an OID Organization Identifier with all formatting characters dots dashes spaces removed with a maximal length of 35 characters and ZZZ is an optional OPI Organization Part Identifier with a maximum length of 35 characters The various components ICD OID OPI are joined with a colon character ASCII 0x3a Note that many existing organization identifiers defined as attributes like leiCode 0199 duns 0060 or GLN 0088 can be expressed using ISO 6523 If possible ISO 6523 codes should be preferred to populating vatID or taxID as ISO identifiers are less ambiguous",
    )
    keywords: Optional[Union[str, List[str]]] = Field(
        None,
        description="Keywords or tags used to describe some item Multiple textual entries in a keywords list are typically delimited by commas or by repeating the property",
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
    legalName: Optional[Union[str, List[str]]] = Field(
        None,
        description="The official name of the organization e g the registered company name",
    )
    leiCode: Optional[Union[str, List[str]]] = Field(
        None,
        description="An organization identifier that uniquely identifies a legal entity as defined in ISO 17442",
    )
    location: Optional[
        Union[
            "Place",
            "PostalAddress",
            "VirtualLocation",
            str,
            List["Place"],
            List["PostalAddress"],
            List["VirtualLocation"],
            List[str],
        ]
    ] = Field(
        None,
        description="The location of for example where an event is happening where an organization is located or where an action takes place",
    )
    logo: Optional[Union["ImageObject", str, List["ImageObject"], List[str]]] = Field(
        None, description="An associated logo"
    )
    makesOffer: Optional[Union["Offer", str, List["Offer"], List[str]]] = Field(
        None,
        description="A pointer to products or services offered by the organization or person Inverse property offeredBy",
    )
    member: Optional[
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
        description="A member of an Organization or a ProgramMembership Organizations can be members of organizations ProgramMembership is typically for individuals Supersedes members musicGroupMember Inverse property memberOf",
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
    nonprofitStatus: Optional[
        Union["NonprofitType", str, List["NonprofitType"], List[str]]
    ] = Field(
        None,
        description="nonprofitStatus indicates the legal status of a non profit organization in its primary place of business",
    )
    numberOfEmployees: Optional[
        Union["QuantitativeValue", str, List["QuantitativeValue"], List[str]]
    ] = Field(
        None, description="The number of employees in an organization e g business"
    )
    ownershipFundingInfo: Optional[
        Union[
            "AboutPage",
            "CreativeWork",
            str,
            List["AboutPage"],
            List["CreativeWork"],
            List[str],
        ]
    ] = Field(
        None,
        description="For an Organization often but not necessarily a NewsMediaOrganization a description of organizational ownership structure funding and grants In a news media setting this is with particular reference to editorial independence Note that the funder is also available and can be used to make basic funder information machine readable",
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
    parentOrganization: Optional[
        Union["Organization", str, List["Organization"], List[str]]
    ] = Field(
        None,
        description="The larger organization that this organization is a subOrganization of if any Supersedes branchOf Inverse property subOrganization",
    )
    publishingPrinciples: Optional[
        Union["CreativeWork", str, List["CreativeWork"], List[str]]
    ] = Field(
        None,
        description="The publishingPrinciples property indicates typically via URL a document describing the editorial principles of an Organization or individual e g a Person writing a blog that relate to their activities as a publisher e g ethics or diversity policies When applied to a CreativeWork e g NewsArticle the principles are those of the party primarily responsible for the creation of the CreativeWork While such policies are most typically expressed in natural language sometimes related information e g indicating a funder can be expressed using schema org terminology",
    )
    review: Optional[Union["Review", str, List["Review"], List[str]]] = Field(
        None, description="A review of the item Supersedes reviews"
    )
    seeks: Optional[Union["Demand", str, List["Demand"], List[str]]] = Field(
        None,
        description="A pointer to products or services sought by the organization or person demand",
    )
    skills: Optional[Union[str, List[str]]] = Field(
        None,
        description="A statement of knowledge skill ability task or any other assertion expressing a competency that is either claimed by a person an organization or desired or required to fulfill a role or to work in an occupation",
    )
    slogan: Optional[Union[str, List[str]]] = Field(
        None, description="A slogan or motto associated with the item"
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
    subOrganization: Optional[
        Union["Organization", str, List["Organization"], List[str]]
    ] = Field(
        None,
        description="A relationship between two organizations where the first includes the second e g as a subsidiary See also the more specific department property Inverse property parentOrganization",
    )
    taxID: Optional[Union[str, List[str]]] = Field(
        None,
        description="The Tax Fiscal ID of the organization or person e g the TIN in the US or the CIF NIF in Spain",
    )
    telephone: Optional[Union[str, List[str]]] = Field(
        None, description="The telephone number"
    )
    unnamedSourcesPolicy: Optional[
        Union["CreativeWork", str, List["CreativeWork"], List[str]]
    ] = Field(
        None,
        description="For an Organization typically a NewsMediaOrganization a statement about policy on use of unnamed sources and the decision process required",
    )
    vatID: Optional[Union[str, List[str]]] = Field(
        None, description="The Value added Tax ID of the organization or person"
    )


# parent dependences
model_dependence("Organization", "Thing")


# attribute dependences
model_dependence(
    "Organization",
    "AboutPage",
    "AdministrativeArea",
    "AggregateRating",
    "Article",
    "Brand",
    "Certification",
    "ContactPoint",
    "CreativeWork",
    "Demand",
    "EducationalOccupationalCredential",
    "GeoShape",
    "ImageObject",
    "Language",
    "LoanOrCredit",
    "MemberProgram",
    "MemberProgramTier",
    "MerchantReturnPolicy",
    "NonprofitType",
    "Offer",
    "OfferCatalog",
    "OwnershipInfo",
    "PaymentMethod",
    "Person",
    "Place",
    "PostalAddress",
    "Product",
    "ProgramMembership",
    "QuantitativeValue",
    "Review",
    "Thing",
    "VirtualLocation",
)
