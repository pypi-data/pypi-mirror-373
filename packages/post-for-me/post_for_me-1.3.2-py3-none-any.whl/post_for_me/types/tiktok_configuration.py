# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel

__all__ = ["TiktokConfiguration"]


class TiktokConfiguration(BaseModel):
    allow_comment: Optional[bool] = None
    """Allow comments on TikTok"""

    allow_duet: Optional[bool] = None
    """Allow duets on TikTok"""

    allow_stitch: Optional[bool] = None
    """Allow stitch on TikTok"""

    caption: Optional[object] = None
    """Overrides the `caption` from the post"""

    disclose_branded_content: Optional[bool] = None
    """Disclose branded content on TikTok"""

    disclose_your_brand: Optional[bool] = None
    """Disclose your brand on TikTok"""

    is_ai_generated: Optional[bool] = None
    """Flag content as AI generated on TikTok"""

    is_draft: Optional[bool] = None
    """
    Will create a draft upload to TikTok, posting will need to be completed from
    within the app
    """

    media: Optional[List[str]] = None
    """Overrides the `media` from the post"""

    privacy_status: Optional[str] = None
    """Sets the privacy status for TikTok (private, public)"""

    title: Optional[str] = None
    """Overrides the `title` from the post"""
