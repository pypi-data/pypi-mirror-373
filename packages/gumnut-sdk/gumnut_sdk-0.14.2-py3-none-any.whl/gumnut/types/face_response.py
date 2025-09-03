# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional
from datetime import datetime

from .._models import BaseModel

__all__ = ["FaceResponse"]


class FaceResponse(BaseModel):
    id: str
    """Unique face identifier with 'face\\__' prefix"""

    asset_id: str
    """ID of the asset containing this face"""

    bounding_box: Dict[str, int]
    """Face location as {x, y, w, h} coordinates in pixels"""

    created_at: datetime
    """When this face was detected and recorded"""

    updated_at: datetime
    """When this face record was last updated"""

    person_id: Optional[str] = None
    """ID of the person this face belongs to (if identified)"""

    thumbnail_url: Optional[str] = None
    """URL to get a cropped thumbnail of just this face"""

    timestamp_ms: Optional[int] = None
    """For video files, timestamp in milliseconds when face appears"""
