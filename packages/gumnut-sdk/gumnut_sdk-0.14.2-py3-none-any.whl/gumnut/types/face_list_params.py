# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import TypedDict

__all__ = ["FaceListParams"]


class FaceListParams(TypedDict, total=False):
    asset_id: Optional[str]
    """Filter by faces in a specific asset"""

    library_id: Optional[str]
    """Library ID (required if user has multiple libraries)"""

    limit: int

    person_id: Optional[str]
    """Filter by faces associated with a specific person"""

    starting_after_id: Optional[str]
    """Face ID to start listing faces after"""
