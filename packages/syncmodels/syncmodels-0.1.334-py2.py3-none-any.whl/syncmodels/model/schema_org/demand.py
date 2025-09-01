# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Text, URL, Date, DateTime, Time, BusinessEntityType, Event


# base imports
from .intangible import Intangible


@register_model
class Demand(Intangible):
    """A demand entity represents the public not necessarily binding not necessarily exclusive announcement by an organization or person to seek a certain type of goods or services For describing demand using this type the very same properties used for Offer apply"""

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
    advanceBookingRequirement: Optional[
        Union["QuantitativeValue", str, List["QuantitativeValue"], List[str]]
    ] = Field(
        None,
        description="The amount of time that is required between accepting the offer and the actual usage of the resource or service",
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
    mpn: Optional[Union[str, List[str]]] = Field(
        None,
        description="The Manufacturer Part Number MPN of the product or the product to which the offer refers",
    )
    priceSpecification: Optional[
        Union["PriceSpecification", str, List["PriceSpecification"], List[str]]
    ] = Field(
        None,
        description="One or more detailed price specifications indicating the unit price and delivery or payment charges",
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
        description="An entity which offers sells leases lends loans the services goods A seller may also be a provider Supersedes vendor merchant",
    )
    serialNumber: Optional[Union[int, str, List[int], List[str]]] = Field(
        None,
        description="The serial number or any alphanumeric identifier of a particular product When attached to an offer it is a shortcut for the serial number of the product included in the offer",
    )
    sku: Optional[Union[int, str, List[int], List[str]]] = Field(
        None,
        description="The Stock Keeping Unit SKU i e a merchant specific identifier for a product or service or the product to which the offer refers",
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
model_dependence("Demand", "Intangible")


# attribute dependences
model_dependence(
    "Demand",
    "AdministrativeArea",
    "AggregateOffer",
    "BusinessFunction",
    "CreativeWork",
    "DeliveryMethod",
    "GeoShape",
    "ItemAvailability",
    "LoanOrCredit",
    "MenuItem",
    "OfferItemCondition",
    "Organization",
    "PaymentMethod",
    "Person",
    "Place",
    "PriceSpecification",
    "Product",
    "QuantitativeValue",
    "Service",
    "Trip",
    "TypeAndQuantityNode",
    "WarrantyPromise",
)
