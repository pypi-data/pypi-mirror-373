# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .intangible import Intangible


@register_model
class Language(Intangible):
    """Natural languages such as Spanish Tamil Hindi English etc Formal language code tags expressed in BCP 47 can be used via the alternateName property The Language type previously also covered programming languages such as Scheme and Lisp which are now best represented using ComputerLanguage"""


# parent dependences
model_dependence("Language", "Intangible")


# attribute dependences
model_dependence(
    "Language",
)
