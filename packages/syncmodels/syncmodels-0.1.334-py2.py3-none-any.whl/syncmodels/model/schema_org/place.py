# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import (
    PropertyValue,
    Text,
    Event,
    Boolean,
    URL,
    DefinedTerm,
    Number,
    Integer,
)


# base imports
from .thing import Thing


@register_model
class Place(Thing):
    """Entities that have a somewhat fixed physical extension"""

    additionalProperty: Optional[Union[str, List[str]]] = Field(
        None,
        description="A property value pair representing an additional characteristic of the entity e g a product feature or another characteristic for which there is no matching property in schema org Note Publishers should be aware that applications designed to use specific schema org properties e g https schema org width https schema org color https schema org gtin13 will typically expect such data to be provided using those properties rather than using the generic property value mechanism",
    )
    address: Optional[Union["PostalAddress", str, List["PostalAddress"], List[str]]] = (
        Field(None, description="Physical address of the item")
    )
    aggregateRating: Optional[
        Union["AggregateRating", str, List["AggregateRating"], List[str]]
    ] = Field(
        None,
        description="The overall rating based on a collection of reviews or ratings of the item",
    )
    amenityFeature: Optional[
        Union[
            "LocationFeatureSpecification",
            str,
            List["LocationFeatureSpecification"],
            List[str],
        ]
    ] = Field(
        None,
        description="An amenity feature e g a characteristic or service of the Accommodation This generic property does not make a statement about whether the feature is included in an offer for the main accommodation or available at extra costs",
    )
    branchCode: Optional[Union[str, List[str]]] = Field(
        None,
        description="A short textual code also called store code that uniquely identifies a place of business The code is typically assigned by the parentOrganization and used in structured URLs For example in the URL http www starbucks co uk store locator etc detail 3047 the code 3047 is a branchCode for a particular branch",
    )
    containedInPlace: Optional[Union["Place", str, List["Place"], List[str]]] = Field(
        None,
        description="The basic containment relation between a place and one that contains it Supersedes containedIn Inverse property containsPlace",
    )
    containsPlace: Optional[Union["Place", str, List["Place"], List[str]]] = Field(
        None,
        description="The basic containment relation between a place and another that it contains Inverse property containedInPlace",
    )
    event: Optional[Union[str, List[str]]] = Field(
        None,
        description="Upcoming or past event associated with this place organization or action Supersedes events",
    )
    faxNumber: Optional[Union[int, str, List[int], List[str]]] = Field(
        None, description="The fax number"
    )
    geo: Optional[
        Union[
            "GeoCoordinates",
            "GeoShape",
            str,
            List["GeoCoordinates"],
            List["GeoShape"],
            List[str],
        ]
    ] = Field(None, description="The geo coordinates of the place")
    geoContains: Optional[
        Union[
            "GeospatialGeometry",
            "Place",
            str,
            List["GeospatialGeometry"],
            List["Place"],
            List[str],
        ]
    ] = Field(
        None,
        description="Represents a relationship between two geometries or the places they represent relating a containing geometry to a contained geometry a contains b iff no points of b lie in the exterior of a and at least one point of the interior of b lies in the interior of a As defined in DE 9IM",
    )
    geoCoveredBy: Optional[
        Union[
            "GeospatialGeometry",
            "Place",
            str,
            List["GeospatialGeometry"],
            List["Place"],
            List[str],
        ]
    ] = Field(
        None,
        description="Represents a relationship between two geometries or the places they represent relating a geometry to another that covers it As defined in DE 9IM",
    )
    geoCovers: Optional[
        Union[
            "GeospatialGeometry",
            "Place",
            str,
            List["GeospatialGeometry"],
            List["Place"],
            List[str],
        ]
    ] = Field(
        None,
        description="Represents a relationship between two geometries or the places they represent relating a covering geometry to a covered geometry Every point of b is a point of the interior or boundary of a As defined in DE 9IM",
    )
    geoCrosses: Optional[
        Union[
            "GeospatialGeometry",
            "Place",
            str,
            List["GeospatialGeometry"],
            List["Place"],
            List[str],
        ]
    ] = Field(
        None,
        description="Represents a relationship between two geometries or the places they represent relating a geometry to another that crosses it a crosses b they have some but not all interior points in common and the dimension of the intersection is less than that of at least one of them As defined in DE 9IM",
    )
    geoDisjoint: Optional[
        Union[
            "GeospatialGeometry",
            "Place",
            str,
            List["GeospatialGeometry"],
            List["Place"],
            List[str],
        ]
    ] = Field(
        None,
        description="Represents spatial relations in which two geometries or the places they represent are topologically disjoint they have no point in common They form a set of disconnected geometries A symmetric relationship as defined in DE 9IM",
    )
    geoEquals: Optional[
        Union[
            "GeospatialGeometry",
            "Place",
            str,
            List["GeospatialGeometry"],
            List["Place"],
            List[str],
        ]
    ] = Field(
        None,
        description="Represents spatial relations in which two geometries or the places they represent are topologically equal as defined in DE 9IM Two geometries are topologically equal if their interiors intersect and no part of the interior or boundary of one geometry intersects the exterior of the other a symmetric relationship",
    )
    geoIntersects: Optional[
        Union[
            "GeospatialGeometry",
            "Place",
            str,
            List["GeospatialGeometry"],
            List["Place"],
            List[str],
        ]
    ] = Field(
        None,
        description="Represents spatial relations in which two geometries or the places they represent have at least one point in common As defined in DE 9IM",
    )
    geoOverlaps: Optional[
        Union[
            "GeospatialGeometry",
            "Place",
            str,
            List["GeospatialGeometry"],
            List["Place"],
            List[str],
        ]
    ] = Field(
        None,
        description="Represents a relationship between two geometries or the places they represent relating a geometry to another that geospatially overlaps it i e they have some but not all points in common As defined in DE 9IM",
    )
    geoTouches: Optional[
        Union[
            "GeospatialGeometry",
            "Place",
            str,
            List["GeospatialGeometry"],
            List["Place"],
            List[str],
        ]
    ] = Field(
        None,
        description="Represents spatial relations in which two geometries or the places they represent touch they have at least one boundary point in common but no interior points A symmetric relationship as defined in DE 9IM",
    )
    geoWithin: Optional[
        Union[
            "GeospatialGeometry",
            "Place",
            str,
            List["GeospatialGeometry"],
            List["Place"],
            List[str],
        ]
    ] = Field(
        None,
        description="Represents a relationship between two geometries or the places they represent relating a geometry to one that contains it i e it is inside i e within its interior As defined in DE 9IM",
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
    hasDriveThroughService: Optional[Union["bool", List["bool"]]] = Field(
        None,
        description="Indicates whether some facility e g FoodEstablishment CovidTestingFacility offers a service that can be used by driving through in a car In the case of CovidTestingFacility such facilities could potentially help with social distancing from other potentially infected users",
    )
    hasGS1DigitalLink: Optional[Union[str, List[str]]] = Field(
        None,
        description="The GS1 digital link associated with the object This URL should conform to the particular requirements of digital links The link should only contain the Application Identifiers AIs that are relevant for the entity being annotated for instance a Product or an Organization and for the correct granularity In particular for products A Digital Link that contains a serial number AI 21 should only be present on instances of IndividualProductA Digital Link that contains a lot number AI 10 should be annotated as SomeProduct if only products from that lot are sold or IndividualProduct if there is only a specific product A Digital Link that contains a global model number AI 8013 should be attached to a Product or a ProductModel Other item types should be adapted similarly",
    )
    hasMap: Optional[Union["Map", str, List["Map"], List[str]]] = Field(
        None, description="A URL to a map of the place Supersedes map maps"
    )
    isAccessibleForFree: Optional[Union["bool", List["bool"]]] = Field(
        None,
        description="A flag to signal that the item event or place is accessible for free Supersedes free",
    )
    isicV4: Optional[Union[str, List[str]]] = Field(
        None,
        description="The International Standard of Industrial Classification of All Economic Activities ISIC Revision 4 code for a particular organization business person or place",
    )
    keywords: Optional[Union[str, List[str]]] = Field(
        None,
        description="Keywords or tags used to describe some item Multiple textual entries in a keywords list are typically delimited by commas or by repeating the property",
    )
    latitude: Optional[Union[float, str, List[float], List[str]]] = Field(
        None, description="The latitude of a location For example 37 42242 WGS 84"
    )
    logo: Optional[Union["ImageObject", str, List["ImageObject"], List[str]]] = Field(
        None, description="An associated logo"
    )
    longitude: Optional[Union[float, str, List[float], List[str]]] = Field(
        None, description="The longitude of a location For example 122 08585 WGS 84"
    )
    maximumAttendeeCapacity: Optional[Union[int, List[int]]] = Field(
        None,
        description="The total number of individuals that may attend an event or venue",
    )
    openingHoursSpecification: Optional[
        Union[
            "OpeningHoursSpecification",
            str,
            List["OpeningHoursSpecification"],
            List[str],
        ]
    ] = Field(None, description="The opening hours of a certain place")
    photo: Optional[
        Union[
            "ImageObject",
            "Photograph",
            str,
            List["ImageObject"],
            List["Photograph"],
            List[str],
        ]
    ] = Field(None, description="A photograph of this place Supersedes photos")
    publicAccess: Optional[Union["bool", List["bool"]]] = Field(
        None,
        description="A flag to signal that the Place is open to public visitors If this property is omitted there is no assumed default boolean value",
    )
    review: Optional[Union["Review", str, List["Review"], List[str]]] = Field(
        None, description="A review of the item Supersedes reviews"
    )
    slogan: Optional[Union[str, List[str]]] = Field(
        None, description="A slogan or motto associated with the item"
    )
    smokingAllowed: Optional[Union["bool", List["bool"]]] = Field(
        None,
        description="Indicates whether it is allowed to smoke in the place e g in the restaurant hotel or hotel room",
    )
    specialOpeningHoursSpecification: Optional[
        Union[
            "OpeningHoursSpecification",
            str,
            List["OpeningHoursSpecification"],
            List[str],
        ]
    ] = Field(
        None,
        description="The special opening hours of a certain place Use this to explicitly override general opening hours brought in scope by openingHoursSpecification or openingHours",
    )
    telephone: Optional[Union[str, List[str]]] = Field(
        None, description="The telephone number"
    )
    tourBookingPage: Optional[Union[str, List[str]]] = Field(
        None,
        description="A page providing information on how to book a tour of some Place such as an Accommodation or ApartmentComplex in a real estate setting as well as other kinds of tours as appropriate",
    )


# parent dependences
model_dependence("Place", "Thing")


# attribute dependences
model_dependence(
    "Place",
    "AggregateRating",
    "Certification",
    "GeoCoordinates",
    "GeoShape",
    "GeospatialGeometry",
    "ImageObject",
    "LocationFeatureSpecification",
    "Map",
    "OpeningHoursSpecification",
    "Photograph",
    "PostalAddress",
    "Review",
)
