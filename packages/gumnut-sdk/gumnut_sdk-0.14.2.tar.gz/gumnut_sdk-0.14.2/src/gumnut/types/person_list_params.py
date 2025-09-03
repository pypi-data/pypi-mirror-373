# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import TypedDict

__all__ = ["PersonListParams"]


class PersonListParams(TypedDict, total=False):
    album_id: Optional[str]
    """Include only people associated with this album ID"""

    asset_id: Optional[str]
    """Include only people associated with this asset ID"""

    library_id: Optional[str]
    """Library ID (required if user has multiple libraries)"""

    limit: int

    starting_after_id: Optional[str]
    """Person ID to start listing people after"""
