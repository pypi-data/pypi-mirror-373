# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import (
    Text,
    URL,
    DefinedTerm,
    Integer,
    DateTime,
    Number,
    Date,
    Grant,
    InteractionCounter,
    Boolean,
    Event,
)


# base imports
from .thing import Thing


@register_model
class CreativeWork(Thing):
    """The most generic kind of creative work including books movies photographs software programs etc"""

    about: Optional[Union["Thing", str, List["Thing"], List[str]]] = Field(
        None, description="The subject matter of the content Inverse property subjectOf"
    )
    abstract: Optional[Union[str, List[str]]] = Field(
        None,
        description="An abstract is a short description that summarizes a CreativeWork",
    )
    accessMode: Optional[Union[str, List[str]]] = Field(
        None,
        description="The human sensory perceptual system or cognitive faculty through which a person may process or perceive information Values should be drawn from the approved vocabulary",
    )
    accessModeSufficient: Optional[
        Union["ItemList", str, List["ItemList"], List[str]]
    ] = Field(
        None,
        description="A list of single or combined accessModes that are sufficient to understand all the intellectual content of a resource Values should be drawn from the approved vocabulary",
    )
    accessibilityAPI: Optional[Union[str, List[str]]] = Field(
        None,
        description="Indicates that the resource is compatible with the referenced accessibility API Values should be drawn from the approved vocabulary",
    )
    accessibilityControl: Optional[Union[str, List[str]]] = Field(
        None,
        description="Identifies input methods that are sufficient to fully control the described resource Values should be drawn from the approved vocabulary",
    )
    accessibilityFeature: Optional[Union[str, List[str]]] = Field(
        None,
        description="Content features of the resource such as accessible media alternatives and supported enhancements for accessibility Values should be drawn from the approved vocabulary",
    )
    accessibilityHazard: Optional[Union[str, List[str]]] = Field(
        None,
        description="A characteristic of the described resource that is physiologically dangerous to some users Related to WCAG 2 0 guideline 2 3 Values should be drawn from the approved vocabulary",
    )
    accessibilitySummary: Optional[Union[str, List[str]]] = Field(
        None,
        description="A human readable summary of specific accessibility features or deficiencies consistent with the other accessibility metadata but expressing subtleties such as short descriptions are present but long descriptions will be needed for non visual users or short descriptions are present and no long descriptions are needed",
    )
    accountablePerson: Optional[Union["Person", str, List["Person"], List[str]]] = (
        Field(
            None,
            description="Specifies the Person that is legally accountable for the CreativeWork",
        )
    )
    acquireLicensePage: Optional[
        Union["CreativeWork", str, List["CreativeWork"], List[str]]
    ] = Field(
        None,
        description="Indicates a page documenting how licenses can be purchased or otherwise acquired for the current item",
    )
    aggregateRating: Optional[
        Union["AggregateRating", str, List["AggregateRating"], List[str]]
    ] = Field(
        None,
        description="The overall rating based on a collection of reviews or ratings of the item",
    )
    alternativeHeadline: Optional[Union[str, List[str]]] = Field(
        None, description="A secondary title of the CreativeWork"
    )
    archivedAt: Optional[Union["WebPage", str, List["WebPage"], List[str]]] = Field(
        None,
        description="Indicates a page or other link involved in archival of a CreativeWork In the case of MediaReview the items in a MediaReviewItem may often become inaccessible but be archived by archival journalistic activist or law enforcement organizations In such cases the referenced page may not directly publish the content",
    )
    assesses: Optional[Union[str, List[str]]] = Field(
        None,
        description="The item being described is intended to assess the competency or learning outcome defined by the referenced term",
    )
    associatedMedia: Optional[
        Union["MediaObject", str, List["MediaObject"], List[str]]
    ] = Field(
        None,
        description="A media object that encodes this CreativeWork This property is a synonym for encoding",
    )
    audience: Optional[Union["Audience", str, List["Audience"], List[str]]] = Field(
        None,
        description="An intended audience i e a group for whom something was created Supersedes serviceAudience",
    )
    audio: Optional[
        Union[
            "AudioObject",
            "Clip",
            "MusicRecording",
            str,
            List["AudioObject"],
            List["Clip"],
            List["MusicRecording"],
            List[str],
        ]
    ] = Field(None, description="An embedded audio object")
    author: Optional[
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
        description="The author of this content or rating Please note that author is special in that HTML 5 provides a special mechanism for indicating authorship via the rel tag That is equivalent to this and may be used interchangeably",
    )
    award: Optional[Union[str, List[str]]] = Field(
        None, description="An award won by or for this item Supersedes awards"
    )
    character: Optional[Union["Person", str, List["Person"], List[str]]] = Field(
        None, description="Fictional person connected with a creative work"
    )
    citation: Optional[Union["CreativeWork", str, List["CreativeWork"], List[str]]] = (
        Field(
            None,
            description="A citation or reference to another creative work such as another publication web page scholarly article etc",
        )
    )
    comment: Optional[Union["Comment", str, List["Comment"], List[str]]] = Field(
        None, description="Comments typically from users"
    )
    commentCount: Optional[Union[int, List[int]]] = Field(
        None,
        description="The number of comments this CreativeWork e g Article Question or Answer has received This is most applicable to works published in Web sites with commenting system additional comments may exist elsewhere",
    )
    conditionsOfAccess: Optional[Union[str, List[str]]] = Field(
        None,
        description="Conditions that affect the availability of or method s of access to an item Typically used for real world items such as an ArchiveComponent held by an ArchiveOrganization This property is not suitable for use as a general Web access control mechanism It is expressed only in natural language For example Available by appointment from the Reading Room or Accessible only from logged in accounts",
    )
    contentLocation: Optional[Union["Place", str, List["Place"], List[str]]] = Field(
        None,
        description="The location depicted or described in the content For example the location in a photograph or painting",
    )
    contentRating: Optional[Union["Rating", str, List["Rating"], List[str]]] = Field(
        None, description="Official rating of a piece of content for example MPAA PG 13"
    )
    contentReferenceTime: Optional[Union[str, List[str]]] = Field(
        None,
        description="The specific time described by a creative work for works e g articles video objects etc that emphasise a particular moment within an Event",
    )
    contributor: Optional[
        Union[
            "Organization",
            "Person",
            str,
            List["Organization"],
            List["Person"],
            List[str],
        ]
    ] = Field(None, description="A secondary contributor to the CreativeWork or Event")
    copyrightHolder: Optional[
        Union[
            "Organization",
            "Person",
            str,
            List["Organization"],
            List["Person"],
            List[str],
        ]
    ] = Field(
        None, description="The party holding the legal copyright to the CreativeWork"
    )
    copyrightNotice: Optional[Union[str, List[str]]] = Field(
        None,
        description="Text of a notice appropriate for describing the copyright aspects of this Creative Work ideally indicating the owner of the copyright for the Work",
    )
    copyrightYear: Optional[Union[float, List[float]]] = Field(
        None,
        description="The year during which the claimed copyright for the CreativeWork was first asserted",
    )
    correction: Optional[
        Union["CorrectionComment", str, List["CorrectionComment"], List[str]]
    ] = Field(
        None,
        description="Indicates a correction to a CreativeWork either via a CorrectionComment textually or in another document",
    )
    countryOfOrigin: Optional[Union["Country", str, List["Country"], List[str]]] = (
        Field(
            None,
            description="The country of origin of something including products as well as creative works such as movie and TV content In the case of TV and movie this would be the country of the principle offices of the production company or individual responsible for the movie For other kinds of CreativeWork it is difficult to provide fully general guidance and properties such as contentLocation and locationCreated may be more applicable In the case of products the country of origin of the product The exact interpretation of this may vary by context and product type and cannot be fully enumerated here",
        )
    )
    creativeWorkStatus: Optional[Union[str, List[str]]] = Field(
        None,
        description="The status of a creative work in terms of its stage in a lifecycle Example terms include Incomplete Draft Published Obsolete Some organizations define a set of terms for the stages of their publication lifecycle",
    )
    creator: Optional[
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
        description="The creator author of this CreativeWork This is the same as the Author property for CreativeWork",
    )
    creditText: Optional[Union[str, List[str]]] = Field(
        None,
        description="Text that can be used to credit person s and or organization s associated with a published Creative Work",
    )
    dateCreated: Optional[Union[str, List[str]]] = Field(
        None,
        description="The date on which the CreativeWork was created or the item was added to a DataFeed",
    )
    dateModified: Optional[Union[str, List[str]]] = Field(
        None,
        description="The date on which the CreativeWork was most recently modified or when the item s entry was modified within a DataFeed",
    )
    datePublished: Optional[Union[str, List[str]]] = Field(
        None,
        description="Date of first publication or broadcast For example the date a CreativeWork was broadcast or a Certification was issued",
    )
    digitalSourceType: Optional[
        Union[
            "IPTCDigitalSourceEnumeration",
            str,
            List["IPTCDigitalSourceEnumeration"],
            List[str],
        ]
    ] = Field(
        None,
        description="Indicates an IPTCDigitalSourceEnumeration code indicating the nature of the digital source s for some CreativeWork",
    )
    discussionUrl: Optional[Union[str, List[str]]] = Field(
        None,
        description="A link to the page containing the comments of the CreativeWork",
    )
    editEIDR: Optional[Union[str, List[str]]] = Field(
        None,
        description="An EIDR Entertainment Identifier Registry identifier representing a specific edit edition for a work of film or television For example the motion picture known as Ghostbusters whose titleEIDR is 10 5240 7EC7 228A 510A 053E CBB8 J has several edits e g 10 5240 1F2A E1C5 680A 14C6 E76B I and 10 5240 8A35 3BEE 6497 5D12 9E4F 3 Since schema org types like Movie and TVEpisode can be used for both works and their multiple expressions it is possible to use titleEIDR alone for a general description or alongside editEIDR for a more edit specific description",
    )
    editor: Optional[Union["Person", str, List["Person"], List[str]]] = Field(
        None, description="Specifies the Person who edited the CreativeWork"
    )
    educationalAlignment: Optional[
        Union["AlignmentObject", str, List["AlignmentObject"], List[str]]
    ] = Field(
        None,
        description="An alignment to an established educational framework This property should not be used where the nature of the alignment can be described using a simple property for example to express that a resource teaches or assesses a competency",
    )
    educationalLevel: Optional[Union[str, List[str]]] = Field(
        None,
        description="The level in terms of progression through an educational or training context Examples of educational levels include beginner intermediate or advanced and formal sets of level indicators",
    )
    educationalUse: Optional[Union[str, List[str]]] = Field(
        None,
        description="The purpose of a work in the context of education for example assignment group work",
    )
    encoding: Optional[Union["MediaObject", str, List["MediaObject"], List[str]]] = (
        Field(
            None,
            description="A media object that encodes this CreativeWork This property is a synonym for associatedMedia Supersedes encodings Inverse property encodesCreativeWork",
        )
    )
    encodingFormat: Optional[Union[str, List[str]]] = Field(
        None,
        description="Media type typically expressed using a MIME format see IANA site and MDN reference e g application zip for a SoftwareApplication binary audio mpeg for mp3 etc In cases where a CreativeWork has several media type representations encoding can be used to indicate each MediaObject alongside particular encodingFormat information Unregistered or niche encoding and file formats can be indicated instead via the most appropriate URL e g defining Web page or a Wikipedia Wikidata entry Supersedes fileFormat",
    )
    exampleOfWork: Optional[
        Union["CreativeWork", str, List["CreativeWork"], List[str]]
    ] = Field(
        None,
        description="A creative work that this work is an example instance realization derivation of Inverse property workExample",
    )
    expires: Optional[Union[str, List[str]]] = Field(
        None,
        description="Date the content expires and is no longer useful or available For example a VideoObject or NewsArticle whose availability or relevance is time limited a ClaimReview fact check whose publisher wants to indicate that it may no longer be relevant or helpful to highlight after some date or a Certification the validity has expired",
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
    genre: Optional[Union[str, List[str]]] = Field(
        None, description="Genre of the creative work broadcast channel or group"
    )
    hasPart: Optional[Union["CreativeWork", str, List["CreativeWork"], List[str]]] = (
        Field(
            None,
            description="Indicates an item or CreativeWork that is part of this item or CreativeWork in some sense Inverse property isPartOf",
        )
    )
    headline: Optional[Union[str, List[str]]] = Field(
        None, description="Headline of the article"
    )
    inLanguage: Optional[Union["Language", str, List["Language"], List[str]]] = Field(
        None,
        description="The language of the content or performance or used in an action Please use one of the language codes from the IETF BCP 47 standard See also availableLanguage Supersedes language",
    )
    interactionStatistic: Optional[Union[str, List[str]]] = Field(
        None,
        description="The number of interactions for the CreativeWork using the WebSite or SoftwareApplication The most specific child type of InteractionCounter should be used Supersedes interactionCount",
    )
    interactivityType: Optional[Union[str, List[str]]] = Field(
        None,
        description="The predominant mode of learning supported by the learning resource Acceptable values are active expositive or mixed",
    )
    interpretedAsClaim: Optional[Union["Claim", str, List["Claim"], List[str]]] = Field(
        None,
        description="Used to indicate a specific claim contained implied translated or refined from the content of a MediaObject or other CreativeWork The interpreting party can be indicated using claimInterpreter",
    )
    isAccessibleForFree: Optional[Union["bool", List["bool"]]] = Field(
        None,
        description="A flag to signal that the item event or place is accessible for free Supersedes free",
    )
    isBasedOn: Optional[
        Union[
            "CreativeWork",
            "Product",
            str,
            List["CreativeWork"],
            List["Product"],
            List[str],
        ]
    ] = Field(
        None,
        description="A resource from which this work is derived or from which it is a modification or adaptation Supersedes isBasedOnUrl",
    )
    isFamilyFriendly: Optional[Union["bool", List["bool"]]] = Field(
        None, description="Indicates whether this content is family friendly"
    )
    isPartOf: Optional[Union["CreativeWork", str, List["CreativeWork"], List[str]]] = (
        Field(
            None,
            description="Indicates an item or CreativeWork that this item or CreativeWork in some sense is part of Inverse property hasPart",
        )
    )
    keywords: Optional[Union[str, List[str]]] = Field(
        None,
        description="Keywords or tags used to describe some item Multiple textual entries in a keywords list are typically delimited by commas or by repeating the property",
    )
    learningResourceType: Optional[Union[str, List[str]]] = Field(
        None,
        description="The predominant type or kind characterizing the learning resource For example presentation handout",
    )
    license: Optional[Union["CreativeWork", str, List["CreativeWork"], List[str]]] = (
        Field(
            None,
            description="A license document that applies to this content typically indicated by URL",
        )
    )
    locationCreated: Optional[Union["Place", str, List["Place"], List[str]]] = Field(
        None,
        description="The location where the CreativeWork was created which may not be the same as the location depicted in the CreativeWork",
    )
    mainEntity: Optional[Union["Thing", str, List["Thing"], List[str]]] = Field(
        None,
        description="Indicates the primary entity described in some page or other CreativeWork Inverse property mainEntityOfPage",
    )
    maintainer: Optional[
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
        description="A maintainer of a Dataset software package SoftwareApplication or other Project A maintainer is a Person or Organization that manages contributions to and or publication of some typically complex artifact It is common for distributions of software and data to be based on upstream sources When maintainer is applied to a specific version of something e g a particular version or packaging of a Dataset it is always possible that the upstream source has a different maintainer The isBasedOn property can be used to indicate such relationships between datasets to make the different maintenance roles clear Similarly in the case of software a package may have dedicated maintainers working on integration into software distributions such as Ubuntu as well as upstream maintainers of the underlying work",
    )
    material: Optional[Union["Product", str, List["Product"], List[str]]] = Field(
        None,
        description="A material that something is made from e g leather wool cotton paper",
    )
    materialExtent: Optional[
        Union["QuantitativeValue", str, List["QuantitativeValue"], List[str]]
    ] = Field(
        None,
        description="The quantity of the materials being described or an expression of the physical space they occupy",
    )
    mentions: Optional[Union["Thing", str, List["Thing"], List[str]]] = Field(
        None,
        description="Indicates that the CreativeWork contains a reference to but is not necessarily about a concept",
    )
    offers: Optional[
        Union["Demand", "Offer", str, List["Demand"], List["Offer"], List[str]]
    ] = Field(
        None,
        description="An offer to provide this item for example an offer to sell a product rent the DVD of a movie perform a service or give away tickets to an event Use businessFunction to indicate the kind of transaction offered i e sell lease etc This property can also be used to describe a Demand While this property is listed as expected on a number of common types it can be used in others In that case using a second type such as Product or a subtype of Product can clarify the nature of the offer Inverse property itemOffered",
    )
    pattern: Optional[Union[str, List[str]]] = Field(
        None,
        description="A pattern that something has for example polka dot striped Canadian flag Values are typically expressed as text although links to controlled value schemes are also supported",
    )
    position: Optional[Union[int, str, List[int], List[str]]] = Field(
        None, description="The position of an item in a series or sequence of items"
    )
    producer: Optional[
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
        description="The person or organization who produced the work e g music album movie TV radio series etc",
    )
    provider: Optional[
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
        description="The service provider service operator or service performer the goods producer Another party a seller may offer those services or goods on behalf of the provider A provider may also serve as the seller Supersedes carrier",
    )
    publication: Optional[
        Union["PublicationEvent", str, List["PublicationEvent"], List[str]]
    ] = Field(None, description="A publication event associated with the item")
    publisher: Optional[
        Union[
            "Organization",
            "Person",
            str,
            List["Organization"],
            List["Person"],
            List[str],
        ]
    ] = Field(None, description="The publisher of the creative work")
    publisherImprint: Optional[
        Union["Organization", str, List["Organization"], List[str]]
    ] = Field(None, description="The publishing division which published the comic")
    publishingPrinciples: Optional[
        Union["CreativeWork", str, List["CreativeWork"], List[str]]
    ] = Field(
        None,
        description="The publishingPrinciples property indicates typically via URL a document describing the editorial principles of an Organization or individual e g a Person writing a blog that relate to their activities as a publisher e g ethics or diversity policies When applied to a CreativeWork e g NewsArticle the principles are those of the party primarily responsible for the creation of the CreativeWork While such policies are most typically expressed in natural language sometimes related information e g indicating a funder can be expressed using schema org terminology",
    )
    recordedAt: Optional[Union[str, List[str]]] = Field(
        None,
        description="The Event where the CreativeWork was recorded The CreativeWork may capture all or part of the event Inverse property recordedIn",
    )
    releasedEvent: Optional[
        Union["PublicationEvent", str, List["PublicationEvent"], List[str]]
    ] = Field(
        None,
        description="The place and time the release was issued expressed as a PublicationEvent",
    )
    review: Optional[Union["Review", str, List["Review"], List[str]]] = Field(
        None, description="A review of the item Supersedes reviews"
    )
    schemaVersion: Optional[Union[str, List[str]]] = Field(
        None,
        description="Indicates by URL or string a particular version of a schema used in some CreativeWork This property was created primarily to indicate the use of a specific schema org release e g 10 0 as a simple string or more explicitly via URL https schema org docs releases html v10 0 There may be situations in which other schemas might usefully be referenced this way e g http dublincore org specifications dublin core dces 1999 07 02 but this has not been carefully explored in the community",
    )
    sdDatePublished: Optional[Union[str, List[str]]] = Field(
        None,
        description="Indicates the date on which the current structured data was generated published Typically used alongside sdPublisher",
    )
    sdLicense: Optional[Union["CreativeWork", str, List["CreativeWork"], List[str]]] = (
        Field(
            None,
            description="A license document that applies to this structured data typically indicated by URL",
        )
    )
    sdPublisher: Optional[
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
        description="Indicates the party responsible for generating and publishing the current structured data markup typically in cases where the structured data is derived automatically from existing published content but published on a different site For example student projects and open data initiatives often re publish existing content with more explicitly structured metadata The sdPublisher property helps make such practices more explicit",
    )
    size: Optional[
        Union[
            "QuantitativeValue",
            "SizeSpecification",
            str,
            List["QuantitativeValue"],
            List["SizeSpecification"],
            List[str],
        ]
    ] = Field(
        None,
        description="A standardized size of a product or creative work specified either through a simple textual string for example XL 32Wx34L a QuantitativeValue with a unitCode or a comprehensive and structured SizeSpecification in other cases the width height depth and weight properties may be more applicable",
    )
    sourceOrganization: Optional[
        Union["Organization", str, List["Organization"], List[str]]
    ] = Field(
        None, description="The Organization on whose behalf the creator was working"
    )
    spatial: Optional[Union["Place", str, List["Place"], List[str]]] = Field(
        None,
        description="The spatial property can be used in cases when more specific properties e g locationCreated spatialCoverage contentLocation are not known to be appropriate",
    )
    spatialCoverage: Optional[Union["Place", str, List["Place"], List[str]]] = Field(
        None,
        description="The spatialCoverage of a CreativeWork indicates the place s which are the focus of the content It is a subproperty of contentLocation intended primarily for more technical and detailed materials For example with a Dataset it indicates areas that the dataset describes a dataset of New York weather would have spatialCoverage which was the place the state of New York",
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
    teaches: Optional[Union[str, List[str]]] = Field(
        None,
        description="The item being described is intended to help a person learn the competency or learning outcome defined by the referenced term",
    )
    temporal: Optional[Union[str, List[str]]] = Field(
        None,
        description="The temporal property can be used in cases where more specific properties e g temporalCoverage dateCreated dateModified datePublished are not known to be appropriate",
    )
    temporalCoverage: Optional[Union[str, List[str]]] = Field(
        None,
        description="The temporalCoverage of a CreativeWork indicates the period that the content applies to i e that it describes either as a DateTime or as a textual string indicating a time period in ISO 8601 time interval format In the case of a Dataset it will typically indicate the relevant time period in a precise notation e g for a 2011 census dataset the year 2011 would be written 2011 2012 Other forms of content e g ScholarlyArticle Book TVSeries or TVEpisode may indicate their temporalCoverage in broader terms textually or via well known URL Written works such as books may sometimes have precise temporal coverage too e g a work set in 1939 1945 can be indicated in ISO 8601 interval format format via 1939 1945 Open ended date ranges can be written with in place of the end date For example 2015 11 indicates a range beginning in November 2015 and with no specified final date This is tentative and might be updated in future when ISO 8601 is officially updated Supersedes datasetTimeInterval",
    )
    text: Optional[Union[str, List[str]]] = Field(
        None, description="The textual content of this CreativeWork"
    )
    thumbnail: Optional[Union["ImageObject", str, List["ImageObject"], List[str]]] = (
        Field(None, description="Thumbnail image for an image or video")
    )
    thumbnailUrl: Optional[Union[str, List[str]]] = Field(
        None, description="A thumbnail image relevant to the Thing"
    )
    timeRequired: Optional[Union["Duration", str, List["Duration"], List[str]]] = Field(
        None,
        description="Approximate or typical time it usually takes to work with or through the content of this work for the typical or target audience",
    )
    translationOfWork: Optional[
        Union["CreativeWork", str, List["CreativeWork"], List[str]]
    ] = Field(
        None,
        description="The work that this work has been translated from E g ç ç èµ æº is a translationOf â On the Origin of Speciesâ Inverse property workTranslation",
    )
    translator: Optional[
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
        description="Organization or person who adapts a creative work to different languages regional differences and technical requirements of a target market or that translates during some event",
    )
    typicalAgeRange: Optional[Union[str, List[str]]] = Field(
        None, description="The typical expected age range e g 7 9 11"
    )
    usageInfo: Optional[Union["CreativeWork", str, List["CreativeWork"], List[str]]] = (
        Field(
            None,
            description="The schema org usageInfo property indicates further information about a CreativeWork This property is applicable both to works that are freely available and to those that require payment or other transactions It can reference additional information e g community expectations on preferred linking and citation conventions as well as purchasing details For something that can be commercially licensed usageInfo can provide detailed resource specific information about licensing options This property can be used alongside the license property which indicates license s applicable to some piece of content The usageInfo property can provide information about other licensing options e g acquiring commercial usage rights for an image that is also available under non commercial creative commons licenses",
        )
    )
    version: Optional[Union[float, str, List[float], List[str]]] = Field(
        None,
        description="The version of the CreativeWork embodied by a specified resource",
    )
    video: Optional[
        Union["Clip", "VideoObject", str, List["Clip"], List["VideoObject"], List[str]]
    ] = Field(None, description="An embedded video object")
    workExample: Optional[
        Union["CreativeWork", str, List["CreativeWork"], List[str]]
    ] = Field(
        None,
        description="Example instance realization derivation of the concept of this creative work E g the paperback edition first edition or e book Inverse property exampleOfWork",
    )
    workTranslation: Optional[
        Union["CreativeWork", str, List["CreativeWork"], List[str]]
    ] = Field(
        None,
        description="A work that is a translation of the content of this work E g è é è has an English workTranslation â Journey to the Westâ a German workTranslation â Monkeys Pilgerfahrtâ and a Vietnamese translation TÃ y du kÃ½ bÃ nh kháº o Inverse property translationOfWork",
    )


# parent dependences
model_dependence("CreativeWork", "Thing")


# attribute dependences
model_dependence(
    "CreativeWork",
    "AggregateRating",
    "AlignmentObject",
    "Audience",
    "AudioObject",
    "Claim",
    "Clip",
    "Comment",
    "CorrectionComment",
    "Country",
    "Demand",
    "Duration",
    "IPTCDigitalSourceEnumeration",
    "ImageObject",
    "ItemList",
    "Language",
    "MediaObject",
    "MusicRecording",
    "Offer",
    "Organization",
    "Person",
    "Place",
    "Product",
    "PublicationEvent",
    "QuantitativeValue",
    "Rating",
    "Review",
    "SizeSpecification",
    "Thing",
    "VideoObject",
    "WebPage",
)
