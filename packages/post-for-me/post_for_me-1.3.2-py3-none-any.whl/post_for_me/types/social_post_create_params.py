# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union, Iterable, Optional
from datetime import datetime
from typing_extensions import Literal, Required, Annotated, TypedDict

from .._utils import PropertyInfo
from .platform_configurations_dto_param import PlatformConfigurationsDtoParam

__all__ = ["SocialPostCreateParams", "AccountConfiguration", "AccountConfigurationConfiguration", "Media"]


class SocialPostCreateParams(TypedDict, total=False):
    caption: Required[str]
    """Caption text for the post"""

    social_accounts: Required[List[str]]
    """Array of social account IDs for posting"""

    account_configurations: Optional[Iterable[AccountConfiguration]]
    """Account-specific configurations for the post"""

    external_id: Optional[str]
    """Array of social account IDs for posting"""

    is_draft: Annotated[Optional[bool], PropertyInfo(alias="isDraft")]
    """If isDraft is set then the post will not be processed"""

    media: Optional[Iterable[Media]]
    """Array of media URLs associated with the post"""

    platform_configurations: Optional[PlatformConfigurationsDtoParam]
    """Platform-specific configurations for the post"""

    scheduled_at: Annotated[Union[str, datetime, None], PropertyInfo(format="iso8601")]
    """
    Scheduled date and time for the post, setting to null or undefined will post
    instantly
    """


class AccountConfigurationConfiguration(TypedDict, total=False):
    allow_comment: Optional[bool]
    """Allow comments on TikTok"""

    allow_duet: Optional[bool]
    """Allow duets on TikTok"""

    allow_stitch: Optional[bool]
    """Allow stitch on TikTok"""

    board_ids: Optional[List[str]]
    """Pinterest board IDs"""

    caption: Optional[object]
    """Overrides the `caption` from the post"""

    disclose_branded_content: Optional[bool]
    """Disclose branded content on TikTok"""

    disclose_your_brand: Optional[bool]
    """Disclose your brand on TikTok"""

    is_ai_generated: Optional[bool]
    """Flag content as AI generated on TikTok"""

    is_draft: Optional[bool]
    """
    Will create a draft upload to TikTok, posting will need to be completed from
    within the app
    """

    link: Optional[str]
    """Pinterest post link"""

    media: Optional[List[str]]
    """Overrides the `media` from the post"""

    placement: Optional[Literal["reels", "timeline", "stories"]]
    """Post placement for Facebook/Instagram/Threads"""

    privacy_status: Optional[str]
    """Sets the privacy status for TikTok (private, public)"""

    title: Optional[str]
    """Overrides the `title` from the post"""


class AccountConfiguration(TypedDict, total=False):
    configuration: Required[AccountConfigurationConfiguration]
    """Configuration for the social account"""

    social_account_id: Required[str]
    """ID of the social account, you want to apply the configuration to"""


class Media(TypedDict, total=False):
    url: Required[str]
    """Public URL of the media"""

    thumbnail_timestamp_ms: Optional[object]
    """Timestamp in milliseconds of frame to use as thumbnail for the media"""

    thumbnail_url: Optional[object]
    """Public URL of the thumbnail for the media"""
