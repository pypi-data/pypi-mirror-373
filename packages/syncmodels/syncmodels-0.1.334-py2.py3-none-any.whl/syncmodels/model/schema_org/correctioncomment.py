# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .comment import Comment


@register_model
class CorrectionComment(Comment):
    """A comment that corrects CreativeWork"""


# parent dependences
model_dependence("CorrectionComment", "Comment")


# attribute dependences
model_dependence(
    "CorrectionComment",
)
