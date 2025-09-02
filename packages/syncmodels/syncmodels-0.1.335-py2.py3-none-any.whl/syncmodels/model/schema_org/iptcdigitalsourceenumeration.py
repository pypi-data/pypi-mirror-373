# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .mediaenumeration import MediaEnumeration


@register_model
class IPTCDigitalSourceEnumeration(MediaEnumeration):
    """IPTC Digital Source codes for use with the digitalSourceType property providing information about the source for a digital media object In general these codes are not declared here to be mutually exclusive although some combinations would be contradictory if applied simultaneously or might be considered mutually incompatible by upstream maintainers of the definitions See the IPTC documentation for detailed definitions of all terms"""


# parent dependences
model_dependence("IPTCDigitalSourceEnumeration", "MediaEnumeration")


# attribute dependences
model_dependence(
    "IPTCDigitalSourceEnumeration",
)
