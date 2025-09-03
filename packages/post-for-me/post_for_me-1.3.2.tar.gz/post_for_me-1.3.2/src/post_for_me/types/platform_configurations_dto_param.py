# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import TypedDict

from .tiktok_configuration_param import TiktokConfigurationParam
from .bluesky_configuration_dto_param import BlueskyConfigurationDtoParam
from .threads_configuration_dto_param import ThreadsConfigurationDtoParam
from .twitter_configuration_dto_param import TwitterConfigurationDtoParam
from .youtube_configuration_dto_param import YoutubeConfigurationDtoParam
from .facebook_configuration_dto_param import FacebookConfigurationDtoParam
from .linkedin_configuration_dto_param import LinkedinConfigurationDtoParam
from .instagram_configuration_dto_param import InstagramConfigurationDtoParam
from .pinterest_configuration_dto_param import PinterestConfigurationDtoParam

__all__ = ["PlatformConfigurationsDtoParam"]


class PlatformConfigurationsDtoParam(TypedDict, total=False):
    bluesky: Optional[BlueskyConfigurationDtoParam]
    """Bluesky configuration"""

    facebook: Optional[FacebookConfigurationDtoParam]
    """Facebook configuration"""

    instagram: Optional[InstagramConfigurationDtoParam]
    """Instagram configuration"""

    linkedin: Optional[LinkedinConfigurationDtoParam]
    """LinkedIn configuration"""

    pinterest: Optional[PinterestConfigurationDtoParam]
    """Pinterest configuration"""

    threads: Optional[ThreadsConfigurationDtoParam]
    """Threads configuration"""

    tiktok: Optional[TiktokConfigurationParam]
    """TikTok configuration"""

    tiktok_business: Optional[TiktokConfigurationParam]
    """TikTok configuration"""

    x: Optional[TwitterConfigurationDtoParam]
    """Twitter configuration"""

    youtube: Optional[YoutubeConfigurationDtoParam]
    """YouTube configuration"""
