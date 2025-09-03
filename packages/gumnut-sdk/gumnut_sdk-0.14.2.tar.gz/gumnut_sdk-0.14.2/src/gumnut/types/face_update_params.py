# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import TypedDict

__all__ = ["FaceUpdateParams"]


class FaceUpdateParams(TypedDict, total=False):
    library_id: Optional[str]
    """Library ID (required if user has multiple libraries)"""

    person_id: Optional[str]
