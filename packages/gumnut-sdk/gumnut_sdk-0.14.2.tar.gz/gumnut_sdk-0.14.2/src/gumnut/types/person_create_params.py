# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Optional
from datetime import date
from typing_extensions import Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["PersonCreateParams"]


class PersonCreateParams(TypedDict, total=False):
    birth_date: Annotated[Union[str, date, None], PropertyInfo(format="iso8601")]

    is_favorite: Optional[bool]

    is_hidden: Optional[bool]

    library_id: Optional[str]

    name: Optional[str]

    thumbnail_face_id: Optional[str]
