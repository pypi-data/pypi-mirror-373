# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Optional
from datetime import datetime
from typing_extensions import Required, Annotated, TypedDict

from .._types import FileTypes
from .._utils import PropertyInfo

__all__ = ["AssetCreateParams"]


class AssetCreateParams(TypedDict, total=False):
    asset_data: Required[FileTypes]

    device_asset_id: Required[str]

    device_id: Required[str]

    file_created_at: Required[Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]]

    file_modified_at: Required[Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]]

    library_id: Optional[str]
    """Library to upload asset to (optional)"""
