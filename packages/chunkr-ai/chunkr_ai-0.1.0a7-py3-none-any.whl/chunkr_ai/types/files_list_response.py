# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime

from .file import File
from .._models import BaseModel

__all__ = ["FilesListResponse"]


class FilesListResponse(BaseModel):
    files: List[File]
    """List of files"""

    has_more: bool
    """Whether there are more files to fetch"""

    next_cursor: Optional[datetime] = None
    """Cursor for pagination (timestamp) e.g. 2025-01-01T00:00:00Z"""
