# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["InstagramConfigurationDto"]


class InstagramConfigurationDto(BaseModel):
    caption: Optional[object] = None
    """Overrides the `caption` from the post"""

    collaborators: Optional[List[str]] = None
    """Instagram usernames to be tagged as a collaborator"""

    media: Optional[List[str]] = None
    """Overrides the `media` from the post"""

    placement: Optional[Literal["reels", "stories", "timeline"]] = None
    """Instagram post placement"""
