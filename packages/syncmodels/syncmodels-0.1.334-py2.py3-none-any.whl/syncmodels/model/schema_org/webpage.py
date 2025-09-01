# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Text, Date, URL


# base imports
from .creativework import CreativeWork


@register_model
class WebPage(CreativeWork):
    """A web page Every web page is implicitly assumed to be declared to be of type WebPage so the various properties about that webpage such as breadcrumb may be used We recommend explicit declaration if these properties are specified but if they are found outside of an itemscope they will be assumed to be about the page"""

    breadcrumb: Optional[
        Union["BreadcrumbList", str, List["BreadcrumbList"], List[str]]
    ] = Field(
        None,
        description="A set of links that can help a user understand and navigate a website hierarchy",
    )
    lastReviewed: Optional[Union[str, List[str]]] = Field(
        None,
        description="Date on which the content on this web page was last reviewed for accuracy and or completeness",
    )
    mainContentOfPage: Optional[
        Union["WebPageElement", str, List["WebPageElement"], List[str]]
    ] = Field(
        None,
        description="Indicates if this web page element is the main subject of the page Supersedes aspect",
    )
    primaryImageOfPage: Optional[
        Union["ImageObject", str, List["ImageObject"], List[str]]
    ] = Field(None, description="Indicates the main image on the page")
    relatedLink: Optional[Union[str, List[str]]] = Field(
        None,
        description="A link related to this web page for example to other related web pages",
    )
    reviewedBy: Optional[
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
        description="People or organizations that have reviewed the content on this web page for accuracy and or completeness",
    )
    significantLink: Optional[Union[str, List[str]]] = Field(
        None,
        description="One of the more significant URLs on the page Typically these are the non navigation links that are clicked on the most Supersedes significantLinks",
    )
    speakable: Optional[
        Union["SpeakableSpecification", str, List["SpeakableSpecification"], List[str]]
    ] = Field(
        None,
        description="Indicates sections of a Web page that are particularly speakable in the sense of being highlighted as being especially appropriate for text to speech conversion Other sections of a page may also be usefully spoken in particular circumstances the speakable property serves to indicate the parts most likely to be generally useful for speech The speakable property can be repeated an arbitrary number of times with three kinds of possible content locator values 1 id value URL references uses id value of an element in the page being annotated The simplest use of speakable has potentially relative URL values referencing identified sections of the document concerned 2 CSS Selectors addresses content in the annotated page e g via class attribute Use the cssSelector property 3 XPaths addresses content via XPaths assuming an XML view of the content Use the xpath property For more sophisticated markup of speakable sections beyond simple ID references either CSS selectors or XPath expressions to pick out document section s as speakable For this we define a supporting type SpeakableSpecification which is defined to be a possible value of the speakable property",
    )
    specialty: Optional[Union["Specialty", str, List["Specialty"], List[str]]] = Field(
        None,
        description="One of the domain specialities to which this web page s content applies",
    )


# parent dependences
model_dependence("WebPage", "CreativeWork")


# attribute dependences
model_dependence(
    "WebPage",
    "BreadcrumbList",
    "ImageObject",
    "Organization",
    "Person",
    "SpeakableSpecification",
    "Specialty",
    "WebPageElement",
)
