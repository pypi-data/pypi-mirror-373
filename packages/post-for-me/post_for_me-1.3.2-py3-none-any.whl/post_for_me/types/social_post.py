# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from .._models import BaseModel
from .social_account import SocialAccount
from .platform_configurations_dto import PlatformConfigurationsDto

__all__ = ["SocialPost", "AccountConfiguration", "AccountConfigurationConfiguration", "Media"]


class AccountConfigurationConfiguration(BaseModel):
    allow_comment: Optional[bool] = None
    """Allow comments on TikTok"""

    allow_duet: Optional[bool] = None
    """Allow duets on TikTok"""

    allow_stitch: Optional[bool] = None
    """Allow stitch on TikTok"""

    board_ids: Optional[List[str]] = None
    """Pinterest board IDs"""

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

    link: Optional[str] = None
    """Pinterest post link"""

    media: Optional[List[str]] = None
    """Overrides the `media` from the post"""

    placement: Optional[Literal["reels", "timeline", "stories"]] = None
    """Post placement for Facebook/Instagram/Threads"""

    privacy_status: Optional[str] = None
    """Sets the privacy status for TikTok (private, public)"""

    title: Optional[str] = None
    """Overrides the `title` from the post"""


class AccountConfiguration(BaseModel):
    configuration: AccountConfigurationConfiguration
    """Configuration for the social account"""

    social_account_id: str
    """ID of the social account, you want to apply the configuration to"""


class Media(BaseModel):
    url: str
    """Public URL of the media"""

    thumbnail_timestamp_ms: Optional[object] = None
    """Timestamp in milliseconds of frame to use as thumbnail for the media"""

    thumbnail_url: Optional[object] = None
    """Public URL of the thumbnail for the media"""


class SocialPost(BaseModel):
    id: str
    """Unique identifier of the post"""

    account_configurations: Optional[List[AccountConfiguration]] = None
    """Account-specific configurations for the post"""

    caption: str
    """Caption text for the post"""

    created_at: str
    """Timestamp when the post was created"""

    external_id: Optional[str] = None
    """Provided unique identifier of the post"""

    media: Optional[List[Media]] = None
    """Array of media URLs associated with the post"""

    platform_configurations: Optional[PlatformConfigurationsDto] = None
    """Platform-specific configurations for the post"""

    scheduled_at: Optional[str] = None
    """Scheduled date and time for the post"""

    social_accounts: List[SocialAccount]
    """Array of social account IDs for posting"""

    status: Literal["draft", "scheduled", "processing", "processed"]
    """Current status of the post: draft, processed, scheduled, or processing"""

    updated_at: str
    """Timestamp when the post was last updated"""
