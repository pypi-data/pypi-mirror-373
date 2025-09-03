# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel

__all__ = ["BlueskyConfigurationDto"]


class BlueskyConfigurationDto(BaseModel):
    caption: Optional[object] = None
    """Overrides the `caption` from the post"""

    media: Optional[List[str]] = None
    """Overrides the `media` from the post"""
