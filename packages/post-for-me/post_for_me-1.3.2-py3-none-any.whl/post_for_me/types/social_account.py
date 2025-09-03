# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["SocialAccount"]


class SocialAccount(BaseModel):
    id: str
    """The unique identifier of the social account"""

    access_token: str
    """The access token of the social account"""

    access_token_expires_at: datetime
    """The access token expiration date of the social account"""

    external_id: Optional[str] = None
    """The external id of the social account"""

    metadata: Optional[object] = None
    """The metadata of the social account"""

    platform: str
    """The platform of the social account"""

    refresh_token: Optional[str] = None
    """The refresh token of the social account"""

    refresh_token_expires_at: Optional[datetime] = None
    """The refresh token expiration date of the social account"""

    status: Literal["connected", "disconnected"]
    """Status of the account"""

    user_id: str
    """The platform's id of the social account"""

    username: Optional[str] = None
    """The platform's username of the social account"""
