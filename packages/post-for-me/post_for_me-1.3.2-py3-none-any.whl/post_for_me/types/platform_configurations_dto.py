# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel
from .tiktok_configuration import TiktokConfiguration
from .bluesky_configuration_dto import BlueskyConfigurationDto
from .threads_configuration_dto import ThreadsConfigurationDto
from .twitter_configuration_dto import TwitterConfigurationDto
from .youtube_configuration_dto import YoutubeConfigurationDto
from .facebook_configuration_dto import FacebookConfigurationDto
from .linkedin_configuration_dto import LinkedinConfigurationDto
from .instagram_configuration_dto import InstagramConfigurationDto
from .pinterest_configuration_dto import PinterestConfigurationDto

__all__ = ["PlatformConfigurationsDto"]


class PlatformConfigurationsDto(BaseModel):
    bluesky: Optional[BlueskyConfigurationDto] = None
    """Bluesky configuration"""

    facebook: Optional[FacebookConfigurationDto] = None
    """Facebook configuration"""

    instagram: Optional[InstagramConfigurationDto] = None
    """Instagram configuration"""

    linkedin: Optional[LinkedinConfigurationDto] = None
    """LinkedIn configuration"""

    pinterest: Optional[PinterestConfigurationDto] = None
    """Pinterest configuration"""

    threads: Optional[ThreadsConfigurationDto] = None
    """Threads configuration"""

    tiktok: Optional[TiktokConfiguration] = None
    """TikTok configuration"""

    tiktok_business: Optional[TiktokConfiguration] = None
    """TikTok configuration"""

    x: Optional[TwitterConfigurationDto] = None
    """Twitter configuration"""

    youtube: Optional[YoutubeConfigurationDto] = None
    """YouTube configuration"""
