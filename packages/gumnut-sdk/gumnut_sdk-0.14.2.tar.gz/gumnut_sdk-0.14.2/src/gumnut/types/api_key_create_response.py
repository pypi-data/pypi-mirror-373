# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from .._models import BaseModel

__all__ = ["APIKeyCreateResponse"]


class APIKeyCreateResponse(BaseModel):
    id: str
    """Unique API key identifier with 'apikey\\__' prefix"""

    api_key: str
    """The actual API key value - store this securely as it cannot be retrieved later"""

    created_at: datetime
    """When this API key was created"""

    is_active: bool
    """Whether this API key is currently valid and can be used"""

    last_used_at: Optional[datetime] = None
    """When this API key was last used for authentication"""

    name: Optional[str] = None
    """Optional descriptive name for this API key"""
