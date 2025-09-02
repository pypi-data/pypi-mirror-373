# from __future__ import annotations

from pydantic import Field
from typing import Optional, Union, ForwardRef

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Text, URL, DateTime, Time, Boolean, Date


# base imports
from .mediaobject import MediaObject


@register_model
class TextObject(MediaObject):
    """A text file The text can be unformatted or contain markup html etc"""

    associatedArticle: Optional["NewsArticle"] = Field(
        None, description="A NewsArticle associated with the Media Object"
    )
    bitrate: Optional[Text] = Field(None, description="The bitrate of the media object")
    contentSize: Optional[Text] = Field(
        None, description="File size in mega kilo bytes"
    )
    contentUrl: Optional[URL] = Field(
        None,
        description="Actual bytes of the media object for example the image file or video file",
    )
    duration: Optional["Duration"] = Field(
        None,
        description="The duration of the item movie audio recording event etc in ISO 8601 duration format",
    )
    embedUrl: Optional[URL] = Field(
        None,
        description="A URL pointing to a player for a specific video In general this is the information in the src element of an embed tag and should not be the same as the content of the loc tag",
    )
    encodesCreativeWork: Optional["CreativeWork"] = Field(
        None,
        description="The CreativeWork encoded by this media object Inverse property encoding",
    )
    encodingFormat: Optional[Union[Text, URL]] = Field(
        None,
        description="Media type typically expressed using a MIME format see IANA site and MDN reference e g application zip for a SoftwareApplication binary audio mpeg for mp3 etc In cases where a CreativeWork has several media type representations encoding can be used to indicate each MediaObject alongside particular encodingFormat information Unregistered or niche encoding and file formats can be indicated instead via the most appropriate URL e g defining Web page or a Wikipedia Wikidata entry Supersedes fileFormat",
    )
    endTime: Optional[Union[DateTime, Time]] = Field(
        None,
        description="The endTime of something For a reserved event or service e g FoodEstablishmentReservation the time that it is expected to end For actions that span a period of time when the action was performed E g John wrote a book from January to December For media including audio and video it s the time offset of the end of a clip within a larger file Note that Event uses startDate endDate instead of startTime endTime even when describing dates with times This situation may be clarified in future revisions",
    )
    height: Optional[Union["Distance", "QuantitativeValue"]] = Field(
        None, description="The height of the item"
    )
    ineligibleRegion: Optional[Union["GeoShape", "Place", Text]] = Field(
        None,
        description="The ISO 3166 1 ISO 3166 1 alpha 2 or ISO 3166 2 code the place or the GeoShape for the geo political region s for which the offer or delivery charge specification is not valid e g a region where the transaction is not allowed See also eligibleRegion",
    )
    interpretedAsClaim: Optional["Claim"] = Field(
        None,
        description="Used to indicate a specific claim contained implied translated or refined from the content of a MediaObject or other CreativeWork The interpreting party can be indicated using claimInterpreter",
    )
    playerType: Optional[Text] = Field(
        None, description="Player type required for example Flash or Silverlight"
    )
    productionCompany: Optional["Organization"] = Field(
        None,
        description="The production company or studio responsible for the item e g series video game episode etc",
    )
    regionsAllowed: Optional["Place"] = Field(
        None,
        description="The regions where the media is allowed If not specified then it s assumed to be allowed everywhere Specify the countries in ISO 3166 format",
    )
    requiresSubscription: Optional[Union["MediaSubscription", Boolean]] = Field(
        None,
        description="Indicates if use of the media require a subscription either paid or free Allowed values are true or false note that an earlier version had yes no",
    )
    sha256: Optional[Text] = Field(
        None,
        description="The SHA 2 SHA256 hash of the content of the item For example a zero length input has value e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    )
    startTime: Optional[Union[DateTime, Time]] = Field(
        None,
        description="The startTime of something For a reserved event or service e g FoodEstablishmentReservation the time that it is expected to start For actions that span a period of time when the action was performed E g John wrote a book from January to December For media including audio and video it s the time offset of the start of a clip within a larger file Note that Event uses startDate endDate instead of startTime endTime even when describing dates with times This situation may be clarified in future revisions",
    )
    uploadDate: Optional[Union[Date, DateTime]] = Field(
        None,
        description="Date including time if available when this media object was uploaded to this site",
    )
    width: Optional[Union["Distance", "QuantitativeValue"]] = Field(
        None, description="The width of the item"
    )


# attribute dependences
model_dependence(
    "TextObject",
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
