# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel

__all__ = ["YoutubeConfigurationDto"]


class YoutubeConfigurationDto(BaseModel):
    caption: Optional[object] = None
    """Overrides the `caption` from the post"""

    media: Optional[List[str]] = None
    """Overrides the `media` from the post"""

    title: Optional[str] = None
    """Overrides the `title` from the post"""
