# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Text, URL


# base imports
from .creativework import CreativeWork


@register_model
class SoftwareApplication(CreativeWork):
    """A software application"""

    applicationCategory: Optional[Union[str, List[str]]] = Field(
        None, description="Type of software application e g Game Multimedia"
    )
    applicationSubCategory: Optional[Union[str, List[str]]] = Field(
        None, description="Subcategory of the application e g Arcade Game"
    )
    applicationSuite: Optional[Union[str, List[str]]] = Field(
        None,
        description="The name of the application suite to which the application belongs e g Excel belongs to Office",
    )
    availableOnDevice: Optional[Union[str, List[str]]] = Field(
        None,
        description="Device required to run the application Used in cases where a specific make model is required to run the application Supersedes device",
    )
    countriesNotSupported: Optional[Union[str, List[str]]] = Field(
        None,
        description="Countries for which the application is not supported You can also provide the two letter ISO 3166 1 alpha 2 country code",
    )
    countriesSupported: Optional[Union[str, List[str]]] = Field(
        None,
        description="Countries for which the application is supported You can also provide the two letter ISO 3166 1 alpha 2 country code",
    )
    downloadUrl: Optional[Union[str, List[str]]] = Field(
        None, description="If the file can be downloaded URL to download the binary"
    )
    featureList: Optional[Union[str, List[str]]] = Field(
        None,
        description="Features or modules provided by this application and possibly required by other applications",
    )
    fileSize: Optional[Union[str, List[str]]] = Field(
        None,
        description="Size of the application package e g 18MB In the absence of a unit MB KB etc KB will be assumed",
    )
    installUrl: Optional[Union[str, List[str]]] = Field(
        None,
        description="URL at which the app may be installed if different from the URL of the item",
    )
    memoryRequirements: Optional[Union[str, List[str]]] = Field(
        None, description="Minimum memory requirements"
    )
    operatingSystem: Optional[Union[str, List[str]]] = Field(
        None, description="Operating systems supported Windows 7 OS X 10 6 Android 1 6"
    )
    permissions: Optional[Union[str, List[str]]] = Field(
        None,
        description="Permission s required to run the app for example a mobile app may require full internet access or may run only on wifi",
    )
    processorRequirements: Optional[Union[str, List[str]]] = Field(
        None,
        description="Processor architecture required to run the application e g IA64",
    )
    releaseNotes: Optional[Union[str, List[str]]] = Field(
        None, description="Description of what changed in this version"
    )
    screenshot: Optional[Union["ImageObject", str, List["ImageObject"], List[str]]] = (
        Field(None, description="A link to a screenshot image of the app")
    )
    softwareAddOn: Optional[
        Union["SoftwareApplication", str, List["SoftwareApplication"], List[str]]
    ] = Field(None, description="Additional content for a software application")
    softwareHelp: Optional[
        Union["CreativeWork", str, List["CreativeWork"], List[str]]
    ] = Field(None, description="Software application help")
    softwareRequirements: Optional[Union[str, List[str]]] = Field(
        None,
        description="Component dependency requirements for application This includes runtime environments and shared libraries that are not included in the application distribution package but required to run the application examples DirectX Java or NET runtime Supersedes requirements",
    )
    softwareVersion: Optional[Union[str, List[str]]] = Field(
        None, description="Version of the software instance"
    )
    storageRequirements: Optional[Union[str, List[str]]] = Field(
        None, description="Storage requirements free space required"
    )
    supportingData: Optional[Union["DataFeed", str, List["DataFeed"], List[str]]] = (
        Field(None, description="Supporting data for a SoftwareApplication")
    )


# parent dependences
model_dependence("SoftwareApplication", "CreativeWork")


# attribute dependences
model_dependence(
    "SoftwareApplication",
    "CreativeWork",
    "DataFeed",
    "ImageObject",
)
