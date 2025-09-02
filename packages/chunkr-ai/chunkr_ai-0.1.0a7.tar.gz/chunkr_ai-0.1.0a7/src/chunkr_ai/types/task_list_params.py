# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union
from datetime import datetime
from typing_extensions import Literal, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["TaskListParams"]


class TaskListParams(TypedDict, total=False):
    base64_urls: bool
    """Whether to return base64 encoded URLs.

    If false, the URLs will be returned as presigned URLs.
    """

    cursor: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]
    """Cursor for pagination (timestamp)"""

    end: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]
    """End date"""

    include_chunks: bool
    """Whether to include chunks in the output response"""

    limit: int
    """Number of tasks per page"""

    sort: Literal["asc", "desc"]
    """Sort order: 'asc' for ascending, 'desc' for descending (default)"""

    start: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]
    """Start date"""

    statuses: List[Literal["Starting", "Processing", "Succeeded", "Failed", "Cancelled"]]
    """Filter by one or more statuses"""

    task_types: List[Literal["Parse", "Extract"]]
    """Filter by one or more task types"""
