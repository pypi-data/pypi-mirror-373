# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Text, URL


# base imports
from .intangible import Intangible


@register_model
class EntryPoint(Intangible):
    """An entry point within some Web based protocol"""

    actionApplication: Optional[
        Union["SoftwareApplication", str, List["SoftwareApplication"], List[str]]
    ] = Field(
        None,
        description="An application that can complete the request Supersedes application",
    )
    actionPlatform: Optional[
        Union[
            "DigitalPlatformEnumeration",
            str,
            List["DigitalPlatformEnumeration"],
            List[str],
        ]
    ] = Field(
        None,
        description="The high level platform s where the Action can be performed for the given URL To specify a specific application or operating system instance use actionApplication",
    )
    contentType: Optional[Union[str, List[str]]] = Field(
        None, description="The supported content type s for an EntryPoint response"
    )
    encodingType: Optional[Union[str, List[str]]] = Field(
        None, description="The supported encoding type s for an EntryPoint request"
    )
    httpMethod: Optional[Union[str, List[str]]] = Field(
        None,
        description="An HTTP method that specifies the appropriate HTTP method for a request to an HTTP EntryPoint Values are capitalized strings as used in HTTP",
    )
    urlTemplate: Optional[Union[str, List[str]]] = Field(
        None,
        description="An url template RFC6570 that will be used to construct the target of the execution of the action",
    )


# parent dependences
model_dependence("EntryPoint", "Intangible")


# attribute dependences
model_dependence(
    "EntryPoint",
    "DigitalPlatformEnumeration",
    "SoftwareApplication",
)
