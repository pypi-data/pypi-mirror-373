# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import date, datetime

from .._models import BaseModel

__all__ = ["PersonResponse"]


class PersonResponse(BaseModel):
    id: str
    """Unique person identifier with 'person\\__' prefix"""

    created_at: datetime
    """When this person record was created"""

    is_favorite: bool
    """Whether this person is marked as a favorite"""

    is_hidden: bool
    """Whether this person should be hidden from the UI"""

    updated_at: datetime
    """When this person record was last updated"""

    birth_date: Optional[date] = None
    """Optional birth date of this person"""

    name: Optional[str] = None
    """Optional name assigned to this person"""

    thumbnail_face_id: Optional[str] = None
    """ID of the face resource used as this person's thumbnail"""

    thumbnail_face_url: Optional[str] = None
    """URL for this person's profile thumbnail image"""
