# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from ..._models import BaseModel

__all__ = ["AssetAddResponse"]


class AssetAddResponse(BaseModel):
    added_assets: List[str]

    duplicate_assets: List[str]
