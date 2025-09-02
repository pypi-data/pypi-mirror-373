# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .page import Page
from .chunk import Chunk
from .._models import BaseModel

__all__ = ["ParseOutputResponse"]


class ParseOutputResponse(BaseModel):
    chunks: List[Chunk]
    """Collection of document chunks, where each chunk contains one or more segments"""

    file_name: Optional[str] = None
    """The name of the file. Deprecated use `file_info.name` instead."""

    mime_type: Optional[str] = None
    """The MIME type of the file. Deprecated use `file_info.mime_type` instead."""

    page_count: Optional[int] = None
    """The number of pages in the file. Deprecated use `file_info.page_count` instead."""

    pages: Optional[List[Page]] = None
    """The pages of the file. Includes the image and metadata for each page."""

    pdf_url: Optional[str] = None
    """The presigned URL of the PDF file."""
