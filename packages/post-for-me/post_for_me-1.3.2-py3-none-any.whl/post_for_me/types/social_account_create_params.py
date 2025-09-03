# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Optional
from datetime import datetime
from typing_extensions import Literal, Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["SocialAccountCreateParams"]


class SocialAccountCreateParams(TypedDict, total=False):
    access_token: Required[str]
    """The access token of the social account"""

    access_token_expires_at: Required[Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]]
    """The access token expiration date of the social account"""

    platform: Required[
        Literal[
            "facebook",
            "instagram",
            "x",
            "tiktok",
            "youtube",
            "pinterest",
            "linkedin",
            "bluesky",
            "threads",
            "tiktok_business",
        ]
    ]
    """The platform of the social account"""

    user_id: Required[str]
    """The user id of the social account"""

    external_id: Optional[str]
    """The external id of the social account"""

    metadata: object
    """The metadata of the social account"""

    refresh_token: Optional[str]
    """The refresh token of the social account"""

    refresh_token_expires_at: Annotated[Union[str, datetime, None], PropertyInfo(format="iso8601")]
    """The refresh token expiration date of the social account"""

    username: Optional[str]
    """The platform's username of the social account"""
