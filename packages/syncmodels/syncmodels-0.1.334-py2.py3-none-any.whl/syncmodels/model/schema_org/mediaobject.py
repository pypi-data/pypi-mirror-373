# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Text, URL, DateTime, Time, Boolean, Date


# base imports
from .creativework import CreativeWork


@register_model
class MediaObject(CreativeWork):
    """A media object such as an image video audio or text object embedded in a web page or a downloadable dataset i e DataDownload Note that a creative work may have many media objects associated with it on the same web page For example a page about a single song MusicRecording may have a music video VideoObject and a high and low bandwidth audio stream 2 AudioObject s"""

    associatedArticle: Optional[
        Union["NewsArticle", str, List["NewsArticle"], List[str]]
    ] = Field(None, description="A NewsArticle associated with the Media Object")
    bitrate: Optional[Union[str, List[str]]] = Field(
        None, description="The bitrate of the media object"
    )
    contentSize: Optional[Union[str, List[str]]] = Field(
        None, description="File size in mega kilo bytes"
    )
    contentUrl: Optional[Union[str, List[str]]] = Field(
        None,
        description="Actual bytes of the media object for example the image file or video file",
    )
    duration: Optional[Union["Duration", str, List["Duration"], List[str]]] = Field(
        None,
        description="The duration of the item movie audio recording event etc in ISO 8601 duration format",
    )
    embedUrl: Optional[Union[str, List[str]]] = Field(
        None,
        description="A URL pointing to a player for a specific video In general this is the information in the src element of an embed tag and should not be the same as the content of the loc tag",
    )
    encodesCreativeWork: Optional[
        Union["CreativeWork", str, List["CreativeWork"], List[str]]
    ] = Field(
        None,
        description="The CreativeWork encoded by this media object Inverse property encoding",
    )
    encodingFormat: Optional[Union[str, List[str]]] = Field(
        None,
        description="Media type typically expressed using a MIME format see IANA site and MDN reference e g application zip for a SoftwareApplication binary audio mpeg for mp3 etc In cases where a CreativeWork has several media type representations encoding can be used to indicate each MediaObject alongside particular encodingFormat information Unregistered or niche encoding and file formats can be indicated instead via the most appropriate URL e g defining Web page or a Wikipedia Wikidata entry Supersedes fileFormat",
    )
    endTime: Optional[Union[str, List[str]]] = Field(
        None,
        description="The endTime of something For a reserved event or service e g FoodEstablishmentReservation the time that it is expected to end For actions that span a period of time when the action was performed E g John wrote a book from January to December For media including audio and video it s the time offset of the end of a clip within a larger file Note that Event uses startDate endDate instead of startTime endTime even when describing dates with times This situation may be clarified in future revisions",
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
    ineligibleRegion: Optional[
        Union["GeoShape", "Place", str, List["GeoShape"], List["Place"], List[str]]
    ] = Field(
        None,
        description="The ISO 3166 1 ISO 3166 1 alpha 2 or ISO 3166 2 code the place or the GeoShape for the geo political region s for which the offer or delivery charge specification is not valid e g a region where the transaction is not allowed See also eligibleRegion",
    )
    interpretedAsClaim: Optional[Union["Claim", str, List["Claim"], List[str]]] = Field(
        None,
        description="Used to indicate a specific claim contained implied translated or refined from the content of a MediaObject or other CreativeWork The interpreting party can be indicated using claimInterpreter",
    )
    playerType: Optional[Union[str, List[str]]] = Field(
        None, description="Player type required for example Flash or Silverlight"
    )
    productionCompany: Optional[
        Union["Organization", str, List["Organization"], List[str]]
    ] = Field(
        None,
        description="The production company or studio responsible for the item e g series video game episode etc",
    )
    regionsAllowed: Optional[Union["Place", str, List["Place"], List[str]]] = Field(
        None,
        description="The regions where the media is allowed If not specified then it s assumed to be allowed everywhere Specify the countries in ISO 3166 format",
    )
    requiresSubscription: Optional[
        Union[
            "MediaSubscription",
            "bool",
            str,
            List["MediaSubscription"],
            List["bool"],
            List[str],
        ]
    ] = Field(
        None,
        description="Indicates if use of the media require a subscription either paid or free Allowed values are true or false note that an earlier version had yes no",
    )
    sha256: Optional[Union[str, List[str]]] = Field(
        None,
        description="The SHA 2 SHA256 hash of the content of the item For example a zero length input has value e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    )
    startTime: Optional[Union[str, List[str]]] = Field(
        None,
        description="The startTime of something For a reserved event or service e g FoodEstablishmentReservation the time that it is expected to start For actions that span a period of time when the action was performed E g John wrote a book from January to December For media including audio and video it s the time offset of the start of a clip within a larger file Note that Event uses startDate endDate instead of startTime endTime even when describing dates with times This situation may be clarified in future revisions",
    )
    uploadDate: Optional[Union[str, List[str]]] = Field(
        None,
        description="Date including time if available when this media object was uploaded to this site",
    )
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
model_dependence("MediaObject", "CreativeWork")


# attribute dependences
model_dependence(
    "MediaObject",
    "Claim",
    "CreativeWork",
    "Distance",
    "Duration",
    "GeoShape",
    "MediaSubscription",
    "NewsArticle",
    "Organization",
    "Place",
    "QuantitativeValue",
)
