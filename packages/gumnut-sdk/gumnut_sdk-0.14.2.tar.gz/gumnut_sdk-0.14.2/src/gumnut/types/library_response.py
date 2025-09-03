# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from .._models import BaseModel

__all__ = ["LibraryResponse"]


class LibraryResponse(BaseModel):
    id: str
    """Unique library identifier with 'lib\\__' prefix"""

    created_at: datetime
    """When this library was created"""

    name: str
    """Display name of the library"""

    updated_at: datetime
    """When this library was last updated"""

    user_id: str
    """ID of the user who owns this library"""

    description: Optional[str] = None
    """Optional description text for the library"""
