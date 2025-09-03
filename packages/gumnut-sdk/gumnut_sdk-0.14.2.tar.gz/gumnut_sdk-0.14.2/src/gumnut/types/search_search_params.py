# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union, Optional
from datetime import datetime
from typing_extensions import Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["SearchSearchParams"]


class SearchSearchParams(TypedDict, total=False):
    captured_after: Annotated[Union[str, datetime, None], PropertyInfo(format="iso8601")]
    """Filter to only include assets captured after this date (ISO format)."""

    captured_before: Annotated[Union[str, datetime, None], PropertyInfo(format="iso8601")]
    """Filter to only include assets captured before this date (ISO format)."""

    library_id: Optional[str]
    """Library to search assets from (optional)"""

    limit: int
    """Number of results per page"""

    page: int
    """Page number"""

    person_ids: List[str]
    """Filter to only include assets containing ALL of these person IDs.

    Can be comma-delimited string (e.g. 'person_123,person_abc') or multiple query
    parameters.
    """

    query: Optional[str]
    """The text query to search for.

    If you want to search for a specific person or set of people, use the person_ids
    parameter instead.If you want to search for a photos taken during a specific
    date range, use the captured_before and captured_after parameters instead.
    """

    threshold: float
    """Similarity threshold (lower means more similar)"""
