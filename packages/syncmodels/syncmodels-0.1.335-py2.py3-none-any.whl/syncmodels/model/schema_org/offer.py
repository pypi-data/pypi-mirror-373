# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import (
    Text,
    PropertyValue,
    URL,
    Date,
    DateTime,
    Time,
    BusinessEntityType,
    AdultOrientedEnumeration,
    Boolean,
    Event,
    Number,
)


# base imports
from .intangible import Intangible


@register_model
class Offer(Intangible):
    """An offer to transfer some rights to an item or to provide a service â for example an offer to sell tickets to an event to rent the DVD of a movie to stream a TV show over the internet to repair a motorcycle or to loan a book Note As the businessFunction property which identifies the form of offer e g sell lease repair dispose defaults to http purl org goodrelations v1 Sell an Offer without a defined businessFunction value can be assumed to be an offer to sell For GTIN related fields see Check Digit calculator and validation guide from GS1"""

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
    addOn: Optional[Union["Offer", str, List["Offer"], List[str]]] = Field(
        None,
        description="An additional offer that can only be obtained in combination with the first base offer e g supplements and extensions that are available for a surcharge",
    )
    additionalProperty: Optional[Union[str, List[str]]] = Field(
        None,
        description="A property value pair representing an additional characteristic of the entity e g a product feature or another characteristic for which there is no matching property in schema org Note Publishers should be aware that applications designed to use specific schema org properties e g https schema org width https schema org color https schema org gtin13 will typically expect such data to be provided using those properties rather than using the generic property value mechanism",
    )
    advanceBookingRequirement: Optional[
        Union["QuantitativeValue", str, List["QuantitativeValue"], List[str]]
    ] = Field(
        None,
        description="The amount of time that is required between accepting the offer and the actual usage of the resource or service",
    )
    aggregateRating: Optional[
        Union["AggregateRating", str, List["AggregateRating"], List[str]]
    ] = Field(
        None,
        description="The overall rating based on a collection of reviews or ratings of the item",
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
    asin: Optional[Union[str, List[str]]] = Field(
        None,
        description="An Amazon Standard Identification Number ASIN is a 10 character alphanumeric unique identifier assigned by Amazon com and its partners for product identification within the Amazon organization summary from Wikipedia s article Note also that this is a definition for how to include ASINs in Schema org data and not a definition of ASINs in general see documentation from Amazon for authoritative details ASINs are most commonly encoded as text strings but the asin property supports URL URI as potential values too",
    )
    availability: Optional[
        Union["ItemAvailability", str, List["ItemAvailability"], List[str]]
    ] = Field(
        None,
        description="The availability of this item for example In stock Out of stock Pre order etc",
    )
    availabilityEnds: Optional[Union[str, List[str]]] = Field(
        None,
        description="The end of the availability of the product or service included in the offer",
    )
    availabilityStarts: Optional[Union[str, List[str]]] = Field(
        None,
        description="The beginning of the availability of the product or service included in the offer",
    )
    availableAtOrFrom: Optional[Union["Place", str, List["Place"], List[str]]] = Field(
        None,
        description="The place s from which the offer can be obtained e g store locations",
    )
    availableDeliveryMethod: Optional[
        Union["DeliveryMethod", str, List["DeliveryMethod"], List[str]]
    ] = Field(None, description="The delivery method s available for this offer")
    businessFunction: Optional[
        Union["BusinessFunction", str, List["BusinessFunction"], List[str]]
    ] = Field(
        None,
        description="The business function e g sell lease repair dispose of the offer or component of a bundle TypeAndQuantityNode The default is http purl org goodrelations v1 Sell",
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
    checkoutPageURLTemplate: Optional[Union[str, List[str]]] = Field(
        None,
        description="A URL template RFC 6570 for a checkout page for an offer This approach allows merchants to specify a URL for online checkout of the offered product by interpolating parameters such as the logged in user ID product ID quantity discount code etc Parameter naming and standardization are not specified here",
    )
    deliveryLeadTime: Optional[
        Union["QuantitativeValue", str, List["QuantitativeValue"], List[str]]
    ] = Field(
        None,
        description="The typical delay between the receipt of the order and the goods either leaving the warehouse or being prepared for pickup in case the delivery method is on site pickup",
    )
    eligibleCustomerType: Optional[Union[str, List[str]]] = Field(
        None, description="The type s of customers for which the given offer is valid"
    )
    eligibleDuration: Optional[
        Union["QuantitativeValue", str, List["QuantitativeValue"], List[str]]
    ] = Field(None, description="The duration for which the given offer is valid")
    eligibleQuantity: Optional[
        Union["QuantitativeValue", str, List["QuantitativeValue"], List[str]]
    ] = Field(
        None,
        description="The interval and unit of measurement of ordering quantities for which the offer or price specification is valid This allows e g specifying that a certain freight charge is valid only for a certain quantity",
    )
    eligibleRegion: Optional[
        Union["GeoShape", "Place", str, List["GeoShape"], List["Place"], List[str]]
    ] = Field(
        None,
        description="The ISO 3166 1 ISO 3166 1 alpha 2 or ISO 3166 2 code the place or the GeoShape for the geo political region s for which the offer or delivery charge specification is valid See also ineligibleRegion",
    )
    eligibleTransactionVolume: Optional[
        Union["PriceSpecification", str, List["PriceSpecification"], List[str]]
    ] = Field(
        None,
        description="The transaction volume in a monetary unit for which the offer or price specification is valid e g for indicating a minimal purchasing volume to express free shipping above a certain order volume or to limit the acceptance of credit cards to purchases to a certain minimal amount",
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
    includesObject: Optional[
        Union["TypeAndQuantityNode", str, List["TypeAndQuantityNode"], List[str]]
    ] = Field(
        None,
        description="This links to a node or nodes indicating the exact quantity of the products included in an Offer or ProductCollection",
    )
    ineligibleRegion: Optional[
        Union["GeoShape", "Place", str, List["GeoShape"], List["Place"], List[str]]
    ] = Field(
        None,
        description="The ISO 3166 1 ISO 3166 1 alpha 2 or ISO 3166 2 code the place or the GeoShape for the geo political region s for which the offer or delivery charge specification is not valid e g a region where the transaction is not allowed See also eligibleRegion",
    )
    inventoryLevel: Optional[
        Union["QuantitativeValue", str, List["QuantitativeValue"], List[str]]
    ] = Field(
        None,
        description="The current approximate inventory level for the item or items",
    )
    isFamilyFriendly: Optional[Union["bool", List["bool"]]] = Field(
        None, description="Indicates whether this content is family friendly"
    )
    itemCondition: Optional[
        Union["OfferItemCondition", str, List["OfferItemCondition"], List[str]]
    ] = Field(
        None,
        description="A predefined value from OfferItemCondition specifying the condition of the product or service or the products or services included in the offer Also used for product return policies to specify the condition of products accepted for returns",
    )
    itemOffered: Optional[
        Union[
            "AggregateOffer",
            "CreativeWork",
            "MenuItem",
            "Product",
            "Service",
            "Trip",
            str,
            List["AggregateOffer"],
            List["CreativeWork"],
            List["MenuItem"],
            List["Product"],
            List["Service"],
            List["Trip"],
            List[str],
        ]
    ] = Field(
        None,
        description="An item being offered or demanded The transactional nature of the offer or demand is documented using businessFunction e g sell lease etc While several common expected types are listed explicitly in this definition others can be used Using a second type such as Product or a subtype of Product can clarify the nature of the offer Inverse property offers",
    )
    leaseLength: Optional[
        Union[
            "Duration",
            "QuantitativeValue",
            str,
            List["Duration"],
            List["QuantitativeValue"],
            List[str],
        ]
    ] = Field(
        None,
        description="Length of the lease for some Accommodation either particular to some Offer or in some cases intrinsic to the property",
    )
    mobileUrl: Optional[Union[str, List[str]]] = Field(
        None,
        description="The mobileUrl property is provided for specific situations in which data consumers need to determine whether one of several provided URLs is a dedicated mobile site To discourage over use and reflecting intial usecases the property is expected only on Product and Offer rather than Thing The general trend in web technology is towards responsive design in which content can be flexibly adapted to a wide range of browsing environments Pages and sites referenced with the long established url property should ideally also be usable on a wide variety of devices including mobile phones In most cases it would be pointless and counter productive to attempt to update all url markup to use mobileUrl for more mobile oriented pages The property is intended for the case when items primarily Product and Offer have extra URLs hosted on an additional mobile site alongside the main one It should not be taken as an endorsement of this publication style",
    )
    mpn: Optional[Union[str, List[str]]] = Field(
        None,
        description="The Manufacturer Part Number MPN of the product or the product to which the offer refers",
    )
    offeredBy: Optional[
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
        description="A pointer to the organization or person making the offer Inverse property makesOffer",
    )
    price: Optional[Union[float, List[float]]] = Field(
        None,
        description="The offer price of a product or of a price component when attached to PriceSpecification and its subtypes Usage guidelines Use the priceCurrency property with standard formats ISO 4217 currency format e g USD Ticker symbol for cryptocurrencies e g BTC well known names for Local Exchange Trading Systems LETS and other currency types e g Ithaca HOUR instead of including ambiguous symbols such as in the value Use Unicode FULL STOP U 002E rather than to indicate a decimal point Avoid using these symbols as a readability separator Note that both RDFa and Microdata syntax allow the use of a content attribute for publishing simple machine readable values alongside more human friendly formatting Use values from 0123456789 Unicode DIGIT ZERO U 0030 to DIGIT NINE U 0039 rather than superficially similar Unicode symbols",
    )
    priceCurrency: Optional[Union[str, List[str]]] = Field(
        None,
        description="The currency of the price or a price component when attached to PriceSpecification and its subtypes Use standard formats ISO 4217 currency format e g USD Ticker symbol for cryptocurrencies e g BTC well known names for Local Exchange Trading Systems LETS and other currency types e g Ithaca HOUR",
    )
    priceSpecification: Optional[
        Union["PriceSpecification", str, List["PriceSpecification"], List[str]]
    ] = Field(
        None,
        description="One or more detailed price specifications indicating the unit price and delivery or payment charges",
    )
    priceValidUntil: Optional[Union[str, List[str]]] = Field(
        None, description="The date after which the price is no longer available"
    )
    review: Optional[Union["Review", str, List["Review"], List[str]]] = Field(
        None, description="A review of the item Supersedes reviews"
    )
    seller: Optional[
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
        description="An entity which offers sells leases lends loans the services goods A seller may also be a provider Supersedes merchant vendor",
    )
    serialNumber: Optional[Union[int, str, List[int], List[str]]] = Field(
        None,
        description="The serial number or any alphanumeric identifier of a particular product When attached to an offer it is a shortcut for the serial number of the product included in the offer",
    )
    shippingDetails: Optional[
        Union["OfferShippingDetails", str, List["OfferShippingDetails"], List[str]]
    ] = Field(
        None,
        description="Indicates information about the shipping policies and options associated with an Offer",
    )
    sku: Optional[Union[int, str, List[int], List[str]]] = Field(
        None,
        description="The Stock Keeping Unit SKU i e a merchant specific identifier for a product or service or the product to which the offer refers",
    )
    validForMemberTier: Optional[
        Union["MemberProgramTier", str, List["MemberProgramTier"], List[str]]
    ] = Field(
        None,
        description="The membership program tier an Offer or a PriceSpecification OfferShippingDetails or MerchantReturnPolicy under an Offer is valid for",
    )
    validFrom: Optional[Union[str, List[str]]] = Field(
        None, description="The date when the item becomes valid"
    )
    validThrough: Optional[Union[str, List[str]]] = Field(
        None,
        description="The date after when the item is not valid For example the end of an offer salary period or a period of opening hours",
    )
    warranty: Optional[
        Union["WarrantyPromise", str, List["WarrantyPromise"], List[str]]
    ] = Field(
        None,
        description="The warranty promise s included in the offer Supersedes warrantyPromise",
    )


# parent dependences
model_dependence("Offer", "Intangible")


# attribute dependences
model_dependence(
    "Offer",
    "AdministrativeArea",
    "AggregateOffer",
    "AggregateRating",
    "BusinessFunction",
    "CategoryCode",
    "CreativeWork",
    "DeliveryMethod",
    "Duration",
    "GeoShape",
    "ItemAvailability",
    "LoanOrCredit",
    "MemberProgramTier",
    "MenuItem",
    "MerchantReturnPolicy",
    "OfferItemCondition",
    "OfferShippingDetails",
    "Organization",
    "PaymentMethod",
    "Person",
    "PhysicalActivityCategory",
    "Place",
    "PriceSpecification",
    "Product",
    "QuantitativeValue",
    "Review",
    "Service",
    "Thing",
    "Trip",
    "TypeAndQuantityNode",
    "WarrantyPromise",
)
