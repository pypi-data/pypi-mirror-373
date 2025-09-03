# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import TypedDict

__all__ = ["AssetDownloadThumbnailParams"]


class AssetDownloadThumbnailParams(TypedDict, total=False):
    size: Optional[str]
    """Desired thumbnail size (e.g., thumbnail, preview)"""
