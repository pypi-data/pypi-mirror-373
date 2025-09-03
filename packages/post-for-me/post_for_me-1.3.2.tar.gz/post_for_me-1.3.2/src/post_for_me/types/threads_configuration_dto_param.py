# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Optional
from typing_extensions import Literal, TypedDict

__all__ = ["ThreadsConfigurationDtoParam"]


class ThreadsConfigurationDtoParam(TypedDict, total=False):
    caption: Optional[object]
    """Overrides the `caption` from the post"""

    media: Optional[List[str]]
    """Overrides the `media` from the post"""

    placement: Optional[Literal["reels", "timeline"]]
    """Threads post placement"""
