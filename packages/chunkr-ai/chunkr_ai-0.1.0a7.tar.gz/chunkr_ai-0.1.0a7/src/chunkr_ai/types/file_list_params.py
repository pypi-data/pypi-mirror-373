# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from datetime import datetime
from typing_extensions import Literal, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["FileListParams"]


class FileListParams(TypedDict, total=False):
    cursor: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]
    """Cursor for pagination (created_at)"""

    end: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]
    """End date"""

    limit: int
    """Number of files per page"""

    sort: Literal["asc", "desc"]
    """Sort order: 'asc' for ascending, 'desc' for descending (default)"""

    start: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]
    """Start date"""
