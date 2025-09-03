# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Optional
from typing_extensions import Literal, TypedDict

__all__ = ["InstagramConfigurationDtoParam"]


class InstagramConfigurationDtoParam(TypedDict, total=False):
    caption: Optional[object]
    """Overrides the `caption` from the post"""

    collaborators: Optional[List[str]]
    """Instagram usernames to be tagged as a collaborator"""

    media: Optional[List[str]]
    """Overrides the `media` from the post"""

    placement: Optional[Literal["reels", "stories", "timeline"]]
    """Instagram post placement"""
