# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import (
    PropertyValue,
    Text,
    URL,
    Grant,
    AdultOrientedEnumeration,
    Boolean,
    DefinedTerm,
    Date,
)


# base imports
from .thing import Thing


@register_model
class Product(Thing):
    """Any offered product or service For example a pair of shoes a concert ticket the rental of a car a haircut or an episode of a TV show streamed online"""

    additionalProperty: Optional[Union[str, List[str]]] = Field(
        None,
        description="A property value pair representing an additional characteristic of the entity e g a product feature or another characteristic for which there is no matching property in schema org Note Publishers should be aware that applications designed to use specific schema org properties e g https schema org width https schema org color https schema org gtin13 will typically expect such data to be provided using those properties rather than using the generic property value mechanism",
    )
    aggregateRating: Optional[
        Union["AggregateRating", str, List["AggregateRating"], List[str]]
    ] = Field(
        None,
        description="The overall rating based on a collection of reviews or ratings of the item",
    )
    asin: Optional[Union[str, List[str]]] = Field(
        None,
        description="An Amazon Standard Identification Number ASIN is a 10 character alphanumeric unique identifier assigned by Amazon com and its partners for product identification within the Amazon organization summary from Wikipedia s article Note also that this is a definition for how to include ASINs in Schema org data and not a definition of ASINs in general see documentation from Amazon for authoritative details ASINs are most commonly encoded as text strings but the asin property supports URL URI as potential values too",
    )
    audience: Optional[Union["Audience", str, List["Audience"], List[str]]] = Field(
        None,
        description="An intended audience i e a group for whom something was created Supersedes serviceAudience",
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
    category: Optional[
        Union[
            "CategoryCode",
            "PhysicalActivityCategory",
            "Thing",
            str,
            List["CategoryCode"],
            List["PhysicalActivityCategory"],
            List["Thing"],
            List[str],
        ]
    ] = Field(
        None,
        description="A category for the item Greater signs or slashes can be used to informally indicate a category hierarchy",
    )
    color: Optional[Union[str, List[str]]] = Field(
        None, description="The color of the product"
    )
    colorSwatch: Optional[Union["ImageObject", str, List["ImageObject"], List[str]]] = (
        Field(
            None,
            description="A color swatch image visualizing the color of a Product Should match the textual description specified in the color property This can be a URL or a fully described ImageObject",
        )
    )
    countryOfAssembly: Optional[Union[str, List[str]]] = Field(
        None, description="The place where the product was assembled"
    )
    countryOfLastProcessing: Optional[Union[str, List[str]]] = Field(
        None,
        description="The place where the item typically Product was last processed and tested before importation",
    )
    countryOfOrigin: Optional[Union["Country", str, List["Country"], List[str]]] = (
        Field(
            None,
            description="The country of origin of something including products as well as creative works such as movie and TV content In the case of TV and movie this would be the country of the principle offices of the production company or individual responsible for the movie For other kinds of CreativeWork it is difficult to provide fully general guidance and properties such as contentLocation and locationCreated may be more applicable In the case of products the country of origin of the product The exact interpretation of this may vary by context and product type and cannot be fully enumerated here",
        )
    )
    depth: Optional[
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
    ] = Field(None, description="The depth of the item")
    funding: Optional[Union[str, List[str]]] = Field(
        None,
        description="A Grant that directly or indirectly provide funding or sponsorship for this item See also ownershipFundingInfo Inverse property fundedItem",
    )
    gtin: Optional[Union[int, str, List[int], List[str]]] = Field(
        None,
        description="A Global Trade Item Number GTIN GTINs identify trade items including products and services using numeric identification codes A correct gtin value should be a valid GTIN which means that it should be an all numeric string of either 8 12 13 or 14 digits or a GS1 Digital Link URL based on such a string The numeric component should also have a valid GS1 check digit and meet the other rules for valid GTINs See also GS1 s GTIN Summary and Wikipedia for more details Left padding of the gtin values is not required or encouraged The gtin property generalizes the earlier gtin8 gtin12 gtin13 and gtin14 properties The GS1 digital link specifications expresses GTINs as URLs URIs IRIs etc Digital Links should be populated into the hasGS1DigitalLink attribute Note also that this is a definition for how to include GTINs in Schema org data and not a definition of GTINs in general see the GS1 documentation for authoritative details",
    )
    gtin12: Optional[Union[int, str, List[int], List[str]]] = Field(
        None,
        description="The GTIN 12 code of the product or the product to which the offer refers The GTIN 12 is the 12 digit GS1 Identification Key composed of a U P C Company Prefix Item Reference and Check Digit used to identify trade items See GS1 GTIN Summary for more details",
    )
    gtin13: Optional[Union[int, str, List[int], List[str]]] = Field(
        None,
        description="The GTIN 13 code of the product or the product to which the offer refers This is equivalent to 13 digit ISBN codes and EAN UCC 13 Former 12 digit UPC codes can be converted into a GTIN 13 code by simply adding a preceding zero See GS1 GTIN Summary for more details",
    )
    gtin14: Optional[Union[int, str, List[int], List[str]]] = Field(
        None,
        description="The GTIN 14 code of the product or the product to which the offer refers See GS1 GTIN Summary for more details",
    )
    gtin8: Optional[Union[int, str, List[int], List[str]]] = Field(
        None,
        description="The GTIN 8 code of the product or the product to which the offer refers This code is also known as EAN UCC 8 or 8 digit EAN See GS1 GTIN Summary for more details",
    )
    hasAdultConsideration: Optional[Union[str, List[str]]] = Field(
        None,
        description="Used to tag an item to be intended or suitable for consumption or use by adults only",
    )
    hasCertification: Optional[
        Union["Certification", str, List["Certification"], List[str]]
    ] = Field(
        None,
        description="Certification information about a product organization service place or person",
    )
    hasEnergyConsumptionDetails: Optional[
        Union[
            "EnergyConsumptionDetails", str, List["EnergyConsumptionDetails"], List[str]
        ]
    ] = Field(
        None,
        description="Defines the energy efficiency Category also known as class or rating for a product according to an international energy efficiency standard",
    )
    hasGS1DigitalLink: Optional[Union[str, List[str]]] = Field(
        None,
        description="The GS1 digital link associated with the object This URL should conform to the particular requirements of digital links The link should only contain the Application Identifiers AIs that are relevant for the entity being annotated for instance a Product or an Organization and for the correct granularity In particular for products A Digital Link that contains a serial number AI 21 should only be present on instances of IndividualProductA Digital Link that contains a lot number AI 10 should be annotated as SomeProduct if only products from that lot are sold or IndividualProduct if there is only a specific product A Digital Link that contains a global model number AI 8013 should be attached to a Product or a ProductModel Other item types should be adapted similarly",
    )
    hasMeasurement: Optional[
        Union["QuantitativeValue", str, List["QuantitativeValue"], List[str]]
    ] = Field(
        None,
        description="A measurement of an item For example the inseam of pants the wheel size of a bicycle the gauge of a screw or the carbon footprint measured for certification by an authority Usually an exact measurement but can also be a range of measurements for adjustable products for example belts and ski bindings",
    )
    hasMerchantReturnPolicy: Optional[
        Union["MerchantReturnPolicy", str, List["MerchantReturnPolicy"], List[str]]
    ] = Field(
        None,
        description="Specifies a MerchantReturnPolicy that may be applicable Supersedes hasProductReturnPolicy",
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
    inProductGroupWithID: Optional[Union[str, List[str]]] = Field(
        None,
        description="Indicates the productGroupID for a ProductGroup that this product isVariantOf",
    )
    isAccessoryOrSparePartFor: Optional[
        Union["Product", str, List["Product"], List[str]]
    ] = Field(
        None,
        description="A pointer to another product or multiple products for which this product is an accessory or spare part",
    )
    isConsumableFor: Optional[Union["Product", str, List["Product"], List[str]]] = (
        Field(
            None,
            description="A pointer to another product or multiple products for which this product is a consumable",
        )
    )
    isFamilyFriendly: Optional[Union["bool", List["bool"]]] = Field(
        None, description="Indicates whether this content is family friendly"
    )
    isRelatedTo: Optional[
        Union["Product", "Service", str, List["Product"], List["Service"], List[str]]
    ] = Field(
        None,
        description="A pointer to another somehow related product or multiple products",
    )
    isSimilarTo: Optional[
        Union["Product", "Service", str, List["Product"], List["Service"], List[str]]
    ] = Field(
        None,
        description="A pointer to another functionally similar product or multiple products",
    )
    isVariantOf: Optional[
        Union[
            "ProductGroup",
            "ProductModel",
            str,
            List["ProductGroup"],
            List["ProductModel"],
            List[str],
        ]
    ] = Field(
        None,
        description="Indicates the kind of product that this is a variant of In the case of ProductModel this is a pointer from a ProductModel to a base product from which this product is a variant It is safe to infer that the variant inherits all product features from the base model unless defined locally This is not transitive In the case of a ProductGroup the group description also serves as a template representing a set of Products that vary on explicitly defined specific dimensions only so it defines both a set of variants as well as which values distinguish amongst those variants When used with ProductGroup this property can apply to any Product included in the group Inverse property hasVariant",
    )
    itemCondition: Optional[
        Union["OfferItemCondition", str, List["OfferItemCondition"], List[str]]
    ] = Field(
        None,
        description="A predefined value from OfferItemCondition specifying the condition of the product or service or the products or services included in the offer Also used for product return policies to specify the condition of products accepted for returns",
    )
    keywords: Optional[Union[str, List[str]]] = Field(
        None,
        description="Keywords or tags used to describe some item Multiple textual entries in a keywords list are typically delimited by commas or by repeating the property",
    )
    logo: Optional[Union["ImageObject", str, List["ImageObject"], List[str]]] = Field(
        None, description="An associated logo"
    )
    manufacturer: Optional[
        Union["Organization", str, List["Organization"], List[str]]
    ] = Field(None, description="The manufacturer of the product")
    material: Optional[Union["Product", str, List["Product"], List[str]]] = Field(
        None,
        description="A material that something is made from e g leather wool cotton paper",
    )
    mobileUrl: Optional[Union[str, List[str]]] = Field(
        None,
        description="The mobileUrl property is provided for specific situations in which data consumers need to determine whether one of several provided URLs is a dedicated mobile site To discourage over use and reflecting intial usecases the property is expected only on Product and Offer rather than Thing The general trend in web technology is towards responsive design in which content can be flexibly adapted to a wide range of browsing environments Pages and sites referenced with the long established url property should ideally also be usable on a wide variety of devices including mobile phones In most cases it would be pointless and counter productive to attempt to update all url markup to use mobileUrl for more mobile oriented pages The property is intended for the case when items primarily Product and Offer have extra URLs hosted on an additional mobile site alongside the main one It should not be taken as an endorsement of this publication style",
    )
    model: Optional[Union["ProductModel", str, List["ProductModel"], List[str]]] = (
        Field(
            None,
            description="The model of the product Use with the URL of a ProductModel or a textual representation of the model identifier The URL of the ProductModel can be from an external source It is recommended to additionally provide strong product identifiers via the gtin8 gtin13 gtin14 and mpn properties",
        )
    )
    mpn: Optional[Union[str, List[str]]] = Field(
        None,
        description="The Manufacturer Part Number MPN of the product or the product to which the offer refers",
    )
    negativeNotes: Optional[
        Union[
            "ItemList",
            "ListItem",
            "WebContent",
            str,
            List["ItemList"],
            List["ListItem"],
            List["WebContent"],
            List[str],
        ]
    ] = Field(
        None,
        description="Provides negative considerations regarding something most typically in pro con lists for reviews alongside positiveNotes For symmetry In the case of a Review the property describes the itemReviewed from the perspective of the review in the case of a Product the product itself is being described Since product descriptions tend to emphasise positive claims it may be relatively unusual to find negativeNotes used in this way Nevertheless for the sake of symmetry negativeNotes can be used on Product The property values can be expressed either as unstructured text repeated as necessary or if ordered as a list in which case the most negative is at the beginning of the list",
    )
    nsn: Optional[Union[str, List[str]]] = Field(
        None, description="Indicates the NATO stock number nsn of a Product"
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
    positiveNotes: Optional[
        Union[
            "ItemList",
            "ListItem",
            "WebContent",
            str,
            List["ItemList"],
            List["ListItem"],
            List["WebContent"],
            List[str],
        ]
    ] = Field(
        None,
        description="Provides positive considerations regarding something for example product highlights or alongside negativeNotes pro con lists for reviews In the case of a Review the property describes the itemReviewed from the perspective of the review in the case of a Product the product itself is being described The property values can be expressed either as unstructured text repeated as necessary or if ordered as a list in which case the most positive is at the beginning of the list",
    )
    productID: Optional[Union[str, List[str]]] = Field(
        None,
        description="The product identifier such as ISBN For example meta itemprop productID content isbn 123 456 789",
    )
    productionDate: Optional[Union[str, List[str]]] = Field(
        None, description="The date of production of the item e g vehicle"
    )
    purchaseDate: Optional[Union[str, List[str]]] = Field(
        None,
        description="The date the item e g vehicle was purchased by the current owner",
    )
    releaseDate: Optional[Union[str, List[str]]] = Field(
        None,
        description="The release date of a product or product model This can be used to distinguish the exact variant of a product",
    )
    review: Optional[Union["Review", str, List["Review"], List[str]]] = Field(
        None, description="A review of the item Supersedes reviews"
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
    sku: Optional[Union[int, str, List[int], List[str]]] = Field(
        None,
        description="The Stock Keeping Unit SKU i e a merchant specific identifier for a product or service or the product to which the offer refers",
    )
    slogan: Optional[Union[str, List[str]]] = Field(
        None, description="A slogan or motto associated with the item"
    )
    weight: Optional[
        Union["QuantitativeValue", str, List["QuantitativeValue"], List[str]]
    ] = Field(None, description="The weight of the product or person")
    width: Optional[
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
    ] = Field(None, description="The width of the item")


# parent dependences
model_dependence("Product", "Thing")


# attribute dependences
model_dependence(
    "Product",
    "AggregateRating",
    "Audience",
    "Brand",
    "CategoryCode",
    "Certification",
    "Country",
    "Demand",
    "Distance",
    "EnergyConsumptionDetails",
    "ImageObject",
    "ItemList",
    "ListItem",
    "MerchantReturnPolicy",
    "Offer",
    "OfferItemCondition",
    "Organization",
    "PhysicalActivityCategory",
    "ProductGroup",
    "ProductModel",
    "QuantitativeValue",
    "Review",
    "Service",
    "SizeSpecification",
    "Thing",
    "WebContent",
)
