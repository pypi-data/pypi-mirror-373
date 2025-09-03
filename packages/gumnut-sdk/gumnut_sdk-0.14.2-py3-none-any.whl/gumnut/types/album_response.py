# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from .._models import BaseModel

__all__ = ["AlbumResponse"]


class AlbumResponse(BaseModel):
    id: str
    """Unique album identifier with 'album\\__' prefix"""

    created_at: datetime
    """When this album was created"""

    name: str
    """Display name of the album"""

    updated_at: datetime
    """When this album was last updated"""

    description: Optional[str] = None
    """Optional description text for the album"""
