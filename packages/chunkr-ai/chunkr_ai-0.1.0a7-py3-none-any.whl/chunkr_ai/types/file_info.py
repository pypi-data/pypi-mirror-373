# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["FileInfo"]


class FileInfo(BaseModel):
    url: str
    """The presigned URL/Base64 encoded URL of the input file."""

    mime_type: Optional[str] = None
    """The MIME type of the file."""

    name: Optional[str] = None
    """The name of the file."""

    page_count: Optional[int] = None
    """The number of pages in the file."""
