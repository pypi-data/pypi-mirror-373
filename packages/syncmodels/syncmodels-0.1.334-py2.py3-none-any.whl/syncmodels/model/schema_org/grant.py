# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .intangible import Intangible


@register_model
class Grant(Intangible):
    """A grant typically financial or otherwise quantifiable of resources Typically a funder sponsors some MonetaryAmount to an Organization or Person sometimes not necessarily via a dedicated or long lived Project resulting in one or more outputs or fundedItems For financial sponsorship indicate the funder of a MonetaryGrant For non financial support indicate sponsor of Grants of resources e g office space Grants support activities directed towards some agreed collective goals often but not always organized as Projects Long lived projects are sometimes sponsored by a variety of grants over time but it is also common for a project to be associated with a single grant The amount of a Grant is represented using amount as a MonetaryAmount"""

    fundedItem: Optional[
        Union[
            "BioChemEntity",
            "CreativeWork",
            "Event",
            "MedicalEntity",
            "Organization",
            "Person",
            "Product",
        ]
    ] = Field(
        None,
        description="Indicates something directly or indirectly funded or sponsored through a Grant See also ownershipFundingInfo Inverse property funding",
    )
    funder: Optional[Union["Organization", "Person"]] = Field(
        None,
        description="A person or organization that supports sponsors something through some kind of financial contribution",
    )
    sponsor: Optional[Union["Organization", "Person"]] = Field(
        None,
        description="A person or organization that supports a thing through a pledge promise or financial contribution E g a sponsor of a Medical Study or a corporate sponsor of an event",
    )


# parent dependences
model_dependence("Grant", "Intangible")


# attribute dependences
model_dependence(
    "Grant",
    "BioChemEntity",
    "CreativeWork",
    "Event",
    "MedicalEntity",
    "Organization",
    "Person",
    "Product",
)
